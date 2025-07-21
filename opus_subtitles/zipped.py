import logging
import multiprocessing as mp
from io import BytesIO
from itertools import groupby
from pathlib import Path
from typing import Generator
from zipfile import ZipFile

from lxml import etree
from tqdm import tqdm

from .languages import get_language_code, standardize_tag
from .utils import (
    deduplicate_consecutive,
    is_cased,
    iter_batch,
    strip_whitespaces,
)

logger = logging.getLogger(__name__)


class SubtitleXML:
    """Class to handle OPUS OpenSubtitles XML files."""

    _parser = etree.XMLParser(recover=True, remove_blank_text=True)

    def __init__(self, xml_bytes: bytes) -> None:
        try:
            self._tree = etree.parse(BytesIO(xml_bytes), self._parser)
        except etree.XMLSyntaxError:
            self._tree = etree.XML("<document></document>", self._parser)

    def get_lines(self, dedup: bool = False) -> list[str]:
        """Get subtitle lines from the XML file."""
        try:
            lines = self._tree.xpath(".//s/text()")
        except (IndexError, AttributeError):
            return []
        else:
            lines = strip_whitespaces(lines)
            if dedup:
                lines = deduplicate_consecutive(lines)
            return lines

    @property
    def language(self) -> str | None:
        """Get the language of the subtitles."""
        try:
            language = self._tree.xpath(".//meta/subtitle/language/text()")[0]
        except (IndexError, AttributeError):
            return
        else:
            return language

    @property
    def original(self) -> str:
        """Get the name of the original language of the subtitles."""
        try:
            original = self._tree.xpath(".//meta/source/original/text()")[0]
        except (IndexError, AttributeError):
            return ""
        else:
            return original.split(",")[0].strip()

    @property
    def confidence(self) -> float | None:
        """Get the confidence score of the subtitles."""
        try:
            confidence = self._tree.xpath(
                ".//meta/subtitle/confidence/text()"
            )[0]
        except (IndexError, AttributeError):
            return
        else:
            return float(confidence)

    @property
    def machine_translated(self) -> bool | None:
        """Check if the subtitles are machine translated."""
        try:
            machine_translated = self._tree.xpath(
                ".//meta/subtitle/machine_translated/text()"
            )[0]
        except (IndexError, AttributeError):
            return
        else:
            return bool(int(machine_translated))

    @property
    def language_code(self) -> str:
        """Get the language code of the original language of the subtitles.
        Macrolanguages are favoured over individual languages.
        """
        return get_language_code(self.original, macro=True)


class ZippedSubtitles:
    """Class to handle OPUS OpenSubtitles XML files in a ZIP archive."""

    def __init__(self, file_path: Path) -> None:
        self._fp = file_path

    def list_xml_files(self, distinct_title: bool = False) -> list[str]:
        """List XML files in the ZIP archive. If `distinct_title` is True,
        only the first XML file for each IMDb ID is returned."""
        with ZipFile(self.path) as zf:
            xml_paths = filter(lambda x: x.endswith(".xml"), zf.namelist())
            if distinct_title:

                def get_imdb_id(xml_path):
                    return xml_path.split("/")[-2]

                xml_paths = (
                    next(group)
                    for imdb_id, group in groupby(xml_paths, key=get_imdb_id)
                )
        return sorted(list(xml_paths))

    def count_xml_files(self, distinct_title: bool = False) -> int:
        """Count the number of XML files in the ZIP archive. If
        `distinct_title` is True, only one XML file for each IMDb ID
        is counted.
        """
        return len(self.list_xml_files(distinct_title=distinct_title))

    def iter_xml_files(
        self,
        distinct_title: bool = False,
        original_only: bool = False,
        cased_only: bool = False,
        deduplicate: bool = False,
        batch_size: int = 1000,
        nb_workers: int | None = None,
    ) -> Generator[tuple[str, str, list[str]], None, None]:
        """Iterate over XML files in the ZIP archive and yield IMDb ID,
        document ID, and subtitle lines.
        """
        origin_lang = self.language_code if original_only else None

        global parse_batch

        def parse_batch(batch) -> list[tuple[str, str, list[str]]]:
            result = []
            for imdb_id, doc_id, xml_bytes in batch:
                subtitle_xml = SubtitleXML(xml_bytes)
                # original language filtering
                if origin_lang and subtitle_xml.language_code != origin_lang:
                    continue
                # cased subtitle filtering
                lines = subtitle_xml.get_lines(dedup=deduplicate)
                if cased_only and not is_cased(" ".join(lines)):
                    continue
                result.append((imdb_id, doc_id, lines))
            return result

        nb_xml_files = self.count_xml_files(distinct_title=distinct_title)
        nb_batches = nb_xml_files // batch_size + 1
        if nb_workers is None or nb_workers < 1:
            nb_workers = mp.cpu_count()  # default to number of CPU cores
        logger.info(
            f"processing {nb_xml_files} XML files in {nb_batches} batches "
            f"with {nb_workers} workers, {batch_size} files per batch:"
        )
        with tqdm(total=nb_batches, unit="batch") as pbar:
            with mp.Pool(processes=nb_workers) as pool:
                batches = self._iter_batch_xml_files(
                    distinct_title=distinct_title, batch_size=batch_size
                )
                for result_batch in pool.imap_unordered(parse_batch, batches):
                    for imdb_id, doc_id, lines in result_batch:
                        yield (imdb_id, doc_id, lines)
                    pbar.update(1)

    def _iter_batch_xml_files(
        self, distinct_title: bool = False, batch_size: int = 1000
    ) -> Generator[list[tuple[str, str, bytes]], None, None]:
        """Iterate over XML files in the ZIP archive in batches."""
        xml_files = self.list_xml_files(distinct_title=distinct_title)
        with ZipFile(self._fp) as zf:

            def get_subtitle(xml_file: str) -> tuple[str, str, bytes]:
                imdb_id, doc_id = xml_file[:-4].split("/")[-2:]
                # parsing from bytes is faster than from a file handle,
                # especially in multiprocessing.
                xml_bytes = zf.read(xml_file)
                return (imdb_id, doc_id, xml_bytes)

            for batch in iter_batch(xml_files, batch_size=batch_size):
                yield list(map(get_subtitle, batch))

    @property
    def language_code(self) -> str:
        """Get the language code of the ZIP archive. Macrolanguages are
        favoured over individual languages.
        """
        macro_language_tag = standardize_tag(self._fp.stem, macro=True)
        macro_language_code = macro_language_tag.split("-")[0]

        return macro_language_code

    @property
    def path(self) -> Path:
        """Get the file path of the ZIP archive."""
        return self._fp

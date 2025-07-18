import logging
from pathlib import Path
from typing import IO, Generator
from zipfile import ZipFile

from lxml import etree
from tqdm import tqdm

from .languages import get_language_code, standardize_tag
from .utils import deduplicate_consecutive, strip_whitespaces

logger = logging.getLogger(__name__)


class SubtitleXML:
    """Class to parse and extract information from OPUS OpenSubtitles XML
    files.
    """

    _parser = etree.XMLParser(recover=True, remove_blank_text=True)

    def __init__(self, xml_file: IO[bytes]) -> None:
        self._f = xml_file
        self._tree = etree.parse(self._f, SubtitleXML._parser)

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

    def count_xml_files(self) -> int:
        """Count the number of XML files in the ZIP archive."""
        cnt_xml_files = 0
        with ZipFile(self.path) as zf:
            for p in zf.namelist():
                if p.endswith(".xml"):
                    cnt_xml_files += 1

        return cnt_xml_files

    def list_xml_files(self) -> list[str]:
        """List all XML files in the ZIP archive."""
        with ZipFile(self.path) as zf:
            xml_paths = filter(lambda x: x.endswith(".xml"), zf.namelist())

        return sorted(list(xml_paths))

    def iter_xml_files(
        self,
    ) -> Generator[tuple[str, str, SubtitleXML], None, None]:
        """Iterate over XML files in the ZIP archive."""
        xml_files = self.list_xml_files()
        with tqdm(total=len(xml_files)) as pbar, ZipFile(self.path) as zf:
            for xml_file in xml_files:
                imdb_id, doc_id = xml_file[:-4].split("/")[-2:]
                with zf.open(xml_file) as f:
                    try:
                        xml_file = SubtitleXML(f)
                    except etree.XMLSyntaxError:
                        msg = f"parsing of {xml_file} failed"
                        logger.warning(msg)
                    else:
                        yield imdb_id, doc_id, xml_file
                pbar.update()

    @property
    def language_code(self) -> str:
        """Get the language code of the ZIP archive. Macrolanguages are
        favoured over individual languages."""
        macro_language_tag = standardize_tag(self._fp.stem, macro=True)
        macro_language_code = macro_language_tag.split("-")[0]

        return macro_language_code

    @property
    def path(self) -> Path:
        """Get the file path of the ZIP archive."""
        return self._fp

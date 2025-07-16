import logging
from pathlib import Path
from typing import IO, Generator
from zipfile import ZipFile

from lxml import etree
from tqdm import tqdm

from .languages import LangTag
from .utils import are_cased, deduplicate_consecutive, strip_whitespaces

logger = logging.getLogger(__name__)


class SubtitleXML:
    _parser = etree.XMLParser(recover=True, remove_blank_text=True)

    def __init__(self, xml_file: IO[bytes]) -> None:
        self._f = xml_file
        self._tree = etree.parse(self._f, SubtitleXML._parser)

    def get_lines(self, dedup: bool = False) -> list[str]:
        try:
            lines = self._tree.xpath(".//s/text()")
        except (IndexError, AttributeError):
            return []
        else:
            lines = strip_whitespaces(lines)
            if dedup:
                lines = deduplicate_consecutive(lines)
            return lines

    def is_cased(self, threshold: float = 0.9) -> bool:
        lines = self.get_lines(dedup=False)
        return are_cased(lines, threshold=threshold)

    @property
    def language(self) -> str | None:
        try:
            language = self._tree.xpath(".//meta/subtitle/language/text()")[0]
        except (IndexError, AttributeError):
            return
        else:
            return language

    @property
    def original(self) -> str:
        try:
            original = self._tree.xpath(".//meta/source/original/text()")[0]
        except (IndexError, AttributeError):
            return ""
        else:
            return original.split(",")[0].strip()

    @property
    def confidence(self) -> float | None:
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
        try:
            machine_translated = self._tree.xpath(
                ".//meta/subtitle/machine_translated/text()"
            )[0]
        except (IndexError, AttributeError):
            return
        else:
            return bool(int(machine_translated))


class RawSubtitleZip:

    def __init__(self, file_path: Path) -> None:
        self._fp = file_path

    def list_xml_files(
        self,
        min_year: int | None = None,
        max_year: int | None = None,
    ) -> list[str]:
        xml_paths = []
        with ZipFile(self.path) as zf:
            for p in zf.namelist():
                if p.endswith(".xml"):
                    year = p.split("/")[-3]
                    if (min_year or max_year) and year == "unknown":
                        continue
                    if min_year and int(year) < min_year:
                        continue
                    if max_year and int(year) > max_year:
                        continue
                    xml_paths.append(p)
        return sorted(xml_paths)

    def iter_xml_files(
        self,
        xml_files: list[str],
        original_language_only: bool = False,
        one_subtitle_per_movie: bool = False,
        min_cased: float = 0.0,
    ) -> Generator[tuple[int, int, SubtitleXML], None, None]:
        with tqdm(total=len(xml_files)) as pbar, ZipFile(self.path) as zf:
            done_imdb_ids = set()
            for xml_file in xml_files:
                imdb_id, doc_id = map(int, xml_file[:-4].split("/")[-2:])
                if one_subtitle_per_movie and imdb_id in done_imdb_ids:
                    pass
                else:
                    with zf.open(xml_file) as f:
                        try:
                            xml_file = SubtitleXML(f)
                        except etree.XMLSyntaxError:
                            msg = f"parsing of {xml_file} failed"
                            logger.warning(msg)
                        else:
                            if (
                                original_language_only
                                and self.language_tag.language_name
                                != LangTag(xml_file.original).language_name
                            ):
                                pass
                            elif self.language_tag.scripts == [
                                "Latn"
                            ] and not xml_file.is_cased(threshold=min_cased):
                                pass
                            else:
                                yield imdb_id, doc_id, xml_file
                                done_imdb_ids.add(imdb_id)
                pbar.update()

    @property
    def language_tag(self) -> LangTag:
        return LangTag(self._fp.stem)

    @property
    def path(self) -> Path:
        return self._fp

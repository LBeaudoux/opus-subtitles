import logging
from pathlib import Path
from typing import Generator
from urllib.parse import urlparse

from .archive import RawSubtitleZip
from .download import download
from .extraction import SubtitleCorpus, SubtitleTXT

logger = logging.getLogger(__name__)


DOWNLOAD_URL = "https://object.pouta.csc.fi/OPUS-OpenSubtitles/v2024/raw/"


def download_raw_subtitle_zip(
    file_name: str, to_dir: Path, overwrite: bool = True
) -> Path:

    from_url = DOWNLOAD_URL + file_name
    to_path = to_dir.joinpath(file_name)
    if not to_path.exists() or overwrite:
        from_host = urlparse(from_url).hostname
        logger.info(f"Downloading {file_name} from {from_host}")
        download(from_url, to_dir)

    return to_path


def extract_subtitle_txt_files(
    from_zip: Path,
    to_dir: Path,
    min_year: int | None = None,
    max_year: int | None = None,
    original_language_only: bool = False,
    one_subtitle_per_movie: bool = False,
    min_cased: float = 0.0,
    deduplicate: bool = False,
) -> None:

    logger.info(f"extracting '{from_zip}' .txt subtitle files to {to_dir}")
    extracted_subtitle_txt_files = []
    corpus = RawSubtitleZip(from_zip)
    xml_paths = corpus.list_xml_files(min_year=min_year, max_year=max_year)
    for imdb_id, doc_id, xml_file in corpus.iter_xml_files(
        xml_paths,
        original_language_only=original_language_only,
        one_subtitle_per_movie=one_subtitle_per_movie,
        min_cased=min_cased,
    ):
        txt_path = to_dir.joinpath(f"{imdb_id}_{doc_id}.txt")
        xml_lines = xml_file.get_lines(dedup=deduplicate)
        SubtitleTXT(txt_path).write_lines(xml_lines)
        extracted_subtitle_txt_files.append(txt_path)
    nb_extracted = len(extracted_subtitle_txt_files)
    logger.info(f"{nb_extracted} .txt subtitle files extracted")


def read_subtitle_lines(sub_txt_dir: Path) -> Generator[str, None, None]:

    subtitle_corpus = SubtitleCorpus(sub_txt_dir)
    return (
        line
        for sub in subtitle_corpus.txt_files()
        for line in sub.read_lines()
    )

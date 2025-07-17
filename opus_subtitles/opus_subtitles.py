import logging
from pathlib import Path
from typing import Generator
from urllib.parse import urlparse

from .archive import RawSubtitleZip
from .download import download
from .extraction import SubtitleCorpus, SubtitleTXT
from .utils import are_cased

logger = logging.getLogger(__name__)


DOWNLOAD_URL = "https://object.pouta.csc.fi/OPUS-OpenSubtitles/v2024/raw/"


def download_raw_subtitle_zip(
    opus_language_tag: str, to_dir: Path, overwrite: bool = True
) -> Path:

    file_name = opus_language_tag + ".zip"
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
    one_subtitle_per_title: bool = False,
    min_cased: float = 0.0,
    deduplicate: bool = False,
) -> None:
    """Extract XML subtitle files from a ZIP archive and save them as .txt
    files.
    """
    logger.info(
        f"extracting {from_zip.resolve()} XML files as .txt files "
        f"to {to_dir.resolve()}/"
    )
    extracted_doc_ids = []
    extracted_imdb_ids = set()
    raw_zip = RawSubtitleZip(from_zip)
    raw_zip_lang = raw_zip.language_code
    for year, imdb_id, doc_id, xml_file in raw_zip.iter_xml_files():
        # avoid near-duplicate extractions
        if one_subtitle_per_title and imdb_id in extracted_imdb_ids:
            continue
        # year filtering
        if (min_year or max_year) and year == "unknown":
            continue
        if min_year and int(year) < min_year:
            continue
        if max_year and int(year) > max_year:
            continue
        # original language filtering
        if original_language_only:
            if xml_file.language_code != raw_zip_lang:
                continue
        # conditional extraction
        xml_lines = xml_file.get_lines(dedup=deduplicate)
        if are_cased(xml_lines, threshold=min_cased):
            txt_path = to_dir.joinpath(f"{imdb_id}-{doc_id}.txt")
            SubtitleTXT(txt_path).write_lines(xml_lines)
            extracted_doc_ids.append(doc_id)
            extracted_imdb_ids.add(imdb_id)
    nb_extracted = len(extracted_doc_ids)
    logger.info(f"{nb_extracted} subtitle files extracted as .txt")


def read_subtitle_lines(sub_txt_dir: Path) -> Generator[str, None, None]:

    subtitle_corpus = SubtitleCorpus(sub_txt_dir)
    return (
        line
        for sub in subtitle_corpus.txt_files()
        for line in sub.read_lines()
    )

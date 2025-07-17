import logging
from pathlib import Path
from typing import Generator
from urllib.parse import urlparse

import requests

from .archive import RawSubtitleZip
from .download import download
from .extraction import SubtitleCorpus, SubtitleTXT
from .utils import are_cased

logger = logging.getLogger(__name__)


API_URL = "https://opus.nlpl.eu/opusapi/"
DOWNLOAD_URL = "https://object.pouta.csc.fi/OPUS-OpenSubtitles/v2024/raw/"


def list_opus_language_tags() -> list[str]:
    """Fetch the list of available OPUS language tags from the OPUS API.

    Returns
    -------
    list[str]
        A list of available OPUS language tags.
    """
    logger.info("Fetching available OPUS language tags...")
    response = requests.get(
        API_URL, params={"languages": True, "corpus": "OpenSubtitles"}
    )
    if response.status_code == 200:
        data = response.json()
        available_languages = data.get("languages", [])
        return available_languages
    else:
        logger.error(
            f"Failed to fetch available languages: {response.status_code}"
        )
        return []


def download_raw_subtitle_zip(
    opus_language_tag: str, to_dir: Path, overwrite: bool = True
) -> Path:
    """Download a raw subtitle ZIP archive.

    Parameters
    ----------
    opus_language_tag : str
        The OPUS language tag for the subtitles.
    to_dir : Path
        The directory to save the downloaded ZIP file.
    overwrite : bool, optional
        Whether to overwrite the existing ZIP file, by default True

    Returns
    -------
    Path
        The path to the downloaded ZIP file.
    """
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
    """Extract XML subtitle files from a raw ZIP archive and save them as .txt
    files.

    Parameters
    ----------
    from_zip : Path
        The path to the input ZIP file.
    to_dir : Path
        The directory to save the extracted .txt files.
    min_year : int | None, optional
        The minimum year for filtering subtitles, by default None
    max_year : int | None, optional
        The maximum year for filtering subtitles, by default None
    original_language_only : bool, optional
        Whether to extract only subtitles in the original language, by default
        False
    one_subtitle_per_title : bool, optional
        Whether to extract only one subtitle per title, by default False
    min_cased : float, optional
        The minimum proportion of cased subtitle lines, by default 0.0
    deduplicate : bool, optional
        Whether to deduplicate consecutive subtitles, by default False
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
    """Read subtitle lines from .txt files in a directory.

    Parameters
    ----------
    sub_txt_dir : Path
        The directory containing the .txt subtitle files.

    Returns
    -------
    Generator[str, None, None]
        A generator yielding the lines of all subtitle files.
    """
    subtitle_corpus = SubtitleCorpus(sub_txt_dir)
    return (
        line
        for sub in subtitle_corpus.txt_files()
        for line in sub.read_lines()
    )

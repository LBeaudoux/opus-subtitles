import logging
from pathlib import Path
from typing import Generator

import requests

from .download import download
from .unzipped import SubtitleTXT, UnzippedSubtitles
from .zipped import ZippedSubtitles

logger = logging.getLogger(__name__)


API_URL = "https://opus.nlpl.eu/opusapi/"
DOWNLOAD_URL = "https://object.pouta.csc.fi/OPUS-OpenSubtitles/v2024/raw/"


def list_opus_opensubtitles_languages() -> list[str]:
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


def download_subtitles(
    opus_language_tag: str, to_dir: str | Path, overwrite: bool = True
) -> Path:
    """Download a raw subtitle ZIP archive.

    Parameters
    ----------
    opus_language_tag : str
        The OPUS language tag for the subtitles.
    to_dir : str | Path
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
    to_path = Path(to_dir).joinpath(file_name)
    if not to_path.exists() or overwrite:
        logger.info(f"Downloading {from_url} to {to_path.parent.resolve()}")
        download(from_url, to_dir)

    return to_path


def extract_subtitles(
    from_zip: str | Path,
    to_dir: str | Path,
    distinct_title: bool = False,
    original_only: bool = False,
    cased_only: bool = False,
    deduplicate: bool = False,
    batch_size: int = 1000,
    nb_workers: int | None = None,
) -> None:
    """Extract XML subtitle files from a raw ZIP archive and save them as .txt
    files.

    Parameters
    ----------
    from_zip : str | Path
        The path to the input ZIP file.
    to_dir : str | Path
        The directory to save the extracted .txt files.
    distinct_title : bool, optional
        Whether to extract only one subtitle per IMDb ID, by default False
    original_only : bool, optional
        Whether to extract only subtitles in the original language, by default
        False
    cased_only : bool, optional
        Whether to only include cased subtitles, by default False
    deduplicate : bool, optional
        Whether to deduplicate consecutive subtitles, by default False
    batch_size : int, optional
        The number of XML files to process in each batch, by default 1000
    nb_workers : int | None, optional
        The number of worker processes to use for parallel processing. If None,
        the number of CPU cores is used, by default None
    """
    logger.info(
        f"extracting {Path(from_zip).resolve()} XML files as .txt files "
        f"to {Path(to_dir).resolve()}/"
    )
    unzipped_doc_ids = []
    zipped_subs = ZippedSubtitles(Path(from_zip))
    for imdb_id, doc_id, xml_lines in zipped_subs.iter_xml_files(
        distinct_title=distinct_title,
        original_only=original_only,
        cased_only=cased_only,
        deduplicate=deduplicate,
        batch_size=batch_size,
        nb_workers=nb_workers,
    ):
        txt_path = Path(to_dir).joinpath(f"{imdb_id}-{doc_id}.txt")
        subtitle_txt = SubtitleTXT(txt_path)
        subtitle_txt.write_lines(xml_lines)
        unzipped_doc_ids.append(doc_id)
    nb_unzipped = len(unzipped_doc_ids)
    logger.info(f"{nb_unzipped} subtitles extracted as .txt files")


def read_extracted_subtitles(
    from_path: str | Path,
) -> Generator[tuple[str, str, str], None, None]:
    """Read all subtitle lines from a directory of .txt files.

    Parameters
    ----------
    from_path : str | Path
        The path of the directory containing subtitle files.

    Returns
    -------
    Generator[tuple[str, str, str], None, None]
        A generator yielding the lines of all subtitle files along with their
        IMDb and OPUS document IDs.
    """
    from_path = Path(from_path)
    if from_path.is_dir():
        logger.info(
            f"Reading subtitle lines from directory {from_path.resolve()}"
        )
        subtitle_corpus = UnzippedSubtitles(Path(from_path))
        return (
            (line, sub.imdb_id, sub.doc_id)
            for sub in subtitle_corpus.txt_files()
            for line in sub.read_lines()
        )
    else:
        raise ValueError(f"Invalid subtitle directory: {from_path}.")


def read_zipped_subtitles(
    from_path: str | Path,
    distinct_title: bool = False,
    original_only: bool = False,
    cased_only: bool = False,
    deduplicate: bool = False,
    batch_size: int = 1000,
    nb_workers: int | None = None,
) -> Generator[tuple[str, str, str], None, None]:
    """Read all subtitle lines from an archive of .xml files.

    Parameters
    ----------
    from_path : str | Path
        The path of the input ZIP file containing subtitle files.

    Returns
    -------
    Generator[tuple[str, str, str], None, None]
        A generator yielding the lines of all subtitle files along with their
        IMDb and OPUS document IDs.
    """
    from_path = Path(from_path)
    if from_path.is_file() and from_path.suffix == ".zip":
        logger.info(f"Reading subtitle lines from {from_path.resolve()}")
        raw_zip = ZippedSubtitles(from_path)
        return (
            (line, imdb_id, doc_id)
            for imdb_id, doc_id, lines in raw_zip.iter_xml_files(
                distinct_title=distinct_title,
                original_only=original_only,
                cased_only=cased_only,
                deduplicate=deduplicate,
                batch_size=batch_size,
                nb_workers=nb_workers,
            )
            for line in lines
        )
    else:
        raise ValueError(f"Invalid subtitle archive: {from_path}.")

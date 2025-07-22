import logging

from .opus_subtitles import (
    download_subtitles,
    extract_subtitles,
    list_opus_opensubtitles_languages,
    read_extracted_subtitles,
    read_zipped_subtitles,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")

__all__ = [
    "download_subtitles",
    "extract_subtitles",
    "list_opus_opensubtitles_languages",
    "read_extracted_subtitles",
    "read_zipped_subtitles",
]

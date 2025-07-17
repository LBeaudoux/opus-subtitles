import logging

from .opus_subtitles import (
    download_raw_subtitle_zip,
    extract_subtitle_txt_files,
    list_opus_language_tags,
    read_subtitle_lines,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")

__all__ = [
    "download_raw_subtitle_zip",
    "extract_subtitle_txt_files",
    "list_opus_language_tags",
    "read_subtitle_lines",
]

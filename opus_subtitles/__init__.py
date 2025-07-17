import logging

from .opus_subtitles import (
    download_subtitle_raw_zip,
    extract_subtitle_txt_files,
    list_opus_language_tags,
    read_subtitle_lines,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")

__all__ = [
    "download_subtitle_raw_zip",
    "extract_subtitle_txt_files",
    "list_opus_language_tags",
    "read_subtitle_lines",
]

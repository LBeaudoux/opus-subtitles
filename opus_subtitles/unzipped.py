import logging
import os
from pathlib import Path
from typing import Generator, Iterable

from tqdm import tqdm

logger = logging.getLogger(__name__)


class SubtitleTXT:
    """A class representing a subtitle file in .txt format."""

    def __init__(self, file_path: Path) -> None:
        self._fp = file_path

    def write_lines(self, new_lines: Iterable) -> None:
        """Write new lines to the subtitle file."""
        self._fp.parent.mkdir(parents=True, exist_ok=True)
        with open(self._fp, "w") as f:
            rows = map(lambda x: x + "\n", new_lines)
            f.writelines(rows)

    def read_lines(self) -> Generator[str, None, None]:
        """Read lines from the subtitle file."""
        return (line.strip() for line in open(self._fp))

    @property
    def imdb_id(self) -> str:
        """Get the IMDb ID of the subtitle."""
        return self._fp.stem.split("-")[0]

    @property
    def doc_id(self) -> str:
        """Get the document ID of the subtitle."""
        return self._fp.stem.split("-")[1]


class UnzippedSubtitles:
    """A class representing a collection of subtitle files in a directory."""

    def __init__(self, dir_path: Path) -> None:
        self._dir = dir_path

    def txt_files(self) -> Generator[SubtitleTXT, None, None]:
        """Yield SubtitleTXT objects for each .txt file in the directory."""
        sub_fnames = self.list_subtitles()
        with tqdm(total=len(sub_fnames)) as pbar:
            for fname in sub_fnames:
                sub_path = self._dir.joinpath(fname)
                yield SubtitleTXT(sub_path)
                pbar.update()

    def list_subtitles(self):
        """List all subtitle files in the directory."""
        try:
            sub_fnames = os.listdir(self._dir)
        except FileNotFoundError:
            sub_fnames = []
        return sub_fnames

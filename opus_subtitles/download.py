import logging
from pathlib import Path

import requests
from tqdm import tqdm

logger = logging.getLogger(__name__)


def download(from_url, to_directory, verbose=True):
    """Download a file. Overwrite previous version."""
    # build out file path
    filename = from_url.rsplit("/", 1)[-1]
    to_dir_path = Path(to_directory)
    to_dir_path.mkdir(parents=True, exist_ok=True)
    to_path = to_dir_path.joinpath(filename)

    try:
        with requests.get(from_url, stream=True) as r:
            r.raise_for_status()
            # init progress bar
            if verbose:
                total_size = int(r.headers.get("content-length", 0))
                tqdm_args = {
                    "total": total_size,
                    "unit": "iB",
                    "unit_scale": True,
                }
                pbar = tqdm(**tqdm_args)
            else:
                pbar = None
            # write data in out file
            with open(to_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024):
                    f.write(chunk)
                    if pbar:
                        pbar.update(len(chunk))
                if pbar:
                    pbar.close()
    except requests.exceptions.RequestException:
        logger.error(f"downloading of {from_url} failed")
        return
    else:
        return to_path

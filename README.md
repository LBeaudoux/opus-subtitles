# opus-subtitles

`opus-subtitles` is a tool to download and parse monolingual OpenSubtitles corpora from the OPUS project.

## Installation

```sh
pip install git+https://github.com/LBeaudoux/opus-subtitles.git#egg=opus-subtitles
```

## Usage

Here are some examples of how to use the `opus-subtitles` package.

### List available languages

```python
from opus_subtitles import list_opus_opensubtitles_languages

list_opus_opensubtitles_languages() # Output: ['bg', 'cs', ... , 'zh_ze']
```

### Download a subtitle archive

```python
from opus_subtitles import download_subtitles

download_subtitles("fr", to_dir="subtitles", overwrite=True)  
```

### Extract subtitle files

```python
from opus_subtitles import extract_subtitles

extract_subtitles(
    "subtitles/fr.zip",
    to_dir="subtitles/fr",
    distinct_title=True,
    original_only=True,
    cased_only=True,
    deduplicate=True,
)
```

### Read subtitle lines from an extracted directory

```python
from opus_subtitles import read_extracted_subtitles

for line, imdb_id, doc_id in read_extracted_subtitles("subtitles/fr/"):
    print(line, imdb_id, doc_id)
```

### Read subtitle lines directly from an archive

```python
from opus_subtitles import read_zipped_subtitles

for line, imdb_id, doc_id in read_zipped_subtitles(
    "subtitles/fr.zip",
    distinct_title=True,
    original_only=True,
    cased_only=True,
    deduplicate=True,
):
    print(line, imdb_id, doc_id)
```


## Acknowledgments

`opus-subtitles` makes use of subtitles from [OpenSubtitles.org](https://www.opensubtitles.org/), which provides a large, multilingual corpus of user-contributed subtitles.

The [OPUS project](https://opus.nlpl.eu/) regularly compiles OpenSubtitles data into structured datasets, making it accessible for research in natural language processing.

## References

P. Lison and J. Tiedemann, 2016, [OpenSubtitles2016: Extracting Large Parallel Corpora from Movie and TV Subtitles.](https://aclanthology.org/L16-1147/) In Proceedings of the 10th International Conference on Language Resources and Evaluation (LREC 2016)
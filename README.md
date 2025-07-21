# opus-subtitles

`opus-subtitles` is a tool to download and parse monolingual OpenSubtitles corpora from the OPUS project.

## Installation

```sh
pip install git+https://github.com/LBeaudoux/opus-subtitles.git#egg=opus-subtitles
```

## Usage

Here are some examples of how to use the `opus-subtitles` package.

### List Available Languages

```python
from opus_subtitles import list_opus_language_tags

list_opus_language_tags() # Output: ['bg', 'cs', ... , 'zh_ze']
```

### Download a Subtitle Archive

```python
from opus_subtitles import download_subtitle_raw_zip

download_subtitle_raw_zip("zh_ze", to_dir="data", overwrite=True)  
```

### Extract Subtitle Files

```python
from opus_subtitles import unzip_subtitle_txt_files

unzip_subtitle_txt_files(
    "fr.zip",
    to_dir="fr_subtitles",   
    distinct_title=True,
    original_only=True,
    cased_only=True,
    deduplicate=True,
)
```

### Read Subtitle Lines

- From a ZIP archive:

```python
from opus_subtitles import read_subtitle_lines

for line, imdb_id, doc_id in read_subtitle_lines("fr.zip"):
    print(line, imdb_id, doc_id)
```

- From an extracted directory:

```python
from opus_subtitles import read_subtitle_lines

for line, imdb_id, doc_id in read_subtitle_lines("fr_subtitles/"):
    print(line, imdb_id, doc_id)
```

## Acknowledgments

`opus-subtitles` makes use of subtitles from [OpenSubtitles.org](https://www.opensubtitles.org/), which provides a large, multilingual corpus of user-contributed subtitles.

The [OPUS project](https://opus.nlpl.eu/) regularly compiles OpenSubtitles data into structured datasets, making it accessible for research in natural language processing.

## References

P. Lison and J. Tiedemann, 2016, [OpenSubtitles2016: Extracting Large Parallel Corpora from Movie and TV Subtitles.](https://aclanthology.org/L16-1147/) In Proceedings of the 10th International Conference on Language Resources and Evaluation (LREC 2016)
from itertools import groupby
from operator import itemgetter
from typing import Generator, Iterable


def strip_whitespaces(my_texts: list[str]) -> list[str]:
    """Strip whitespaces on both ends

    >>> strip_whitespaces([" foo", "  \tbar  "])
    ['foo', 'bar']
    """
    return list(filter(None, map(lambda x: x.strip(), my_texts)))


def deduplicate_consecutive(my_texts: list[str]) -> list[str]:
    """Deduplicate consecutive duplicates

    >>> deduplicate_consecutive([1, 1, 1, 2, 3, 1, 1])
    [1, 2, 3, 1]
    """
    return list(map(itemgetter(0), groupby(my_texts)))


def is_cased(my_text: str) -> bool:
    """Check if a string is cased

    >>> is_cased('FOOBAR')
    False
    >>> is_cased('foobar')
    False
    >>> is_cased('Foobar')
    True
    """
    return not (my_text.isupper() or my_text.islower())


def iter_batch(
    iterable: Iterable, batch_size: int
) -> Generator[list, None, None]:
    """Yield successive n-sized chunks from iterable."""
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:
        yield batch

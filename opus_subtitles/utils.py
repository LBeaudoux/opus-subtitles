from itertools import groupby
from operator import itemgetter


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


def are_cased(my_texts: list[str], threshold: float = 0.9) -> bool:
    return len(list(filter(is_cased, my_texts))) / len(my_texts) >= threshold

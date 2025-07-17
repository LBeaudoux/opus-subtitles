from langcodes import Language, standardize_tag
from langcodes.tag_parser import LanguageTagError


def get_language_code(language_name: str, macro: bool = False) -> str:
    """Get the language code for a given language name."""
    try:
        language_tag = Language.find(language_name, language="en").to_tag()
    except LookupError:
        language_code = ""
    else:
        if macro:
            language_tag = standardize_tag(language_tag, macro=True)
        language_code = language_tag.split("-")[0]

    return language_code


def get_language_name(language_tag: str, macro: bool = False) -> str:
    """Get the language name for a given language tag."""
    try:
        standard_tag = standardize_tag(language_tag, macro=macro)
    except LanguageTagError:
        language_name = ""
    else:
        language_name = Language.get(standard_tag).language_name()

    return language_name

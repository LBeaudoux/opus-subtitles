from iso639 import Lang
from iso639.exceptions import DeprecatedLanguageValue, InvalidLanguageValue
from langcodes import Language


def get_language_code(language: str, macro: bool = False) -> str:
    """Get the corresponding ISO 639-3 identifier for a given language name or
    language tag.
    """
    language_value = language.split("_")[0]  # Handle OPUS language tags

    try:
        lang = Lang(language_value)
    except InvalidLanguageValue:
        try:
            # Recognize non-standard ISO 639 language names
            language_code = Language.find(language_value).to_alpha3()
        except LookupError:
            language_code = ""
    except DeprecatedLanguageValue as e:
        language_code = Lang(e.change_to).pt3
    else:
        language_code = lang.pt3

    # Replace by macrolanguage when there is one
    if macro and language_code:
        macro_lang = Lang(language_code).macro()
        if macro_lang:
            language_code = macro_lang.pt3

    return language_code

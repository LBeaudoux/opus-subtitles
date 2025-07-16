from langcodes import Language, find, standardize_tag
from langcodes.tag_parser import LanguageTagError


class LangTag:
    # Scripts used by regex (https://github.com/mrabarnett/mrab-regex)
    _scripts = {
        "af": ["Latn"],
        "ar": ["Arab"],
        "bg": ["Cyrl"],
        "bn": ["Beng"],
        "br": ["Latn"],
        "bs": ["Cyrl", "Latn"],
        "ca": ["Latn"],
        "cs": ["Latn"],
        "da": ["Latn"],
        "de": ["Latn"],
        "el": ["Grek"],
        "en": ["Latn"],
        "eo": ["Latn"],
        "es": ["Latn"],
        "et": ["Latn"],
        "eu": ["Latn"],
        "fa": ["Arab"],
        "fi": ["Latn"],
        "fr": ["Latn"],
        "gl": ["Latn"],
        "he": ["Hebr"],
        "hi": ["Deva"],
        "hr": ["Latn"],
        "hu": ["Latn"],
        "hy": ["Armn"],
        "id": ["Latn"],
        "is": ["Latn"],
        "it": ["Latn"],
        "ja": ["Hrkt"],  # hiragana or katakana
        "ka": ["Geor"],
        "kk": ["Arab", "Cyrl"],
        "ko": ["Hang"],
        "lt": ["Latn"],
        "lv": ["Latn"],
        "mk": ["Cyrl"],
        "ml": ["Mlym"],
        "ms": ["Arab", "Latn"],
        "nl": ["Latn"],
        "no": ["Latn"],
        "pl": ["Latn"],
        "pt": ["Latn"],
        "pt-BR": ["Latn"],
        "ro": ["Latn"],
        "ru": ["Cyrl"],
        "si": ["Sinh"],
        "sk": ["Latn"],
        "sl": ["Latn"],
        "sq": ["Latn"],
        "sr": ["Cyrl", "Latn"],
        "sv": ["Latn"],
        "ta": ["Taml"],
        "te": ["Telu"],
        "th": ["Thai"],
        "fil": ["Latn"],
        "tr": ["Latn"],
        "uk": ["Cyrl"],
        "ur": ["Arab"],
        "vi": ["Latn"],
        "zh-CN": ["Han"],
        "zh-TW": ["Han"],
    }

    def __init__(self, language: str):
        try:
            self._tag = standardize_tag(language)
        except LanguageTagError:
            try:
                self._tag = str(find(language))
            except LookupError:
                self._tag = ""

    def __repr__(self):
        return repr(self._tag)

    @property
    def language_code(self) -> str:
        return Language.get(self._tag).to_alpha3() if self._tag else ""

    @property
    def territory(self) -> str:
        return Language.get(self._tag).territory_name() if self._tag else ""

    @property
    def language_name(self) -> str:
        return Language.get(self._tag).language_name() if self._tag else ""

    @property
    def scripts(self) -> list[str]:
        return LangTag._scripts.get(self._tag, []) if self._tag else []

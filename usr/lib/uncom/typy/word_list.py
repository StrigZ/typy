import os
from utility import load_word_list
from constants import APP_DIR

from app_settings import get_app_settings

app_settings = get_app_settings()

INSTALLED_WORDS_DIR = "/usr/share/uncom/typy/words"
if os.path.exists(INSTALLED_WORDS_DIR):
    WORDS_DIR = INSTALLED_WORDS_DIR
else:
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, "..", "..", "..", ".."))
    WORDS_DIR = os.path.join(PROJECT_ROOT, "usr", "share", "uncom", "typy", "words")


class WordList:
    def __init__(self) -> None:
        self.words = self._load(app_settings.get_string_language())
        app_settings.connect("notify::string-language", self.on_language_change)

    def get_words(self):
        return self.words

    def on_language_change(self, obj, _):
        self.words = self._load(obj.props.string_language)

    def _load(self, lang: str):
        path = os.path.join(WORDS_DIR, f"words_{lang}.csv")
        if not os.path.exists(path):
            path = os.path.join(WORDS_DIR, "words_en.csv")  # fallback to English
        return load_word_list(path)


_word_list = WordList()


def get_word_list() -> WordList:
    return _word_list

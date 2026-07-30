import json
import os

from constants import APP_SETTINGS_FILE
from utility import ensure_folder_exists
from gi.repository import GObject
from typing import Literal


DEFAULT_MAX_CHARS = 100
DEFAULT_LANGUAGE = "en"


class AppSettings(GObject.Object):
    string_length = GObject.Property(type=int, default=DEFAULT_MAX_CHARS)
    string_language = GObject.Property(type=str, default=DEFAULT_LANGUAGE)

    def __init__(self):
        super().__init__()
        self._load_data()
        self.connect("notify::string-length", lambda *a: self._save_data())
        self.connect("notify::string-language", lambda *a: self._save_data())

    def get_string_language(self):
        return self.string_language

    def set_string_language(self, value: Literal["ru", "en"]):
        self.string_language = value

    def get_string_length(self) -> int:
        return self.string_length

    def set_string_length(self, value: int):
        self.string_length = value

    def _save_data(self):
        ensure_folder_exists(os.path.dirname(APP_SETTINGS_FILE))
        with open(APP_SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "string_length": self.string_length,
                    "string_language": self.string_language,
                },
                f,
            )

    def _load_data(self):
        try:
            with open(APP_SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.string_length = data.get("string_length", DEFAULT_MAX_CHARS)
            self.string_language = data.get("string_language", DEFAULT_LANGUAGE)
        except (FileNotFoundError, json.JSONDecodeError):
            pass


_app_settings = AppSettings()


def get_app_settings() -> AppSettings:
    return _app_settings

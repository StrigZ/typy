import json
import os

from constants import APP_SETTINGS_FILE
from utility import ensure_folder_exists
from gi.repository import GObject


DEFAULT_MAX_CHARS = 100
DEFAULT_LANGUAGE = "en"


class AppSettings(GObject.Object):
    string_length = GObject.Property(type=int, default=DEFAULT_MAX_CHARS)
    string_language = GObject.Property(type=str, default=DEFAULT_LANGUAGE)

    def __init__(self):
        super().__init__()
        self._load_data()
        self.connect("notify", lambda *a: self._save_data())

    def _property_names(self) -> list[str]:
        return [pspec.name.replace("-", "_") for pspec in self.list_properties()]

    def _save_data(self):
        ensure_folder_exists(os.path.dirname(APP_SETTINGS_FILE))
        data = {name: getattr(self, name) for name in self._property_names()}
        with open(APP_SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def _load_data(self):
        try:
            with open(APP_SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return

        for name in self._property_names():
            if name in data:
                setattr(self, name, data[name])


_app_settings = AppSettings()


def get_app_settings() -> AppSettings:
    return _app_settings

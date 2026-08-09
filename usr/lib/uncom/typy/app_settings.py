from constants import APP_SETTINGS_FILE
from gi.repository import GObject

from json_persisted import JsonPersisted
# DEFAULTS

MAX_CHARS = 100
LANGUAGE = "en"
DAILY_GOAL_IN_MINUTES = 15


class AppSettings(GObject.Object, JsonPersisted):
    string_length = GObject.Property(type=int, default=MAX_CHARS)
    string_language = GObject.Property(type=str, default=LANGUAGE)
    daily_goal = GObject.Property(type=int, default=DAILY_GOAL_IN_MINUTES)

    def __init__(self):
        super().__init__()
        self._load_data()
        self.connect("notify", lambda *a: self._save_data())

    def _property_names(self) -> list[str]:
        return [pspec.name.replace("-", "_") for pspec in self.list_properties()]

    def _save_data(self):
        data = {name: getattr(self, name) for name in self._property_names()}
        self._save_raw(APP_SETTINGS_FILE, data)

    def _load_data(self):
        raw = self._load_raw(APP_SETTINGS_FILE)

        for name in self._property_names():
            if name in raw:
                setattr(self, name, raw[name])


_app_settings = AppSettings()


def get_app_settings() -> AppSettings:
    return _app_settings

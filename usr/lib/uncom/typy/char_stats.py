import json
import os
from typing import TypedDict

from constants import USER_DATA_DIR
from utility import ensure_folder_exists, delete_file_if_exists

from app_settings import get_app_settings

app_settings = get_app_settings()


TIME_CEILING = 5.0  # ignore pauses longer than this
MIN_SAMPLES = 5  # reps needed before trusting a char's average
SLOW_MULTIPLIER = 1.8  # "slow" = this much slower than the char's own average
EMA_ALPHA = 0.25  # how fast the rolling average adapts to recent reps


class CharStat(TypedDict):
    miss: int
    slow: int
    avg_time: float
    samples: int


class CharStats:
    def __init__(self):
        self.path = os.path.join(
            USER_DATA_DIR, f"key_stats_{app_settings.string_language}.json"
        )

        self.data: dict[str, CharStat] = self._load()
        app_settings.connect("notify::string-language", self.on_language_change)

    def on_language_change(self, obj, _pspec):
        self.path = os.path.join(
            USER_DATA_DIR, f"key_stats_{obj.props.string_language}.json"
        )

        self.data = self._load()

    def update_stat(
        self, char: str, elapsed: float | None, is_correct: bool, skip_timing=False
    ):
        if not char.isalpha():
            return

        stat = self.get_stat(char)

        if not is_correct:
            stat["miss"] += 1
            return

        # First keystroke = speed is ignored
        if skip_timing or elapsed is None:
            return

        if elapsed > TIME_CEILING:
            return

        is_slow = (
            stat["samples"] >= MIN_SAMPLES
            and elapsed > stat["avg_time"] * SLOW_MULTIPLIER
        )
        stat["avg_time"] = (
            elapsed
            if stat["samples"] == 0
            else EMA_ALPHA * elapsed + (1 - EMA_ALPHA) * stat["avg_time"]
        )
        stat["samples"] += 1

        if is_slow:
            stat["slow"] += 1
        else:
            stat["slow"] = max(0, stat["slow"] - 1)
            stat["miss"] = max(0, stat["miss"] - 1)

    def peek_stat(self, char: str) -> CharStat | None:
        return self.data.get(char)

    def get_stat(self, char: str) -> CharStat:
        if char not in self.data:
            self._add_new_char(char)
        return self.data[char]

    def save_data(self):
        ensure_folder_exists(os.path.dirname(self.path))
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False)

    def reset_data(self):
        self.data.clear()
        delete_file_if_exists(self.path)

    def _add_new_char(self, char: str):
        self.data[char] = {"miss": 0, "slow": 0, "avg_time": 0.0, "samples": 0}

    def _load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            return {char: CharStat(**fields) for char, fields in raw.items()}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

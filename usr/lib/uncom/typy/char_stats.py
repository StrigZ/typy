import json
import os
from typing import TypedDict

from constants import STATS_FILE
from utility import ensure_folder_exists, delete_file_if_exists

TIME_CEILING = (
    5.0  # ignore pauses longer than this — treat as distraction, not hesitation
)
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
        self.data: dict[str, CharStat] = self._load_data()

    def update_stat(self, char: str, elapsed: float, is_correct: bool):
        stat = self.get_stat(char)

        if not is_correct:
            stat["miss"] += 1
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

    def get_stat(self, char: str):
        if char not in self.data:
            self._add_new_char(char)
        return self.data[char]

    def save_data(self):
        ensure_folder_exists(os.path.dirname(STATS_FILE))
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f)

    def reset_data(self):
        self.data.clear()
        delete_file_if_exists(STATS_FILE)

    def _add_new_char(self, char: str):
        self.data[char] = {"miss": 0, "slow": 0, "avg_time": 0.0, "samples": 0}

    def _load_data(self):
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
            return {char: CharStat(**fields) for char, fields in raw.items()}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

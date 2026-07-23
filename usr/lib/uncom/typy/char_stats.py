import json
import os
import random
from typing import TypedDict

from constants import STATS_FILE
from utility import ensure_folder_exists, delete_file_if_exists


class CharStat(TypedDict):
    miss: int
    slow: int
    avg_time: float
    samples: int


class CharStats:
    def __init__(self):
        self.data: dict[str, CharStat] = self._load_data()

    def record_sample(self, char: str):
        if char not in self.data:
            self._add_new_char(char)

        self.data[char]["samples"] += 1
        self.save_data()

    def record_miss(self, char: str):
        if char not in self.data:
            self._add_new_char(char)

        self.data[char]["miss"] += 1
        self.save_data()

    def record_slow(self, char: str):
        if char not in self.data:
            self._add_new_char(char)

        self.data[char]["slow"] += 1
        self.save_data()

    def save_data(self):
        ensure_folder_exists(os.path.dirname(STATS_FILE))
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f)

    def reset_data(self):
        self.data.clear()
        delete_file_if_exists(STATS_FILE)

    def _add_new_char(self, char: str):
        self.data[char] = {"miss": 0, "slow": 0, "avg_time": 0.0, "samples": 0}
        self.save_data()

    def _load_data(self):
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
            return {char: CharStat(**fields) for char, fields in raw.items()}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

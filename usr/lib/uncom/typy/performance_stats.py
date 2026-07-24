import json
import os
import time
from dataclasses import dataclass

from constants import PERFORMANCE_STATS_FILE
from utility import ensure_folder_exists, delete_file_if_exists

EMA_ALPHA = 0.2  # how fast the running average adapts to each new completed string


@dataclass
class PerformanceAverages:
    avg_wpm: float = 0.0
    avg_accuracy: float = 0.0
    strings_completed: int = 0


class PerformanceStats:
    def __init__(self):
        self.averages: PerformanceAverages = self._load_data()

        self.string_start_time = time.monotonic()
        self.keystrokes = 0
        self.mistakes = 0

    def start_new_string(self):
        self.string_start_time = time.monotonic()
        self.keystrokes = 0
        self.mistakes = 0

    def record_keystroke(self, is_correct: bool):
        self.keystrokes += 1
        if not is_correct:
            self.mistakes += 1

    def get_current_wpm(self, chars_typed: int) -> float:
        elapsed_minutes = (time.monotonic() - self.string_start_time) / 60
        if elapsed_minutes <= 0:
            return 0.0
        words = chars_typed / 5  # standard WPM convention: 5 chars = 1 "word"
        return words / elapsed_minutes

    def get_current_accuracy(self) -> float:
        if self.keystrokes == 0:
            return 100.0
        correct = self.keystrokes - self.mistakes
        return (correct / self.keystrokes) * 100

    def update_and_save_averages(self, chars_typed: int):
        wpm = self.get_current_wpm(chars_typed)
        accuracy = self.get_current_accuracy()

        n = self.averages.strings_completed
        if n == 0:
            self.averages.avg_wpm = wpm
            self.averages.avg_accuracy = accuracy
        else:
            self.averages.avg_wpm = (
                EMA_ALPHA * wpm + (1 - EMA_ALPHA) * self.averages.avg_wpm
            )
            self.averages.avg_accuracy = (
                EMA_ALPHA * accuracy + (1 - EMA_ALPHA) * self.averages.avg_accuracy
            )

        self.averages.strings_completed += 1
        self._save_data()

    def _save_data(self):
        ensure_folder_exists(os.path.dirname(PERFORMANCE_STATS_FILE))
        with open(PERFORMANCE_STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(vars(self.averages), f)

    def _load_data(self) -> PerformanceAverages:
        try:
            with open(PERFORMANCE_STATS_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
            return PerformanceAverages(**raw)
        except (FileNotFoundError, json.JSONDecodeError):
            return PerformanceAverages()

    def reset_data(self):
        self.averages = PerformanceAverages()
        delete_file_if_exists(PERFORMANCE_STATS_FILE)

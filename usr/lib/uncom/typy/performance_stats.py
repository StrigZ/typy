import json
import os
import time
from dataclasses import dataclass
from gi.repository import GObject

from constants import USER_DATA_DIR
from utility import ensure_folder_exists, delete_file_if_exists
from app_settings import get_app_settings

app_settings = get_app_settings()

EMA_ALPHA = 0.2  # how fast the running average adapts to each new completed string


@dataclass
class Performance:
    best_wpm: float = 0.0
    avg_wpm: float = 0.0
    avg_accuracy: float = 0.0
    strings_completed: int = 0


@dataclass
class StringResult:
    wpm: float
    accuracy: float
    wpm_diff: float
    accuracy_diff: float
    is_first: bool


class PerformanceStats(GObject.Object):
    __gsignals__ = {
        "new-best-wpm": (GObject.SignalFlags.RUN_FIRST, None, (float,)),
    }

    def __init__(self):
        super().__init__()
        self.path = os.path.join(
            USER_DATA_DIR, f"performance_{app_settings.string_language}.json"
        )
        app_settings.connect("notify::string-language", self.on_language_change)

        self.performance: Performance = self._load()

        self.string_start_time: None | float = None
        self.keystrokes = 0
        self.mistakes = 0

    def on_language_change(self, obj, _pspec):
        self.path = os.path.join(
            USER_DATA_DIR, f"performance_{obj.props.string_language}.json"
        )

        self.performance: Performance = self._load()

    def reset_counters(self):
        self.string_start_time = None
        self.keystrokes = 0
        self.mistakes = 0

    def record_keystroke(self, is_correct: bool):
        self.keystrokes += 1
        if not is_correct:
            self.mistakes += 1

    def get_current_wpm(self, chars_typed: int) -> float:
        if self.string_start_time is None:
            return 0.0

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

    def update_and_save_averages(self, chars_typed: int) -> StringResult:
        wpm = self.get_current_wpm(chars_typed)
        accuracy = self.get_current_accuracy()
        is_first = self.performance.strings_completed == 0

        if is_first:
            wpm_diff = 0.0
            accuracy_diff = 0.0
            self.performance.best_wpm = wpm
            self.performance.avg_wpm = wpm
            self.performance.avg_accuracy = accuracy
        else:
            wpm_diff = wpm - self.performance.avg_wpm
            accuracy_diff = accuracy - self.performance.avg_accuracy

            if wpm > self.performance.best_wpm:
                self.performance.best_wpm = wpm
                self.emit("new-best-wpm", wpm)

            self.performance.avg_wpm = (
                EMA_ALPHA * wpm + (1 - EMA_ALPHA) * self.performance.avg_wpm
            )
            self.performance.avg_accuracy = (
                EMA_ALPHA * accuracy + (1 - EMA_ALPHA) * self.performance.avg_accuracy
            )

        self.performance.strings_completed += 1
        self._save_data()

        return StringResult(wpm, accuracy, wpm_diff, accuracy_diff, is_first)

    def _save_data(self):
        ensure_folder_exists(os.path.dirname(self.path))
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(vars(self.performance), f)

    def _load(self) -> Performance:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            return Performance(
                best_wpm=raw.get("best_wpm", 0.0),
                avg_wpm=raw.get("avg_wpm", 0.0),
                avg_accuracy=raw.get("avg_accuracy", 0.0),
                strings_completed=raw.get("strings_completed", 0),
            )
        except (FileNotFoundError, json.JSONDecodeError):
            return Performance()

    def reset_data(self):
        self.performance = Performance()
        delete_file_if_exists(self.path)

import os

from app_settings import get_app_settings
from constants import LEARNING_MIN_SAMPLES, LEARNING_ORDER, USER_DATA_DIR
from gi.repository import GObject
from json_persisted import JsonPersisted
from utility import delete_file_if_exists

app_settings = get_app_settings()


class LearningProgress(GObject.Object, JsonPersisted):
    __gsignals__ = {
        "progress-changed": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, char_stats):
        super().__init__()
        self._char_stats = char_stats
        self.order = LEARNING_ORDER[app_settings.string_language]
        self.current_index = min(2, len(self.order) - 1)
        self._set_path()
        self._load()
        app_settings.connect("notify::string-language", self._on_language_change)
        app_settings.connect("notify::desired-wpm", self._on_desired_wpm_change)

    def get_active_chars(self) -> list[str]:
        return list(self.order[: self.current_index + 1])

    def get_active_chars_lower(self) -> list[str]:
        return [c.lower() for c in self.get_active_chars()]

    def get_needs_improvement(self) -> list[str]:
        return [c for c in self.get_active_chars() if not self._meets_target(c)]

    def get_current_learning_char(self) -> str:
        queue = self.get_needs_improvement()
        if not queue:
            return self.order[self.current_index]

        newest = self.order[self.current_index]
        established_queue = [c for c in queue if c != newest]
        candidates = established_queue if established_queue else queue

        def gap(c: str) -> float:
            stat = self._char_stats.peek_stat(c.lower())
            threshold = self._threshold_seconds()
            if stat is None or stat.get("samples", 0) == 0:
                return float("inf")
            return stat["avg_time"] - threshold

        return min(candidates, key=gap)

    def get_current_learning_char_lower(self) -> str:
        return self.get_current_learning_char().lower()

    def check_progress(self):
        if self.get_needs_improvement():
            return
        if self.current_index >= len(self.order) - 1:
            return
        self.current_index += 1
        self._save()
        self.emit("progress-changed")

    def get_proficiency(self, char: str) -> float:
        stat = self._char_stats.peek_stat(char.lower())
        if stat is None or stat.get("samples", 0) == 0:
            return 0.0
        threshold = self._threshold_seconds()
        ratio = (2 * threshold - stat["avg_time"]) / (2 * threshold - 0)
        return max(0.0, min(1.0, ratio))

    def get_all_proficiencies(self) -> dict[str, float]:
        return {c: self.get_proficiency(c) for c in self.order}

    def _meets_target(self, char: str) -> bool:
        stat = self._char_stats.peek_stat(char.lower())
        threshold = self._threshold_seconds()
        return (
            stat is not None
            and stat.get("samples", 0) >= LEARNING_MIN_SAMPLES
            and stat["avg_time"] < threshold
        )

    def _threshold_seconds(self) -> float:
        wpm = max(1, app_settings.desired_wpm)
        return 60 / (wpm * 5)

    def _on_language_change(self, obj, _pspec):
        self.order = LEARNING_ORDER[app_settings.string_language]
        self._set_path()
        self._load()
        self.emit("progress-changed")

    def _on_desired_wpm_change(self, obj, _pspec):
        self.emit("progress-changed")

    def _set_path(self):
        self.path = os.path.join(
            USER_DATA_DIR, f"learning_progress_{app_settings.string_language}.json"
        )

    def _load(self):
        raw = self._load_raw(self.path)
        self.current_index = raw.get("current_index", min(2, len(self.order) - 1))

    def _save(self):
        self._save_raw(self.path, {"current_index": self.current_index})

    def reset(self):
        self.current_index = min(2, len(self.order) - 1)
        delete_file_if_exists(self.path)

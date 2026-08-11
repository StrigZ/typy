from gi.repository import GObject
from app_settings import get_app_settings
from constants import LEARNING_MIN_SAMPLES, LEARNING_ORDER

app_settings = get_app_settings()


class LearningProgress(GObject.Object):
    __gsignals__ = {
        "progress-changed": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, char_stats):
        super().__init__()
        self._char_stats = char_stats
        self.order = LEARNING_ORDER[app_settings.string_language]
        self.current_index = self._compute_current_index()
        app_settings.connect("notify::string-language", self._on_language_change)
        app_settings.connect("notify::desired-wpm", self._on_desired_wpm_change)

    def get_active_chars(self) -> list[str]:
        return list(self.order[: self.current_index + 1])

    def get_current_learning_char(self) -> str:
        return self.order[self.current_index]

    def check_progress(self):
        new_index = self._compute_current_index()
        if new_index != self.current_index:
            self.current_index = new_index
            self.emit("progress-changed")

    def get_proficiency(self, char: str) -> float:
        stat = self._char_stats.peek_stat(char)
        if stat is None or stat.get("samples", 0) == 0:
            return 0.0
        threshold = self._threshold_seconds()
        # avg_time at or below threshold = 1.0 (mastered speed)
        # avg_time at 2x threshold or worse = 0.0 (floor)
        ratio = 1 - (stat["avg_time"] - threshold) / threshold
        return max(0.0, min(1.0, ratio))

    def get_all_proficiencies(self) -> dict[str, float]:
        return {c: self.get_proficiency(c) for c in self.order}

    def _threshold_seconds(self) -> float:
        return 60 / (app_settings.desired_wpm * 5)

    def _compute_current_index(self) -> int:
        threshold = self._threshold_seconds()

        for i, c in enumerate(self.order):
            stat = self._char_stats.peek_stat(c.lower())
            is_mastered = (
                stat is not None
                and stat.get("samples", 0) >= LEARNING_MIN_SAMPLES
                and stat["avg_time"] < threshold
            )
            if not is_mastered:
                return i
        return len(self.order) - 1

    def _on_language_change(self, obj, _pspec):
        self.current_index = self._compute_current_index()
        self.order = LEARNING_ORDER[app_settings.string_language]
        self.emit("progress-changed")

    def _on_desired_wpm_change(self, obj, _pspec):
        self.current_index = self._compute_current_index()
        self.emit("progress-changed")

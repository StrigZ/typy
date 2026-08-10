from gi.repository import GObject
from app_settings import get_app_settings
from constants import LEARNING_MIN_SAMPLES, LEARNING_ORDER

app_settings = get_app_settings()


class LearningProgress(GObject.Object):
    __gsignals__ = {
        "progress-changed": (GObject.SignalFlags.RUN_FIRST, None),
    }

    def __init__(self, char_stats):
        super().__init__()
        self._char_stats = char_stats
        self.current_index = self._compute_current_index()

    def get_active_chars(self) -> list[str]:
        return list(LEARNING_ORDER[: self.current_index + 1])

    def get_current_learning_char(self) -> str:
        return LEARNING_ORDER[self.current_index]

    def check_progress(self):
        new_index = self._compute_current_index()
        if new_index != self.current_index:
            self.current_index = new_index
            self.emit("progress-changed")

    def _threshold_ms(self) -> float:
        return 60000 / (app_settings.desired_wpm * 5)

    def _compute_current_index(self) -> int:
        threshold = self._threshold_ms()
        for i, c in enumerate(LEARNING_ORDER):
            stat = self._char_stats.peek_stat(c)
            is_mastered = (
                stat is not None
                and stat.get("samples", 0) >= LEARNING_MIN_SAMPLES
                and stat["avg_time"] < threshold
            )
            if not is_mastered:
                return i
        return len(LEARNING_ORDER) - 1

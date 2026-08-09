import json
import os
from datetime import date, timedelta

from constants import USER_DATA_DIR
from utility import ensure_folder_exists
from dataclasses import dataclass, asdict, fields
from app_settings import get_app_settings
from gi.repository import GObject

app_settings = get_app_settings()


@dataclass
class DayRecord:
    goal_in_minutes: int = app_settings.daily_goal
    elapsed_in_minutes: float = 0.0

    chars_typed: int = 0
    strings_completed: int = 0
    wpm_sum: float = 0.0
    accuracy_sum: float = 0.0
    best_wpm: float = 0.0

    @property
    def avg_wpm(self) -> float:
        return self.wpm_sum / self.strings_completed if self.strings_completed else 0.0

    @property
    def avg_accuracy(self) -> float:
        return (
            self.accuracy_sum / self.strings_completed
            if self.strings_completed
            else 0.0
        )

    @property
    def is_goal_reached(self) -> bool:
        return self.elapsed_in_minutes >= self.goal_in_minutes


class DailyStats(GObject.Object):
    __gsignals__ = {
        "goal-reached": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self):
        super().__init__()
        self.path = os.path.join(
            USER_DATA_DIR, f"daily_stats_{app_settings.string_language}.json"
        )
        app_settings.connect("notify::string-language", self.on_language_change)

        self._load()
        self._check_new_day()

    def on_language_change(self, obj, _pspec):
        self.path = os.path.join(
            USER_DATA_DIR, f"daily_stats_{obj.props.string_language}.json"
        )

        self._load()
        self._check_new_day()

    def _parse_record(self, raw: dict) -> DayRecord:
        known_fields = {f.name for f in fields(DayRecord)}
        return DayRecord(**{k: v for k, v in raw.items() if k in known_fields})

    def get_progress_in_fractions(self) -> float:
        if self.today.goal_in_minutes <= 0:
            return 0.0
        return self.today.elapsed_in_minutes / self.today.goal_in_minutes

    def get_streak(self) -> int:
        def day_reached(raw: dict) -> bool:
            rec = self._parse_record(raw)
            return rec.elapsed_in_minutes >= rec.goal_in_minutes

        streak = 0
        current_date = date.today()

        # If today's goal is not reached yet,
        # start counting from yesterday
        today_data = self.data.get(current_date.isoformat(), {})
        if not day_reached(today_data):
            current_date -= timedelta(days=1)

        while True:
            day_data = self.data.get(current_date.isoformat())
            if not day_data or not day_reached(day_data):
                break
            streak += 1
            current_date -= timedelta(days=1)

        return streak

    def record_string(self, chars_typed: int, wpm: float, accuracy: float):
        self._check_new_day()
        self.today.chars_typed += chars_typed
        self.today.strings_completed += 1
        self.today.wpm_sum += wpm
        self.today.best_wpm = max(wpm, self.today.best_wpm)
        self.today.accuracy_sum += accuracy
        self._save_data()

    def tick_progress(self, elapsed_in_seconds: float):
        self._check_new_day()

        was_reached = self.today.is_goal_reached
        self.today.elapsed_in_minutes += elapsed_in_seconds / 60

        if not was_reached and self.today.is_goal_reached:
            self.emit("goal-reached")

        self._save_data()

    def _check_new_day(self):
        today = date.today().isoformat()
        if today == self.date:
            return

        self.date = today
        self.today = DayRecord(
            goal_in_minutes=self.today.goal_in_minutes
        )  # carry the goal forward, reset everything else
        self._save_data()

    def _save_data(self):
        ensure_folder_exists(os.path.dirname(USER_DATA_DIR))
        self.data[self.date] = asdict(self.today)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f)

    def set_goal(self, goal: int):
        self.today.goal_in_minutes = goal
        self._save_data()

    def _load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
                today = date.today().isoformat()
                today_data = self.data.get(today, {})

                self.date = today

                self.today = (
                    self._parse_record(today_data)
                    if today_data
                    else DayRecord(goal_in_minutes=app_settings.daily_goal)
                )
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = {}
            self.date = None
            self.today = DayRecord(goal_in_minutes=app_settings.daily_goal)

    def reset_progress(self):
        self.today.elapsed_in_minutes = 0.0
        self._save_data()

    def reset_stats(self):
        self.today = DayRecord(
            goal_in_minutes=self.today.goal_in_minutes,
            elapsed_in_minutes=self.today.elapsed_in_minutes,
        )
        self._save_data()

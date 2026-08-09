from dataclasses import dataclass, asdict, fields
from app_settings import get_app_settings
from utility import ensure_folder_exists
from constants import DAILY_GOAL_FILE
from datetime import date, timedelta

import json
import os

app_settings = get_app_settings()


@dataclass
class DayRecord:
    elapsed_in_minutes: float = 0.0

    @property
    def is_goal_reached(self) -> bool:
        return self.elapsed_in_minutes >= app_settings.daily_goal


class DailyGoal:
    def __init__(self) -> None:
        self._load()

    def get_streak(self) -> int:
        def day_active(raw: dict) -> bool:
            rec = self._parse_record(raw)
            return rec.elapsed_in_minutes > 0

        streak = 0
        current_date = date.today()

        # If no activity today yet, start counting from yesterday
        today_data = self.data.get(current_date.isoformat(), {})
        if not day_active(today_data):
            current_date -= timedelta(days=1)

        while True:
            day_data = self.data.get(current_date.isoformat())
            if not day_data or not day_active(day_data):
                break
            streak += 1
            current_date -= timedelta(days=1)

        return streak

    def get_progress_in_fractions(self) -> float:
        if app_settings.daily_goal <= 0:
            return 0.0

        return self.today_record.elapsed_in_minutes / app_settings.daily_goal

    def tick_progress(self, elapsed_in_seconds: float):
        self._check_new_day()
        self.today_record.elapsed_in_minutes += elapsed_in_seconds / 60
        self._save_data()

    def _check_new_day(self):
        today = date.today().isoformat()
        if today == self.today_date:
            return

        self.today_date = today
        self.today_record = DayRecord()
        self._save_data()

    def _load(self):
        try:
            with open(DAILY_GOAL_FILE, "r", encoding="utf-8") as f:
                self.data = json.load(f)

                today: str = date.today().isoformat()
                today_data = self.data.get(today, {})

                self.today_date = today

                self.today_record = (
                    self._parse_record(today_data) if today_data else DayRecord()
                )
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = {}
            self.today_date = None
            self.today_record = DayRecord()

    def _save_data(self):
        ensure_folder_exists(os.path.dirname(DAILY_GOAL_FILE))
        self.data[self.today_date] = asdict(self.today_record)
        with open(DAILY_GOAL_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f)

    def _parse_record(self, raw: dict) -> DayRecord:
        known = {f.name for f in fields(DayRecord)}
        return DayRecord(**{k: v for k, v in raw.items() if k in known})

    def reset(self):
        self.today_record = DayRecord()
        self._save_data()

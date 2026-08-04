import json
import os
from datetime import date, timedelta

from constants import DAILY_GOAL_FILE
from utility import ensure_folder_exists

from app_settings import get_app_settings

app_settings = get_app_settings()


class DailyGoal:
    def __init__(self):
        self._load_data()

        today = date.today().isoformat()
        today_data = self.data.get(today, {})

        self.date = today
        self.goal_in_minutes = today_data.get(
            "goal_in_minutes", app_settings.daily_goal
        )
        self.elapsed_in_minutes = today_data.get("elapsed_in_minutes", 0.0)

        self._check_new_day()

    @property
    def is_goal_reached(self) -> bool:
        return self.elapsed_in_minutes >= self.goal_in_minutes

    def get_progress_in_fractions(self) -> float:
        if self.goal_in_minutes <= 0:
            return 0.0
        return self.elapsed_in_minutes / self.goal_in_minutes

    def get_streak(self) -> int:
        def day_reached(day_data: dict) -> bool:
            return day_data.get("elapsed_in_minutes", 0.0) >= day_data.get(
                "goal_in_minutes", 1
            )

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

    def increment(self, elapsed_in_seconds: float):
        self._check_new_day()
        self.elapsed_in_minutes += elapsed_in_seconds / 60
        self._save_data()

    def _check_new_day(self):
        today = date.today().isoformat()

        # if the same day, do nothing
        if today == self.date:
            return

        # if new day, reset props
        self.date = today
        self.elapsed_in_minutes = 0.0
        self._save_data()

    def _save_data(self):
        ensure_folder_exists(os.path.dirname(DAILY_GOAL_FILE))
        self.data[self.date] = {
            "goal_in_minutes": self.goal_in_minutes,
            "elapsed_in_minutes": self.elapsed_in_minutes,
        }
        with open(DAILY_GOAL_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f)

    def set_goal(self, goal: int):
        self.goal_in_minutes = goal
        self._save_data()

    def _load_data(self):
        try:
            with open(DAILY_GOAL_FILE, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = {}

    def reset_daily_progress(self):
        self.elapsed_in_minutes = 0.0
        self._save_data()

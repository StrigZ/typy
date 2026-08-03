import json
import os
from datetime import date, timedelta

from constants import DAILY_GOAL_FILE
from utility import ensure_folder_exists


class DailyGoal:
    def __init__(self):
        self._load_data()

        today = date.today().isoformat()
        today_data = self.data.get(today, {})

        self.date = today

        self.goal_in_minutes = today_data.get("goal_in_minutes", 15)
        self.elapsed_in_minutes = today_data.get("elapsed_in_minutes", 0.0)
        self.streak = today_data.get("streak", 0)
        self.was_goal_reached = today_data.get("was_goal_reached", False)

        self._check_new_day()

    @property
    def is_goal_reached(self) -> bool:
        return self.elapsed_in_minutes >= self.goal_in_minutes

    def reset_daily_progress(self):
        self.elapsed_in_minutes = 0.0
        self._save_data()

    def get_goal_in_minutes(self):
        return self.goal_in_minutes

    def get_progress_in_fractions(self) -> float:
        if self.goal_in_minutes <= 0:
            return 0.0
        return self.elapsed_in_minutes / self.goal_in_minutes

    def increment(self, elapsed_in_seconds: float):
        self._check_new_day()

        self.elapsed_in_minutes += elapsed_in_seconds / 60

        if not self.was_goal_reached and self.is_goal_reached:
            self.was_goal_reached = True

            yesterday_str = (date.today() - timedelta(days=1)).isoformat()
            yesterday_data = self.data.get(yesterday_str, {})

            if yesterday_data.get("was_goal_reached"):
                self.streak = yesterday_data.get("streak", 0) + 1
            else:
                self.streak = 1

        self._save_data()

    def set_goal(self, goal: int):
        self.goal_in_minutes = goal
        self._save_data()

    def _check_new_day(self):
        today = date.today().isoformat()
        yesterday_str = (date.today() - timedelta(days=1)).isoformat()

        # if the same day, do nothing
        if today == self.date:
            return

        # if new day, reset props
        self.date = today
        self.elapsed_in_minutes = 0
        self.was_goal_reached = False

        yesterday_data = self.data.get(yesterday_str, {})
        if yesterday_data.get("was_goal_reached"):
            self.streak = yesterday_data.get("streak", 0)
        else:
            self.streak = 0

        self._save_data()

    def _save_data(self):
        ensure_folder_exists(os.path.dirname(DAILY_GOAL_FILE))
        self.data[self.date] = {
            "goal_in_minutes": self.goal_in_minutes,
            "elapsed_in_minutes": self.elapsed_in_minutes,
            "was_goal_reached": self.was_goal_reached,
            "streak": self.streak,
        }

        with open(DAILY_GOAL_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f)

    def _load_data(self):
        try:
            with open(DAILY_GOAL_FILE, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = {}

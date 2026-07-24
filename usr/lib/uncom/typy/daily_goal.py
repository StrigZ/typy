import json
import os
from datetime import date

from constants import DAILY_GOAL_FILE
from utility import ensure_folder_exists


class DailyGoal:
    # TODO: get goal from config file
    def __init__(self, goal: int = 1):
        self.goal_in_minutes = goal
        self.elapsed_in_minutes: float = 0.0
        self.date: str = date.today().isoformat()
        self.is_goal_reached = self.elapsed_in_minutes >= self.goal_in_minutes

        self._load_data()

    def increment(self, elapsed_in_seconds: float):
        self._check_new_day()
        self.elapsed_in_minutes += elapsed_in_seconds / 60
        self.is_goal_reached = self.elapsed_in_minutes >= self.goal_in_minutes
        self._save_data()

    def set_goal(self, goal: int):
        self.goal_in_minutes = goal
        self._save_data()

    def _check_new_day(self):
        today = date.today().isoformat()
        if today != self.date:
            self.date = today
            self.elapsed_in_minutes = 0.0

    def _save_data(self):
        ensure_folder_exists(os.path.dirname(DAILY_GOAL_FILE))
        with open(DAILY_GOAL_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "goal_in_minutes": self.goal_in_minutes,
                    "elapsed_in_minutes": self.elapsed_in_minutes,
                    "goal_reached": self.is_goal_reached,
                    "date": self.date,
                },
                f,
            )

    def _load_data(self):
        try:
            with open(DAILY_GOAL_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.goal_in_minutes = data.get("goal_in_minutes", self.goal_in_minutes)
            self.elapsed_in_minutes = data.get("elapsed_in_minutes", 0.0)
            self.is_goal_reached = data.get("goal_reached", False)
            self.date = data.get("date", self.date)
            self._check_new_day()
        except (FileNotFoundError, json.JSONDecodeError):
            pass

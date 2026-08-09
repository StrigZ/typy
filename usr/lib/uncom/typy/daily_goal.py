from dataclasses import dataclass
from app_settings import get_app_settings
from constants import DAILY_GOAL_FILE
from datetime import date, timedelta
from json_persisted import JsonPersisted


app_settings = get_app_settings()


@dataclass
class DayRecord:
    elapsed_in_minutes: float = 0.0

    @property
    def is_goal_reached(self) -> bool:
        return self.elapsed_in_minutes >= app_settings.daily_goal


class DailyGoal(JsonPersisted):
    def __init__(self) -> None:
        self._load()

    def get_streak(self) -> int:
        def day_active(raw: dict) -> bool:
            rec = self._parse_record(DayRecord, raw)
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
        self.data = self._load_raw(DAILY_GOAL_FILE)
        today: str = date.today().isoformat()
        today_data = self.data.get(today, {})

        self.today_date = today

        self.today_record = (
            self._parse_record(DayRecord, today_data) if today_data else DayRecord()
        )

    def _save_data(self):
        self.data[self.today_date] = self._record_to_dict(self.today_record)
        self._save_raw(DAILY_GOAL_FILE, self.data)

    def reset(self):
        self.today_record = DayRecord()
        self._save_data()

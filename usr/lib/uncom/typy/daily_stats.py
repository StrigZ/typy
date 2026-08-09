import os
from datetime import date

from constants import USER_DATA_DIR
from dataclasses import dataclass
from app_settings import get_app_settings
from json_persisted import JsonPersisted


app_settings = get_app_settings()


@dataclass
class DayRecord:
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


class DailyStats(JsonPersisted):
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

    def record_string(self, chars_typed: int, wpm: float, accuracy: float):
        self._check_new_day()
        self.today_record.chars_typed += chars_typed
        self.today_record.strings_completed += 1
        self.today_record.wpm_sum += wpm
        self.today_record.best_wpm = max(wpm, self.today_record.best_wpm)
        self.today_record.accuracy_sum += accuracy
        self._save_data()

    def _check_new_day(self):
        today = date.today().isoformat()
        if today == self.today_date:
            return

        self.today_date = today
        self.today_record = DayRecord()
        self._save_data()

    def _save_data(self):
        self.data[self.today_date] = self._record_to_dict(self.today_record)
        self._save_raw(self.path, self.data)

    def _load(self):
        self.data = self._load_raw(self.path)
        today = date.today().isoformat()
        today_data = self.data.get(today, {})
        self.today_date = today
        self.today_record = (
            self._parse_record(DayRecord, today_data) if today_data else DayRecord()
        )

    def reset(self):
        self.today_record = DayRecord()
        self._save_data()

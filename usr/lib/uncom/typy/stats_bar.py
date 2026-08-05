from gi.repository import Gtk

from performance_stats_ui import PerformanceStatsUI
from performance_stats import PerformanceStats
from daily_goal import DailyGoal
from daily_goal_ui import DailyGoalUI
from app_settings import get_app_settings

app_settings = get_app_settings()


class StatsBar(Gtk.Box):
    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=32, **kwargs)

        self.performance_stats = PerformanceStats()
        self.daily_goal = DailyGoal()

        self._build_ui()

        app_settings.connect(
            "notify::daily-goal",
            lambda obj, _pspec: self.set_daily_goal_minutes(obj.props.daily_goal),
        )
        self.daily_goal.connect("goal-reached", self._on_goal_reached)
        self.performance_stats.connect("new-best-wpm", self._on_new_best_wpm)

    def _on_goal_reached(self, obj):
        print(
            f"Goal reached! {self.daily_goal.record.strings_completed} strings, "
            f"{self.daily_goal.record.chars_typed} chars, "
            f"avg {self.daily_goal.record.avg_wpm:.0f}wpm / {self.daily_goal.record.avg_accuracy:.0f}%"
        )

    def _on_new_best_wpm(self, obj, wpm: float):
        self.performance_stats_ui.flash_new_best()

    def set_daily_goal_minutes(self, minutes: int):
        self.daily_goal.set_goal(minutes)
        self.daily_goal_ui.update(
            self.daily_goal.record.goal_in_minutes,
            self.daily_goal.get_progress_in_fractions(),
        )
        self.daily_goal_ui.update_streak(self.daily_goal.get_streak())

    def reset_daily_progress(self):
        self.daily_goal.reset_progress()
        self.daily_goal_ui.update(
            self.daily_goal.record.goal_in_minutes,
            self.daily_goal.get_progress_in_fractions(),
        )

    def update_performance_stats(self, string_length: int):
        result = self.performance_stats.update_and_save_averages(string_length)
        self.performance_stats_ui.update(result)
        self.daily_goal.record_string(string_length, result.wpm, result.accuracy)

    def update_daily_goal_stats(self, elapsed: float):
        self.daily_goal.tick_progress(elapsed)

        self.daily_goal_ui.update(
            self.daily_goal.record.goal_in_minutes,
            self.daily_goal.get_progress_in_fractions(),
        )
        self.daily_goal_ui.update_streak(self.daily_goal.get_streak())

    def _build_ui(self):

        self.performance_stats_ui = PerformanceStatsUI()
        self.append(self.performance_stats_ui)

        self.daily_goal_ui = DailyGoalUI()
        self.daily_goal_ui.update(
            self.daily_goal.record.goal_in_minutes,
            self.daily_goal.get_progress_in_fractions(),
        )
        self.daily_goal_ui.update_streak(self.daily_goal.get_streak())

        self.append(self.daily_goal_ui)

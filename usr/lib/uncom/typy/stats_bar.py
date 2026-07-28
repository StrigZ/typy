from gi.repository import Gtk

from performance_stats_ui import PerformanceStatsUI
from performance_stats import PerformanceStats
from daily_goal import DailyGoal
from daily_goal_ui import DailyGoalUI


class StatsBar(Gtk.Box):
    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=16, **kwargs)

        self._performance_stats = PerformanceStats()
        self._daily_goal = DailyGoal()

        self._build_ui()

    def set_daily_goal_minutes(self, minutes: int):
        self._daily_goal.set_goal(minutes)
        self.daily_goal_ui.update(
            self._daily_goal.get_goal_in_minutes(),
            self._daily_goal.get_progress_in_fractions(),
        )

    def reset_daily_progress(self):
        self._daily_goal.reset_daily_progress()
        self.daily_goal_ui.update(
            self._daily_goal.get_goal_in_minutes(),
            self._daily_goal.get_progress_in_fractions(),
        )

    def reset_current_string_counters(self):
        self._performance_stats.start_new_string()

    def record_keystroke(self, is_correct: bool):
        self._performance_stats.record_keystroke(is_correct)

    def update_performance_stats(self, string_length: int):
        self.performance_stats_ui.update(
            self._performance_stats.get_current_wpm(string_length),
            self._performance_stats.get_current_accuracy(),
        )

        self._performance_stats.update_and_save_averages(string_length)
        self._performance_stats.start_new_string()

    def update_daily_goal_stats(self, elapsed: float):
        self._daily_goal.increment(elapsed)

        self.daily_goal_ui.update(
            self._daily_goal.get_goal_in_minutes(),
            self._daily_goal.get_progress_in_fractions(),
        )

    def _build_ui(self):

        self.performance_stats_ui = PerformanceStatsUI()
        self.append(self.performance_stats_ui)

        self.daily_goal_ui = DailyGoalUI()
        self.daily_goal_ui.update(
            self._daily_goal.get_goal_in_minutes(),
            self._daily_goal.get_progress_in_fractions(),
        )
        self.append(self.daily_goal_ui)

from gi.repository import Gtk

from performance_stats_ui import PerformanceStatsUI
from performance_stats import PerformanceStats
from daily_goal import DailyGoal
from daily_goal_ui import DailyGoalUI


class StatsBar(Gtk.Box):
    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=32, **kwargs)

        self.performance_stats = PerformanceStats()
        self.daily_goal = DailyGoal()

        self._build_ui()

    def set_daily_goal_minutes(self, minutes: int):
        self.daily_goal.set_goal(minutes)
        self.daily_goal_ui.update(
            self.daily_goal.goal_in_minutes,
            self.daily_goal.get_progress_in_fractions(),
        )

    def reset_daily_progress(self):
        self.daily_goal.reset_daily_progress()
        self.daily_goal_ui.update(
            self.daily_goal.goal_in_minutes,
            self.daily_goal.get_progress_in_fractions(),
        )

    def update_performance_stats(self, string_length: int):
        self.performance_stats_ui.update(
            self.performance_stats.get_current_wpm(string_length),
            self.performance_stats.get_current_accuracy(),
        )

        self.performance_stats.update_and_save_averages(string_length)

    def update_daily_goal_stats(self, elapsed: float):
        self.daily_goal.increment(elapsed)

        self.daily_goal_ui.update(
            self.daily_goal.goal_in_minutes,
            self.daily_goal.get_progress_in_fractions(),
        )

    def _build_ui(self):

        self.performance_stats_ui = PerformanceStatsUI()
        self.append(self.performance_stats_ui)

        self.daily_goal_ui = DailyGoalUI()
        self.daily_goal_ui.update(
            self.daily_goal.goal_in_minutes,
            self.daily_goal.get_progress_in_fractions(),
        )
        self.append(self.daily_goal_ui)

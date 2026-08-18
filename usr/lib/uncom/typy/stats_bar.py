from app_settings import get_app_settings
from char_stats import CharStats
from current_key_stats_ui import CurrentKeyStatsUI
from daily_goal import DailyGoal
from daily_goal_ui import DailyGoalUI
from daily_stats import DailyStats
from gi.repository import Gtk
from learning_progress import LearningProgress
from learning_progress_ui import LearningProgressUI
from performance_stats import PerformanceStats
from performance_stats_ui import PerformanceStatsUI

app_settings = get_app_settings()


class StatsBar(Gtk.Box):
    def __init__(
        self, learning_progress: LearningProgress, char_stats: CharStats, **kwargs
    ):
        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            valign=Gtk.Align.CENTER,
            spacing=32,
            **kwargs,
        )

        self.learning_progress = learning_progress
        self.char_stats = char_stats
        self.performance_stats = PerformanceStats()
        self.daily_stats = DailyStats()
        self.daily_goal = DailyGoal()

        self._build_ui()

        app_settings.connect("notify::daily-goal", self.on_daily_goal_change)
        app_settings.connect("notify::string-language", self._on_language_change)
        app_settings.connect("notify::typing-mode", self._on_typing_mode_change)
        app_settings.connect("notify::desired-wpm", self._on_desired_wpm_change)
        self.performance_stats.connect("new-best-wpm", self.on_new_best_wpm)

    def on_new_best_wpm(self, obj, wpm: float):
        self.performance_stats_ui.flash_new_best()

    def on_daily_goal_change(self, obj, _pspec):
        self.daily_goal_ui.update(
            app_settings.daily_goal, self.daily_goal.get_progress_in_fractions()
        )

    def _on_language_change(self, obj, _pspec):
        self.update_learning_stats()

    def _on_typing_mode_change(self, obj, _pspec):
        new_mode = obj.props.typing_mode

        self.current_key_stats_ui.set_visible(new_mode == "learning")
        self.learning_progress_ui.set_visible(new_mode == "learning")
        self.performance_stats_ui.set_visible(new_mode != "learning")

    def _on_desired_wpm_change(self, obj, _pspec):
        self.update_learning_stats()

    def update_learning_stats(self):

        curr_learning_char = self.learning_progress.get_current_learning_char()
        self.learning_progress_ui.update(
            curr_learning_char,
            self.learning_progress.get_active_chars(),
            self.learning_progress.get_needs_improvement(),
            self.learning_progress.get_all_proficiencies(),
        )
        self.current_key_stats_ui.update(
            curr_learning_char,
            self.char_stats.peek_stat(curr_learning_char.lower()),
        )

    def reset_daily_progress(self):
        self.daily_goal.reset()
        self.daily_goal_ui.update(
            app_settings.daily_goal,
            self.daily_goal.get_progress_in_fractions(),
        )

    def update_stats(self, string_length: int):
        result = self.performance_stats.update_and_save_averages(string_length)
        self.performance_stats_ui.update(result)
        self.daily_stats.record_string(string_length, result.wpm, result.accuracy)

    def update_daily_goal(self, elapsed: float):
        self.daily_goal.tick_progress(elapsed)

        self.daily_goal_ui.update(
            app_settings.daily_goal,
            self.daily_goal.get_progress_in_fractions(),
        )
        self.daily_goal_ui.update_streak(self.daily_goal.get_streak())

    def _build_ui(self):
        typing_mode = app_settings.typing_mode

        curr_learning_char = self.learning_progress.get_current_learning_char()
        self.current_key_stats_ui = CurrentKeyStatsUI()
        self.current_key_stats_ui.update(
            curr_learning_char,
            self.char_stats.peek_stat(curr_learning_char.lower()),
        )
        self.current_key_stats_ui.set_visible(typing_mode == "learning")
        self.append(self.current_key_stats_ui)

        self.performance_stats_ui = PerformanceStatsUI()
        self.performance_stats_ui.set_visible(typing_mode != "learning")
        self.append(self.performance_stats_ui)

        self.learning_progress_ui = LearningProgressUI()
        self.learning_progress_ui.update(
            curr_learning_char,
            self.learning_progress.get_active_chars(),
            self.learning_progress.get_needs_improvement(),
            self.learning_progress.get_all_proficiencies(),
        )
        self.learning_progress_ui.set_visible(typing_mode == "learning")
        self.append(self.learning_progress_ui)

        self.daily_goal_ui = DailyGoalUI()
        self.daily_goal_ui.update(
            app_settings.daily_goal,
            self.daily_goal.get_progress_in_fractions(),
        )
        self.daily_goal_ui.update_streak(self.daily_goal.get_streak())
        self.append(self.daily_goal_ui)

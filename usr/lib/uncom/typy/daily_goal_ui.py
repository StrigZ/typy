from gi.repository import Gtk
from constants import _


class DailyGoalUI(Gtk.Box):
    def __init__(self, **kwargs):
        super().__init__(
            css_classes=["daily-goal"],
            orientation=Gtk.Orientation.HORIZONTAL,
            hexpand=True,
            spacing=16,
            **kwargs,
        )

        self._build_ui()

    def update(self, goal_in_minutes: int, progress_in_fractions: float):
        is_reached = progress_in_fractions >= 1.0

        self.goal_label.set_text(f"{goal_in_minutes}min")
        self.progress_label.set_text(f"{round(progress_in_fractions * 100)}%/")

        self.progress_bar.set_fraction(min(progress_in_fractions, 1.0))

        if is_reached:
            self.progress_bar.add_css_class("goal-reached")
        else:
            self.progress_bar.remove_css_class("goal-reached")

        self.checkmark_label.set_visible(is_reached)

    def update_streak(self, streak: int):
        self.streak_count_label.set_text(str(streak))

        if streak > 0:
            self.streak_label.add_css_class("lit")
        else:
            self.streak_label.remove_css_class("lit")

    def _build_ui(self):
        streak_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            valign=Gtk.Align.CENTER,
            spacing=4,
        )

        self.streak_label = Gtk.Label(label="🔥")
        self.streak_label.add_css_class("streak-flame")
        streak_box.append(self.streak_label)

        self.streak_count_label = Gtk.Label(valign=Gtk.Align.CENTER)
        streak_box.append(self.streak_count_label)
        self.append(streak_box)

        title_label = Gtk.Label()
        title_label.set_text(_("Daily goal"))
        self.append(title_label)

        content_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            valign=Gtk.Align.CENTER,
            hexpand=True,
            spacing=8,
        )
        self.append(content_box)

        progress_box = Gtk.Box(css_classes=["dim-label"])
        content_box.append(progress_box)

        self.progress_label = Gtk.Label(valign=Gtk.Align.CENTER)
        progress_box.append(self.progress_label)

        self.goal_label = Gtk.Label(valign=Gtk.Align.CENTER)
        progress_box.append(self.goal_label)

        self.progress_bar = Gtk.ProgressBar(
            valign=Gtk.Align.CENTER,
            hexpand=True,
        )
        content_box.append(self.progress_bar)

        self.checkmark_label = Gtk.Label(label="✓")
        self.checkmark_label.add_css_class("checkmark")
        self.checkmark_label.set_visible(False)
        content_box.append(self.checkmark_label)

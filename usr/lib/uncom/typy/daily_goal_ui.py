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

    def update_progress(
        self,
        progress: float,
    ):
        self.progress_label.set_text(f"{round(progress * 100)}%/")
        self.progress_bar.set_fraction(progress)

    def update_goal(self, goal_in_minutes: int, progress_in_fractions: float):
        self.goal_label.set_text(f"{goal_in_minutes}min")
        self.update_progress(progress_in_fractions)

    def _build_ui(self):
        title_label = Gtk.Label()
        title_label.set_text(_("Daily goal"))
        self.append(title_label)

        content_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            valign=Gtk.Align.CENTER,
            hexpand=True,
            spacing=4,
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

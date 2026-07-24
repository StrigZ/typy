from gi.repository import Gtk

from constants import _


class PerfomanceStatsUI(Gtk.Box):
    def __init__(self, **kwargs):
        super().__init__(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=20,
            css_classes=["perfomance-stats"],
            **kwargs,
        )

        self.wpm_label = Gtk.Label()
        self.accuracy_label = Gtk.Label()

        self.append(self.wpm_label)
        self.append(self.accuracy_label)

    def update(self, wpm: float, accuracy: float):
        self.wpm_label.set_text(_("{:.0f} WPM").format(wpm))
        self.accuracy_label.set_text(_("{:.0f}% accuracy").format(accuracy))

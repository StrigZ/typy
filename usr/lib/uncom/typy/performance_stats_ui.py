from gi.repository import Gtk, GLib

from constants import _


class PerformanceStatsUI(Gtk.Box):
    def __init__(self, **kwargs):
        super().__init__(
            css_classes=["performance-stats"],
            orientation=Gtk.Orientation.HORIZONTAL,
            halign=Gtk.Align.CENTER,
            spacing=32,
            **kwargs,
        )

        self._build_ui()

    def flash_new_best(self):
        self.new_best_label.add_css_class("visible")
        GLib.timeout_add(2000, self._hide_new_best)

    def _hide_new_best(self):
        self.new_best_label.remove_css_class("visible")
        return False

    def update(self, wpm: float, accuracy: float):
        self.wpm_value_label.set_text(("{:.0f}wpm").format(wpm))
        self.accuracy_value_label.set_text(("{:.0f}%").format(accuracy))

    def _build_ui(self):
        self.wpm_value_label = Gtk.Label(
            label="0wpm",
        )
        wpm_box = self._build_stat_box(
            title_label_text=_("Speed"), value_label=self.wpm_value_label
        )
        self.new_best_label = Gtk.Label(label=_("NEW BEST!"))
        self.new_best_label.add_css_class("new-best")
        wpm_box.append(self.new_best_label)
        self.append(wpm_box)

        self.accuracy_value_label = Gtk.Label(
            label="0%",
        )
        accuracy_box = self._build_stat_box(
            title_label_text=_("Accuracy"), value_label=self.accuracy_value_label
        )
        self.append(accuracy_box)

    def _build_stat_box(self, title_label_text: str, value_label: Gtk.Label):
        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8,
            halign=Gtk.Align.CENTER,
        )
        title_label = Gtk.Label(label=title_label_text, css_classes=["dim-label"])

        box.append(title_label)
        box.append(value_label)
        return box

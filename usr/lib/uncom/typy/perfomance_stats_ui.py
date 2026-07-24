from gi.repository import Gtk

from constants import _


class PerfomanceStatsUI(Gtk.Box):
    def __init__(self, **kwargs):
        super().__init__(
            css_classes=["perfomance-stats"],
            orientation=Gtk.Orientation.HORIZONTAL,
            halign=Gtk.Align.CENTER,
            spacing=25,
            **kwargs,
        )

        self._build_ui()

    def update(self, wpm: float, accuracy: float):
        self.wpm_value_label.set_text(("{:.0f}wpm").format(wpm))
        self.accuracy_value_label.set_text(("{:.0f}%").format(accuracy))

    def _build_ui(self):
        self.wpm_value_label = Gtk.Label(
            label="0wpm",
        )
        self._build_stat_box(
            title_label_text=_("Speed"), value_label=self.wpm_value_label
        )

        self.accuracy_value_label = Gtk.Label(
            label="0%",
        )
        self._build_stat_box(
            title_label_text=_("Accuracy"), value_label=self.accuracy_value_label
        )

    def _build_stat_box(self, title_label_text: str, value_label: Gtk.Label):
        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=15,
            halign=Gtk.Align.CENTER,
        )
        title_label = Gtk.Label(label=title_label_text, css_classes=["dim-label"])

        box.append(title_label)
        box.append(value_label)
        self.append(box)

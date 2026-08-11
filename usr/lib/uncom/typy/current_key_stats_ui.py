from gi.repository import Gtk
from constants import _, CURRENT_KEY_DISPLAY_MIN_SAMPLES
from char_stats import CharStat


class CurrentKeyStatsUI(Gtk.Box):
    def __init__(self, **kwargs):
        super().__init__(
            orientation=Gtk.Orientation.HORIZONTAL,
            halign=Gtk.Align.CENTER,
            spacing=32,
            **kwargs,
        )

        self._build_ui()

    def update(self, char: str, char_stat: CharStat | None):
        self.current_key_label.set_label(char)
        if char_stat and char_stat.get("samples", 0) > CURRENT_KEY_DISPLAY_MIN_SAMPLES:
            self.wpm_value_label.set_label(
                f"{convert_avg_time_to_wpm(char_stat['avg_time']):0.1f}wpm"
            )
            self.accuracy_value_label.set_label(f"{get_accuracy(char_stat):0.1f}%")
        else:
            self.wpm_value_label.set_label("Gathering data…")
            self.accuracy_value_label.set_label("Gathering data…")

    def _build_ui(self):
        def build_stat_box(title_label_text: str, value_label: Gtk.Label):
            box = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL,
                spacing=8,
                halign=Gtk.Align.CENTER,
            )
            title_label = Gtk.Label(label=title_label_text, css_classes=["dim-label"])

            box.append(title_label)
            box.append(value_label)
            return box

        self.current_key_label = Gtk.Label()
        current_key_box = build_stat_box(_("Current key"), self.current_key_label)
        self.append(current_key_box)

        self.wpm_value_label = Gtk.Label()
        wpm_box = build_stat_box(
            title_label_text=_("Speed"), value_label=self.wpm_value_label
        )

        self.append(wpm_box)

        self.accuracy_value_label = Gtk.Label()
        accuracy_box = build_stat_box(
            title_label_text=_("Accuracy"), value_label=self.accuracy_value_label
        )
        self.append(accuracy_box)


def get_accuracy(char_stat: CharStat) -> float:
    return (char_stat["samples"] / char_stat["attempts"]) * 100


def convert_avg_time_to_wpm(avg_time: float):
    return 12 / avg_time

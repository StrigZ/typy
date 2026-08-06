from gi.repository import Adw, Gtk
from daily_stats import DailyStats
from performance_stats import PerformanceStats
from constants import _


class StatsDialog(Adw.Dialog):
    def __init__(
        self, daily_stats: DailyStats, performance_stats: PerformanceStats, **kwargs
    ):
        super().__init__(can_close=True, title="Stats", **kwargs)
        self.daily_stats = daily_stats
        self.performans_stats = performance_stats

        header_bar = Adw.HeaderBar(title_widget=Adw.WindowTitle(title=_("Stats")))
        content_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=4,
            margin_start=24,
            margin_end=24,
        )

        stack = Gtk.Stack()
        switcher = Gtk.StackSwitcher(
            stack=stack,
        )
        content_box.append(switcher)
        content_box.append(stack)

        toolbar_view = Adw.ToolbarView(
            content=content_box, top_bar_style=Adw.ToolbarStyle.FLAT
        )
        toolbar_view.add_top_bar(header_bar)
        self.set_child(toolbar_view)

        self._build_ui()

        stack.add_titled(self.today_stats_box, "today", _("Today"))
        stack.add_titled(self.all_time_stats_box, "all_time", _("All time"))

    def _build_ui(self):
        self._build_today_stats()
        self._build_all_time_stats()

    def _build_today_stats(self):
        self.today_stats_box = self._build_stats_box(self.daily_stats.today)

    def _build_all_time_stats(self):
        self.all_time_stats_box = self._build_stats_box(
            self.performans_stats.performance
        )

    def _build_stats_box(self, stats):
        def build_stat_box(title, value_label: Gtk.Label):
            stat_box = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL,
                spacing=8,
                margin_bottom=4,
                margin_top=4,
                margin_end=4,
                margin_start=4,
                hexpand=True,
            )
            value_label.add_css_class("title-1")
            value_label.set_width_chars(10)
            value_label.set_justify(Gtk.Justification.CENTER)

            title_label = Gtk.Label(label=title, css_classes=["dim-label", "caption"])
            stat_box.append(title_label)
            stat_box.append(value_label)

            return stat_box

        stats_box = Gtk.Box(
            spacing=8,
            margin_bottom=24,
            margin_top=24,
            margin_end=24,
            margin_start=24,
        )
        size_group = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)

        labels = [
            (_("Average speed"), f"{stats.avg_wpm:.1f}wpm"),
            (_("Average accuracy"), f"{stats.avg_accuracy:.1f}%"),
            (_("Characters typed"), str(stats.chars_typed)),
            (_("Strings completed"), str(stats.strings_completed)),
        ]
        for i, (title, value) in enumerate(labels):
            if i > 0:
                stats_box.append(
                    Gtk.Separator(
                        orientation=Gtk.Orientation.VERTICAL,
                        margin_top=12,
                        margin_bottom=12,
                    )
                )
            box = build_stat_box(title, Gtk.Label(label=value))
            size_group.add_widget(box)
            stats_box.append(box)

        return Adw.Clamp(child=stats_box, margin_top=12)


def show_stats(parent_window, daily_stats, performance_stats):
    dialog = StatsDialog(daily_stats, performance_stats)
    dialog.present(parent_window)

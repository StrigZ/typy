from gi.repository import Adw, Gtk

from constants import _

from typing_controller import TypingController


class SettingsDialog(Adw.PreferencesDialog):
    def __init__(self, typing_controller: TypingController, **kwargs):
        super().__init__(**kwargs)
        self._typing_controller = typing_controller

        page = Adw.PreferencesPage()
        self.add(page)

        page.add(self._build_typing_group())
        page.add(self._build_daily_goal_group())
        # page.add(self._build_language_group())

    def _build_typing_group(self) -> Adw.PreferencesGroup:
        group = Adw.PreferencesGroup(title=_("Typing"))

        reset_row = Adw.ActionRow(title=_("Reset stats"))
        reset_button = Gtk.Button(label=_("Reset"), valign=Gtk.Align.CENTER)
        reset_button.connect(
            "clicked", lambda *a: self._typing_controller._char_stats.reset_data()
        )
        reset_row.add_suffix(reset_button)
        group.add(reset_row)

        return group

    def _build_daily_goal_group(self) -> Adw.PreferencesGroup:
        group = Adw.PreferencesGroup(title=_("Daily goal"))

        stats_bar = self._typing_controller._stats_bar

        set_goal_row = Adw.SpinRow.new_with_range(5, 240, 5)
        set_goal_row.set_title(_("Minutes per day"))
        set_goal_row.set_value(stats_bar._daily_goal.goal_in_minutes)
        set_goal_row.connect(
            "notify::value",
            lambda row, param: stats_bar.set_daily_goal_minutes(int(row.get_value())),
        )
        group.add(set_goal_row)

        reset_row = Adw.ActionRow(title=_("Reset daily progress"))
        reset_button = Gtk.Button(label=_("Reset"), valign=Gtk.Align.CENTER)
        reset_button.connect(
            "clicked",
            lambda *a: stats_bar.reset_daily_progress(),
        )
        reset_row.add_suffix(reset_button)
        group.add(reset_row)

        return group


def show_settings(parent_window, typing_controller):
    dialog = SettingsDialog(typing_controller)
    dialog.present(parent_window)

from gi.repository import Adw, Gtk

from constants import _

from typing_controller import TypingController
from app_settings import get_app_settings

app_settings = get_app_settings()


class SettingsDialog(Adw.PreferencesDialog):
    def __init__(self, typing_controller: TypingController, **kwargs):
        super().__init__(**kwargs)
        self._typing_controller = typing_controller

        page = Adw.PreferencesPage()
        self.add(page)

        page.add(self._build_typing_group())
        page.add(self._build_daily_goal_group())
        page.add(self._build_stats_group())
        # page.add(self._build_language_group())

    def _build_stats_group(self) -> Adw.PreferencesGroup:
        group = Adw.PreferencesGroup(title=_("Stats"))

        reset_row = Adw.ActionRow(title=_("Reset stats"))
        reset_button = Gtk.Button(label=_("Reset"), valign=Gtk.Align.CENTER)
        reset_button.connect(
            "clicked", lambda *a: self._typing_controller.char_stats.reset_data()
        )
        reset_row.add_suffix(reset_button)
        group.add(reset_row)

        return group

    def _build_daily_goal_group(self) -> Adw.PreferencesGroup:
        group = Adw.PreferencesGroup(title=_("Daily goal"))

        stats_bar = self._typing_controller.stats_bar

        set_goal_row = Adw.SpinRow.new_with_range(5, 240, 5)
        set_goal_row.set_title(_("Minutes per day"))
        set_goal_row.set_value(stats_bar.daily_goal.goal_in_minutes)
        set_goal_row.connect(
            "notify::value",
            lambda row, param: setattr(
                app_settings, "daily_goal", int(row.get_value())
            ),
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

    def _build_typing_group(self) -> Adw.PreferencesGroup:
        group = Adw.PreferencesGroup(title=_("Typing"))

        string_length_row = Adw.SpinRow.new_with_range(50, 150, 10)
        string_length_row.set_title(_("String length"))
        string_length_row.set_value(app_settings.string_length)
        string_length_row.connect(
            "notify::value",
            lambda row, param: setattr(
                app_settings, "string_length", int(row.get_value())
            ),
        )
        group.add(string_length_row)

        language_list = Gtk.StringList(strings=["ru", "en"])
        selected_index = language_list.find(app_settings.string_language)

        # Prevent crashing if language is not found
        if selected_index == Gtk.INVALID_LIST_POSITION:
            selected_index = 0

        string_language_row = Adw.ComboRow(
            model=language_list,
            selected=language_list.find(app_settings.string_language),
        )
        string_language_row.set_title(_("Language"))

        def on_language_changed(combo_row, _pspec):
            selected = combo_row.get_selected_item().get_string()
            app_settings.string_language = selected

        string_language_row.connect("notify::selected", on_language_changed)
        group.add(string_language_row)

        return group


def show_settings(parent_window, typing_controller):
    dialog = SettingsDialog(typing_controller)
    dialog.present(parent_window)

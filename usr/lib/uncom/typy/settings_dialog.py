from app_settings import get_app_settings
from constants import _
from gi.repository import Adw, GLib, Gtk
from typing_controller import TypingController

app_settings = get_app_settings()

language_name_to_code_map = {"Русский": "ru", "English": "en"}
language_code_to_name_map = {
    code: name for name, code in language_name_to_code_map.items()
}

TYPING_MODE_CODES = ["freeform", "adaptive", "learning"]
typing_mode_name_to_code = {
    _("Freeform"): "freeform",
    _("Adaptive"): "adaptive",
    _("Learning"): "learning",
}
typing_mode_code_to_name = {v: k for k, v in typing_mode_name_to_code.items()}


class SettingsDialog(Adw.PreferencesDialog):
    def __init__(self, typing_controller: TypingController, **kwargs):
        super().__init__(**kwargs)
        self._typing_controller = typing_controller

        # apply slider values,
        # if settings window closes
        self._pending_flushes = []
        self.connect("closed", lambda *a: self._flush_all())

        page = Adw.PreferencesPage()
        self.add(page)

        page.add(self._build_typing_group())
        page.add(self._build_daily_goal_group())
        page.add(self._build_reset_group())

    def _flush_all(self):
        for flush in self._pending_flushes:
            flush()

    def _build_reset_group(self) -> Adw.PreferencesGroup:
        def build_reset_row(title: str, callback):
            reset_row = Adw.ActionRow(title=title)
            reset_button = Gtk.Button(label=_("Reset"), valign=Gtk.Align.CENTER)
            reset_button.connect("clicked", lambda *a: callback())
            reset_row.add_suffix(reset_button)

            return reset_row

        stats_bar = self._typing_controller.stats_bar
        group = Adw.PreferencesGroup(title=_("Danger zone"))

        def on_char_stat_reset():
            self._typing_controller.char_stats.reset_data()
            self._typing_controller.learning_progress.reset()
            self._typing_controller.stats_bar.update_learning_stats()

        reset_char_stats_row = build_reset_row(
            _("Reset char stats"), on_char_stat_reset
        )
        group.add(reset_char_stats_row)

        reset_today_stats_row = build_reset_row(
            _("Reset today stats"), stats_bar.daily_stats.reset
        )
        group.add(reset_today_stats_row)

        reset_today_progress_row = build_reset_row(
            _("Reset today progress"), stats_bar.reset_daily_progress
        )
        group.add(reset_today_progress_row)

        reset_all_time_stats_row = build_reset_row(
            _("Reset all time stats"), stats_bar.performance_stats.reset_data
        )
        group.add(reset_all_time_stats_row)

        return group

    def _build_daily_goal_group(self) -> Adw.PreferencesGroup:
        group = Adw.PreferencesGroup(title=_("Daily goal"))

        set_goal_row = Adw.SpinRow.new_with_range(5, 240, 5)
        set_goal_row.set_title(_("Minutes per day"))
        set_goal_row.set_value(app_settings.daily_goal)
        set_goal_row.connect(
            "notify::value",
            lambda row, param: setattr(
                app_settings, "daily_goal", int(row.get_value())
            ),
        )
        group.add(set_goal_row)

        return group

    def _build_typing_group(self) -> Adw.PreferencesGroup:
        group = Adw.PreferencesGroup(title=_("Typing"))

        def on_string_length_change(new_value):
            app_settings.string_length = new_value

        string_length_row = self.create_slider_row(
            _("String length"),
            app_settings.string_length,
            50,
            150,
            10,
            on_string_length_change,
            "ch",
        )
        group.add(string_length_row)

        string_language_row = self.create_dropdown_row(
            list(language_name_to_code_map.keys()),
            language_code_to_name_map[app_settings.string_language],
            _("Language"),
        )

        def on_language_changed(combo_row, _pspec):
            selected_lang = combo_row.get_selected_item().get_string()
            app_settings.string_language = language_name_to_code_map[selected_lang]

        string_language_row.connect("notify::selected", on_language_changed)
        group.add(string_language_row)

        typing_mode_row = self.create_dropdown_row(
            list(typing_mode_name_to_code.keys()),
            typing_mode_code_to_name[app_settings.typing_mode],
            _("Mode"),
        )

        def on_typing_mode_change(combo_row, _pspec):
            selected = combo_row.get_selected_item().get_string()
            app_settings.typing_mode = typing_mode_name_to_code[selected]

        typing_mode_row.connect("notify::selected", on_typing_mode_change)
        group.add(typing_mode_row)

        def on_desired_wpm_change(new_value):
            app_settings.desired_wpm = new_value

        desired_wpm_slider_row = self.create_slider_row(
            _("Desired WPM"),
            app_settings.desired_wpm,
            30,
            200,
            5,
            on_desired_wpm_change,
            "wpm",
        )
        desired_wpm_slider_row.set_visible(app_settings.typing_mode == "learning")
        app_settings.connect(
            "notify::typing-mode",
            lambda obj, _pspec: desired_wpm_slider_row.set_visible(
                obj.props.typing_mode == "learning"
            ),
        )

        group.add(desired_wpm_slider_row)

        return group

    def create_slider_row(
        self, title, value, min, max, step, on_change, label_suffix=None
    ):
        adjustment = Gtk.Adjustment(
            value=value, lower=min, upper=max, step_increment=step
        )
        scale = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL,
            adjustment=adjustment,
            hexpand=True,
            valign=Gtk.Align.CENTER,
            round_digits=0,
        )

        value_label = Gtk.Label(
            label=(f"{value:0.0f}{label_suffix if label_suffix else ''}"),
            width_chars=8,
        )

        _debounce_id = None
        _pending_value = None

        def on_slider_changed(adj):
            nonlocal _debounce_id, _pending_value
            raw = adj.get_value()
            snapped = round(raw / step) * step
            value_label.set_label(
                f"{snapped:0.0f}{label_suffix if label_suffix else ''}"
            )
            _pending_value = snapped

            if _debounce_id is not None:
                GLib.source_remove(_debounce_id)

            def commit():
                nonlocal _debounce_id
                _debounce_id = None
                on_change(_pending_value)
                return False

            _debounce_id = GLib.timeout_add(300, commit)

        def flush():
            nonlocal _debounce_id
            if _debounce_id is not None:
                GLib.source_remove(_debounce_id)
                _debounce_id = None
                on_change(_pending_value)

        adjustment.connect("value-changed", on_slider_changed)
        self._pending_flushes.append(flush)

        row = Adw.ActionRow(title=title, hexpand=True)
        row.add_suffix(scale)
        row.add_suffix(value_label)

        return row

    def create_dropdown_row(self, options, selected_value, title):
        options_list = Gtk.StringList(strings=options)

        selected_index = options_list.find(selected_value)

        if selected_index == Gtk.INVALID_LIST_POSITION:
            selected_index = 0

        return Adw.ComboRow(
            model=options_list,
            title=title,
            selected=selected_index,
        )


def show_settings(parent_window, typing_controller):
    dialog = SettingsDialog(typing_controller)
    dialog.present(parent_window)

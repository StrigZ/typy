#!/usr/bin/python3

import argparse
import gettext
import os
import random
import sys
from collections import defaultdict
import json

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gdk, GLib, Gtk

# --- Localization ---
# (this is a global path, will not work during local testing)
TEXT_DOMAIN = "typy"
gettext.bindtextdomain(TEXT_DOMAIN, "/usr/share/locale")
gettext.textdomain(TEXT_DOMAIN)
_ = gettext.gettext

# --- Paths & constants ---
APP_DIR = os.path.dirname(os.path.abspath(__file__))
STYLE_CSS = os.path.join(APP_DIR, "style.css")
STATS_FILE = os.path.join(GLib.get_user_data_dir(), "typy", "stats.json")

COMMON_WORDS = ["the", "quick", "brown", "fox", "jumps", "over", "lazy", "dog"]


def load_missed_char_counts():
    try:
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return defaultdict(int, data)
    except (FileNotFoundError, json.JSONDecodeError):
        return defaultdict(int)


def save_missed_char_counts(counts):
    ensure_folder_exists(os.path.dirname(STATS_FILE))
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(counts, f)


def reset_missed_char_counts():
    missed_char_counts.clear()
    if os.path.exists(STATS_FILE):
        os.remove(STATS_FILE)


missed_char_counts = load_missed_char_counts()


def generate_string(word_list, missed_char_counts, word_count=5):
    """Pick word_count words, weighted toward ones containing
    characters the user has historically mistyped."""

    def word_weight(word):
        return 1 + sum(missed_char_counts.get(c, 0) for c in word)

    weights = [word_weight(w) for w in word_list]
    chosen = random.choices(word_list, weights=weights, k=word_count)
    return " ".join(chosen)


def ensure_folder_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


# --- Dialogs ---


def show_completion_popup(window, callback_restart):
    dialog = Gtk.AlertDialog()
    dialog.set_message(_("Finished!"))
    dialog.set_detail(_("You completed the typing test."))
    dialog.set_buttons([_("Restart"), _("Close")])
    dialog.set_default_button(0)  # Restart triggered by Enter
    dialog.set_cancel_button(1)  # Close triggered by Escape

    def on_response(source, result, *_data):
        try:
            button_index = dialog.choose_finish(result)
        except GLib.Error:
            return  # dismissed without a button (e.g. window closed)

        if button_index == 0:
            callback_restart()

    dialog.choose(window, None, on_response)


def show_settings(window):
    dialog = Adw.PreferencesDialog()

    page = Adw.PreferencesPage()
    dialog.add(page)

    group = Adw.PreferencesGroup(title=_("Typing"))
    page.add(group)

    reset_row = Adw.ActionRow(title=_("Reset stats"))
    reset_button = Gtk.Button(label=_("Reset"), valign=Gtk.Align.CENTER)
    reset_button.connect("clicked", lambda *a: reset_missed_char_counts())
    reset_row.add_suffix(reset_button)
    group.add(reset_row)

    dialog.present(window)


# --- Main window ---


class WindowMain(Gtk.ApplicationWindow):
    def __init__(self, **kargs):
        super().__init__(**kargs, title=_("typy"))
        self.set_resizable(False)
        self.set_default_size(500, 300)

        self.missed_keys_indices = set()
        self.string_to_type = self.generate_string_to_type()
        self.string_to_type_pointer = 0

        self.load_css()
        self._build_ui()
        self.update_string_to_type_highlights()

        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self.on_key_pressed)
        self.add_controller(key_controller)

    def _build_ui(self):
        main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main.props.margin_start = 25
        main.props.margin_end = 25
        main.props.margin_top = 25
        main.props.margin_bottom = 25
        self.set_child(main)

        self.visual_container = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=10
        )
        main.append(self.visual_container)

        string_to_type_label = Gtk.Label()
        string_to_type_label.set_text(self.string_to_type)
        string_to_type_label.add_css_class("string-to-type")
        string_to_type_label.props.wrap = True
        string_to_type_label.props.justify = Gtk.Justification.CENTER
        self.string_to_type_label = string_to_type_label
        main.append(self.string_to_type_label)

        key_display_label = Gtk.Label()
        key_display_label.set_text("Press a key...")
        key_display_label.add_css_class("key-display")
        self.key_display_label = key_display_label
        main.append(self.key_display_label)

        settings_button = Gtk.Button(label=_("Settings"))
        settings_button.connect("clicked", lambda *a: show_settings(self))
        main.append(settings_button)

    def reset_stats(self):
        reset_missed_char_counts()
        self.restart()

    def load_css(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(STYLE_CSS)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def generate_string_to_type(self):
        return generate_string(COMMON_WORDS, missed_char_counts)

    def update_string_to_type_highlights(self):
        parts = []
        for i, ch in enumerate(self.string_to_type):
            escaped = GLib.markup_escape_text(ch)
            if i < self.string_to_type_pointer:
                color = "#e53935" if i in self.missed_keys_indices else "#4caf50"
            else:
                color = "#888888"
            parts.append(f'<span foreground="{color}">{escaped}</span>')

        self.string_to_type_label.set_markup("".join(parts))

    def on_key_pressed(self, controller, keyval, keycode, state):
        if self.string_to_type_pointer >= len(self.string_to_type):
            return True

        unicode_val = Gdk.keyval_to_unicode(keyval)
        if not unicode_val:
            return True  # ignore non-printable keys (Shift, Escape, arrows, etc.)

        char = chr(unicode_val)
        self.key_display_label.set_text(char)

        curr_char = self.string_to_type[self.string_to_type_pointer]

        if curr_char == char:
            self.string_to_type_pointer += 1
            if self.string_to_type_pointer == len(self.string_to_type):
                show_completion_popup(self, self.restart)
        else:
            self.missed_keys_indices.add(self.string_to_type_pointer)
            missed_char_counts[self.string_to_type[self.string_to_type_pointer]] += 1

        self.update_string_to_type_highlights()
        return True

    def restart(self):
        save_missed_char_counts(missed_char_counts)
        self.string_to_type = self.generate_string_to_type()
        self.string_to_type_pointer = 0
        self.missed_keys_indices.clear()
        self.key_display_label.set_text("Press a key...")
        self.update_string_to_type_highlights()
        print(missed_char_counts)


# --- Application ---


class Application(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.uncom.typy")
        GLib.set_application_name(_("typy"))
        self.connect("shutdown", lambda *a: save_missed_char_counts(missed_char_counts))

    def do_activate(self):
        window = WindowMain(application=self)
        window.present()


# --- CLI entry point ---


def parse_args():
    parser = argparse.ArgumentParser(
        description="Uncom App Template demonstration application. Can be used via terminal and GUI.",
        epilog="Start without parameters to view help.",
    )
    parser.add_argument(
        "-g",
        "--gui",
        action="store_true",
        help="run with graphical UI, used for desktop sessions",
    )
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("-a", "--option-a", action="store_true", help="some option A")
    group.add_argument("-b", "--option-b", action="store_true", help="some option B")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.option_a:
        print("Option A is given")
    elif args.option_b:
        print("Option B is given")

    if args.gui:
        sys.argv = [sys.argv[0]]  # clear args so GTK doesn't parse them too
        app = Application()
        sys.exit(app.run(sys.argv))
    else:
        print("This application does nothing...")


if __name__ == "__main__":
    main()

#!/usr/bin/python3

import sys
import argparse
import gi
import stat
import subprocess
import os
import string
import random
import re
import shutil
import configparser
import gettext
import threading
import time
from PIL import Image

gi.require_version("Gtk", "4.0")
gi.require_version('Adw', '1')
from gi.repository import GLib, Gtk, Adw, Gdk

# This block is about localization (this is global path, will not work during local testing)
text_domain = "typy"
gettext.bindtextdomain(text_domain, '/usr/share/locale')
gettext.textdomain(text_domain)
_ = gettext.gettext


APP_DIR = os.path.dirname(os.path.abspath(__file__))
STYLE_CSS = os.path.join(APP_DIR, "style.css")

class WindowMain(Gtk.ApplicationWindow):
    def __init__(self, **kargs):
        super().__init__(**kargs, title=_("typy"))
        self.load_css()
        self.set_resizable(False)
        self.set_default_size(500, 300)

        # Common top level container
        main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main.props.margin_start = 25
        main.props.margin_end = 25
        main.props.margin_top = 25
        main.props.margin_bottom = 25
        self.set_child(main)

        # Visual container
        self.visual_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main.append(self.visual_container)

        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self.on_key_pressed)
        self.add_controller(key_controller)



        string_to_type = "test" #TODO: replace with actual string logic
        self.string_to_type = string_to_type
        self.string_to_type_pointer = 0

        self.missed_keys_indices = set()

        string_to_type_label = Gtk.Label()
        string_to_type_label.set_text(self.string_to_type)
        string_to_type_label.add_css_class("string-to-type")
        self.string_to_type_label = string_to_type_label
        main.append(self.string_to_type_label)
        self.update_string_to_type_highlights()

        key_display_label = Gtk.Label()
        key_display_label.set_text("Press a key...")
        key_display_label.add_css_class("key-display")
        self.key_display_label = key_display_label
        main.append(self.key_display_label)

    def load_css(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(STYLE_CSS)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

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

        if (curr_char == char):
            self.string_to_type_pointer += 1
            if self.string_to_type_pointer == len(self.string_to_type):
                show_completion_popup(self, self.restart)
        else:
            self.missed_keys_indices.add(self.string_to_type_pointer)

        self.update_string_to_type_highlights()
        return True

    def restart(self):
        self.string_to_type_pointer = 0
        self.missed_keys_indices.clear()
        self.key_display_label.set_text("Press a key...")
        self.update_string_to_type_highlights()


def _continue_after_message(dialog, callback):
    dialog.destroy()
    callback()

def show_error_message(window, message, callback):
        dialog = Gtk.MessageDialog(
            transient_for=window,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=_("Error"),
            secondary_text=message
        )
        dialog.present()
        dialog.connect("response", lambda *a: _continue_after_message(dialog, callback))

def show_completion_popup(window, callback_restart):
    dialog = Gtk.AlertDialog()
    dialog.set_message(_("Finished!"))
    dialog.set_detail(_("You completed the typing test."))
    dialog.set_buttons([_("Restart"), _("Close")])
    dialog.set_default_button(0)   # Restart triggered by Enter
    dialog.set_cancel_button(1)    # Close triggered by Escape

    def on_response(source, result, *_data):
        try:
            button_index = dialog.choose_finish(result)
        except GLib.Error:
            return  # dialog dismissed without a button (rare, e.g. window closed)

        if button_index == 0:
            callback_restart()

    dialog.choose(window, None, on_response)



class Application(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.uncom.typy")
        GLib.set_application_name(_("typy"))

    def do_activate(self):
        window = WindowMain(application=self)
        window.present()


# Supportive function to make sure path exists
def ensure_folder_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Supportive function to generate random string
def generate_random_string(length=15):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


# Setup optional and mandatory launch arguments for command line
parser = argparse.ArgumentParser(
    description="Uncom App Template demonstration application. Can be used via terminal and GUI.",
    epilog="Start without parameters to view help.")

parser.add_argument('-g', '--gui', action='store_true', help='run with graphical UI, used for desktop sessions')

group = parser.add_mutually_exclusive_group(required=False)
group.add_argument('-a', '--option-a', action='store_true', help='some option A')
group.add_argument('-b', '--option-b', action='store_true', help='some option B')

# Add line below if file path is mandatory argument
# parser.add_argument('file_name', type=str, help="Path to some file")

args = parser.parse_args()

if args.gui: # run in GUI mode

    # clear arguments so GTK will not trigger on them
    sys.argv = [sys.argv[0]]

    if args.option_a:
        print("Option A is given")
    elif args.option_b:
        print("Option B is given")

    app = Application()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)

else: # run in command line mode

    if args.option_a:
        print("Option A is given")
    elif args.option_b:
        print("Option B is given")

    # put any logic here for terminal way of usage
    print ("This application does nothing...")

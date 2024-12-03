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
from gi.repository import GLib, Gtk, Adw

# This block is about localization (this is global path, will not work during local testing)
text_domain = "uncom-app-template"
gettext.bindtextdomain(text_domain, '/usr/share/uncom/uncom-app-template/locale')
gettext.textdomain(text_domain)
_ = gettext.gettext

# Define global links to resources here (this is global path, will not work during local testing)
CUSTOM_IMAGE = "/usr/share/uncom/uncom-app-template/content/image.png"

class WindowMain(Gtk.ApplicationWindow):
    def __init__(self, **kargs):
        super().__init__(**kargs, title=_("Uncom App Template"))
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

        # Message container
        horizontal_message = Gtk.Box(spacing=10)
        main.append(horizontal_message)

        # Buttons container
        horiontal_buttons = Gtk.Box(spacing=10)
        horiontal_buttons.props.margin_top = 25
        main.append(horiontal_buttons)

        # Image (put it in Visual container)
        self.picture = Gtk.Picture.new_for_filename(CUSTOM_IMAGE)
        self.picture.props.vexpand = True
        self.visual_container.append(self.picture)

        # Messages (put it in Message container)
        label_message = Gtk.Label()
        label_message.set_markup(_("Here is some text with <b>different format</b> options."))
        label_message.props.justify = Gtk.Justification.CENTER
        label_message.props.wrap = True
        label_message.props.hexpand = True
        horizontal_message.append(label_message)

        # Left button (put it in Buttons container)
        self.button_l = Gtk.Button.new_with_label(_("Show popup"))
        self.button_l.connect('clicked', self.on_click_show_popup)
        self.button_l.props.hexpand = True
        horiontal_buttons.append(self.button_l)

        # Right button (put it in Buttons container)
        self.button_r = Gtk.Button.new_with_mnemonic(_("Start 3-sec process..."))
        self.button_r.connect('clicked', self.on_click_long_process)
        self.button_r.props.hexpand = True
        horiontal_buttons.append(self.button_r)

    def show_spinner(self):
        self.spinner = Gtk.Spinner()
        self.spinner.props.vexpand = True
        self.visual_container.remove(self.picture)
        self.visual_container.append(self.spinner)
        self.spinner.start()

    def hide_spinner(self):
        self.spinner.stop()
        self.visual_container.remove(self.spinner)
        self.visual_container.append(self.picture)

    def on_click_show_popup(self, _button):
        # Notice, that buttons from main window will be still clickable
        show_success_message(self, _("Dialogue Title"), _("Some message..."), lambda *a: None)

    def on_click_long_process(self, _button):
        self.button_l.set_sensitive(False)
        self.button_r.set_sensitive(False)
        self.show_spinner()

        def on_task_complete():
            self.hide_spinner()
            show_success_message(self, _("Completed"), _("Long process completed successfully."), lambda *a: exit())
        
        def on_task_error():
            self.hide_spinner()
            show_error_message(self, _("Error during long process: ") + str(self.err), lambda *a: exit())

        def do_long_process():
            try:
                # Here is some long process, this time it is just fake 3 seconds sleep delay
                time.sleep(3)
            except Exception as err:
                self.err = err
                GLib.idle_add(on_task_error)
            else:
                GLib.idle_add(on_task_complete)

        thread = threading.Thread(target=do_long_process)
        thread.start()


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

def show_success_message(window, title, message, callback):
        dialog = Gtk.MessageDialog(
            transient_for=window,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=title,
            secondary_text=message
        )
        dialog.present()
        dialog.connect("response", lambda *a: _continue_after_message(dialog, callback))

class Application(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.uncom.app-template") # TODO: Define you app ID here
        GLib.set_application_name(_("Uncomm App Template")) # TODO: Define you app window title here

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

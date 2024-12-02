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

PATH_TO_APPS_FOLDER = '~/.local/bin/'
PATH_TO_DESKTOP_FILES_FOLDER = '~/.local/share/applications/'
PATH_TO_ICONS_FOLDER = '~/.local/share/icons/appimage'
DEFAULT_APP_ICON = "appimage_application.png"
WINDOW_IMAGE = "/usr/share/icons/hicolor/512x512/apps/appimage_application.png"

text_domain = "uncom-manager-appimage"
gettext.bindtextdomain(text_domain, '/usr/share/uncom/uncom-manager-appimage/locale')
gettext.textdomain(text_domain)
_ = gettext.gettext


class WindowAskForInstall(Gtk.ApplicationWindow):
    def __init__(self, **kargs):
        super().__init__(**kargs, title=_("AppImage Installer"))
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

        # Image
        self.picture = Gtk.Picture.new_for_filename(WINDOW_IMAGE)
        self.picture.props.vexpand = True
        self.visual_container.append(self.picture)

        # Messages
        label_message = Gtk.Label()
        label_message.set_markup(_("This application may be installed into system. After that you can find it in menu <b>All applications</b>."))
        label_message.props.justify = Gtk.Justification.CENTER
        label_message.props.wrap = True
        label_message.props.hexpand = True
        horizontal_message.append(label_message)

        # Left button
        self.button_l = Gtk.Button.new_with_label(_("Launch"))
        self.button_l.connect('clicked', self.on_click_launch)
        self.button_l.props.hexpand = True
        horiontal_buttons.append(self.button_l)

        # Right button
        self.button_r = Gtk.Button.new_with_mnemonic(_("Install"))
        self.button_r.connect('clicked', self.on_click_install)
        self.button_r.props.hexpand = True
        horiontal_buttons.append(self.button_r)

        # Check if given AppImage file exists
        if not os.path.isfile(args.file_name):
            self.button_l.set_sensitive(False)
            self.button_r.set_sensitive(False)
            show_error_message(self, _("Given AppImage file does not exist: ") + args.file_name, lambda *a: exit())

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

    def on_click_launch(self, _button):
        self.button_l.set_sensitive(False)
        self.button_r.set_sensitive(False)
        launch(args.file_name)

    def on_click_install(self, _button):
        self.button_l.set_sensitive(False)
        self.button_r.set_sensitive(False)
        self.show_spinner()

        def on_task_complete():
            self.hide_spinner()
            show_success_message(self, _("Installed"), _("Application installed succeessfully."), lambda *a: exit())
        
        def on_task_error():
            self.hide_spinner()
            show_error_message(self, _("Error during installation: ") + str(self.err), lambda *a: exit())

        def do_installation():
            try:
                install(args.file_name)
            except Exception as err:
                self.err = err
                GLib.idle_add(on_task_error)
            else:
                GLib.idle_add(on_task_complete)

        thread = threading.Thread(target=do_installation)
        thread.start()


class WindowAskForRemove(Gtk.ApplicationWindow):
    def __init__(self, **kargs):
        super().__init__(**kargs, title=_("AppImage Installer"))
        self.set_resizable(False)
        self.set_default_size(500, 100)
        
        # Common top level container
        main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main.props.margin_start = 25
        main.props.margin_end = 25
        main.props.margin_top = 25
        main.props.margin_bottom = 25
        self.set_child(main)

        # Message container
        horiontal_message = Gtk.Box(spacing=10)
        main.append(horiontal_message)

        # Buttons container
        horiontal_buttons = Gtk.Box(spacing=10)
        horiontal_buttons.props.margin_top = 25
        horiontal_buttons.props.halign = Gtk.Align.CENTER
        main.append(horiontal_buttons)

        # Messages
        label_message = Gtk.Label()
        label_message.set_markup(_("Do you want to delete this application?"))
        label_message.props.justify = Gtk.Justification.CENTER
        label_message.props.wrap = True
        label_message.props.hexpand = True
        horiontal_message.append(label_message)

        # Right button
        button = Gtk.Button.new_with_mnemonic(_("Yes"))
        button.get_child().props.margin_start = 25
        button.get_child().props.margin_end = 25
        button.connect('clicked', self.on_click_yes)
        horiontal_buttons.append(button)

        # Left button
        button = Gtk.Button.new_with_label(_("No"))
        button.get_child().props.margin_start = 25
        button.get_child().props.margin_end = 25
        button.connect('clicked', self.on_click_no)
        horiontal_buttons.append(button)

    def on_click_no(self, _button):
        exit()

    def on_click_yes(self, _button):
        remove(args.file_name)
        exit()

class WindowWelcome(Gtk.ApplicationWindow):
    def __init__(self, **kargs):
        super().__init__(**kargs, title=_("AppImage Installer"))
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

        # Image
        self.picture = Gtk.Picture.new_for_filename(WINDOW_IMAGE)
        self.picture.props.vexpand = True
        self.visual_container.append(self.picture)

        # Messages
        label_message = Gtk.Label()
        label_message.set_markup(_("This app allows to install AppImage applications into system and launch them via apps menu. Download any AppImage file and double click on it to launch or install."))
        label_message.props.justify = Gtk.Justification.CENTER
        label_message.props.wrap = True
        label_message.props.hexpand = True
        horizontal_message.append(label_message)

        # Button
        self.button = Gtk.Button.new_with_label(_("OK"))
        self.button.connect('clicked', self.on_click_ok)
        self.button.props.hexpand = True
        horiontal_buttons.append(self.button)

    def on_click_ok(self, _button):
        exit()

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
    mode = ""

    def __init__(self, mode):
        super().__init__(application_id="com.uncom.manager-appimage")
        self.mode = mode
        GLib.set_application_name(_("AppImage Installer")) # Установщик AppImage

    def do_activate(self):
        if self.mode == "remove":
            window = WindowAskForRemove(application=self)
            window.present()
        elif self.mode == "welcome":
            window = WindowWelcome(application=self)
            window.present()
        else:
            window = WindowAskForInstall(application=self)
            window.present()


# Supportive function to make sure path exists
def ensure_folder_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

# Supportive function to generate random string
def generate_random_string(length=15):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

# Supportive function to make file non executable
def make_non_executable(file_name):
    existing_permissions = stat.S_IMODE(os.stat(file_name).st_mode)

    if os.access(file_name, os.X_OK):
        print("Executable tag: presented, removing")
        new_permissions = existing_permissions ^ stat.S_IXUSR
        os.chmod(file_name, new_permissions)
        return True
    else:
        print("Executable tag: non presented")
        return False

# Supportive function to make file executable
def make_executable(file_name):
    existing_permissions = stat.S_IMODE(os.stat(file_name).st_mode)

    if not os.access(file_name, os.X_OK):
        print("Executable tag: not presented, adding")
        new_permissions = existing_permissions | stat.S_IXUSR
        os.chmod(file_name, new_permissions)
        return True
    else:
        print("Executable tag: presented")
        return False

# Supportive function to extract AppImage and view its content
def prepare_appimage_meta(file_name):
    # Remove previous extracted folder
    extract_folder = "/tmp/squashfs-root/"
    tmp_folder = "/tmp/"
    if os.path.isdir(extract_folder) and not os.path.islink(extract_folder):
        shutil.rmtree(extract_folder)
    
    # Extract content (only required files)
    print("Content of AppImage file...")
    changed = make_executable(file_name)
    current_dir = os.getcwd()
    os.chdir(tmp_folder)
    subprocess.call([os.path.join(current_dir, file_name), "--appimage-extract"])
    os.chdir(current_dir)
    if changed:
        make_non_executable(file_name)
    print("... all files are extracted.")

    # Parse .desktop file
    new_desktop_config = configparser.ConfigParser()
    new_desktop_config.optionxform = lambda option: option
    new_desktop_config.optionxform = lambda option: option
    new_desktop_config['Desktop Entry'] = {}
    new_desktop_entry = new_desktop_config['Desktop Entry']
    regex_desktop = re.compile('(.*desktop$)')
    desktop_file_found = False
    for file in os.listdir(extract_folder):
        if regex_desktop.match(file):
            desktop_file_path = os.path.join(extract_folder, file)
            print("Source desktop file path: " + desktop_file_path)
            desktop_file_found = True
            old_desktop_config = configparser.ConfigParser()
            old_desktop_config.read(desktop_file_path)
            old_desktop_entry = old_desktop_config['Desktop Entry']
            if "Name" in old_desktop_entry:
                new_desktop_entry["Name"] = old_desktop_entry["Name"]
            else: 
                new_desktop_entry["Name"] = "Application"
                new_desktop_entry["Name[ru]"] = "Программа"
            if "Type" in old_desktop_entry:
                new_desktop_entry["Type"] = old_desktop_entry["Type"]
            else:
                new_desktop_entry["Type"] = "Application"
            if "Terminal" in old_desktop_entry:
                new_desktop_entry["Terminal"] = old_desktop_entry["Terminal"]
            else:
                new_desktop_entry["Terminal"] = "false"
            if "StartupWMClass" in old_desktop_entry:
                new_desktop_entry["StartupWMClass"] = old_desktop_entry["StartupWMClass"]
    if not desktop_file_found:
        print("Source desktop file not found")
        new_desktop_entry["Name"] = "Application"
        new_desktop_entry["Name[ru]"] = "Программа"
        new_desktop_entry["Type"] = "Application"
        new_desktop_entry["Terminal"] = "false"
    
    # Get application image
    regex_image = re.compile('(.*png$)|(.*ico$)|(.*svg$)|(.*icns$)')
    image_file_path = ""
    image_file_found = False
    for file in os.listdir(extract_folder):
        if regex_image.match(file):
            image_file_path = os.path.join(extract_folder, file)
            print("Source icon file path: " + image_file_path)
            image_file_found = True
    if not image_file_found:
        print("Source icon file not found")
    
    return [new_desktop_config, image_file_path]


# Main logic: run appimage application
def launch(file_name):
    changed = make_executable(file_name)
    print("Launching AppImage application...")
    proc = subprocess.Popen([file_name])
    if changed:
        make_non_executable(file_name)
    exit()

# Main logic: install appimage - move into appropriate location and create .desktop file
def install(file_name):
    # Prepare meta data for appimage
    meta = prepare_appimage_meta(file_name)
    desktop_config = meta[0]
    original_image_file_path = meta[1]

    base_name = os.path.basename(file_name)
    pure_file_extension = os.path.splitext(base_name)[1]
    pure_file_name = os.path.splitext(base_name)[0]
    path_apps_folder = os.path.expanduser(PATH_TO_APPS_FOLDER)
    path_desktop_folder = os.path.expanduser(PATH_TO_DESKTOP_FILES_FOLDER)
    random_string = generate_random_string()

    # Define new file path
    app_name = desktop_config["Desktop Entry"]["Name"].replace(' ', '-').lower()
    new_base_name = app_name + "-" + random_string + pure_file_extension
    new_file_name = os.path.join(path_apps_folder, new_base_name)
    ensure_folder_exists(path_apps_folder)

    # Move binary into appropriate location
    print("Move appimage from: " + file_name)
    print("Move appimage to: " + new_file_name)
    os.rename(file_name, new_file_name)
    make_executable(new_file_name)

    # Save icon image
    if original_image_file_path == "":
        # There is no own icon, use default
        new_image_file_path = DEFAULT_APP_ICON
    else:
        # There is an existing icon from appimage, use it
        icons_folder = os.path.expanduser(PATH_TO_ICONS_FOLDER)
        new_image_file_name = new_base_name + os.path.splitext(original_image_file_path)[1]
        new_image_file_path = os.path.join(icons_folder, new_image_file_name)
        ensure_folder_exists(icons_folder)

        print("Move icon image from: " + original_image_file_path)
        print("Move icon image to: " + new_image_file_path)
        shutil.copyfile(original_image_file_path, new_image_file_path)

    desktop_entry = desktop_config["Desktop Entry"]
    desktop_entry["Version"] = "1.0"
    desktop_entry["Exec"] = new_file_name
    desktop_entry["Actions"] = "remove"
    desktop_entry["Icon"] = new_image_file_path

    desktop_config["Desktop Action remove"] = {}
    desktop_action = desktop_config["Desktop Action remove"]
    desktop_action["Name"] = "Uninstall"
    desktop_action["Name[ru]"] = "Удалить"
    desktop_action["Exec"] = 'uncom-manager-appimage -g -r "' + new_file_name + '"'

    # Create .desktop file
    desktop_base_name = new_base_name + ".desktop"
    desktop_file_name = os.path.join(path_desktop_folder, desktop_base_name)
    with open(desktop_file_name, 'w') as desktop_file:
        desktop_config.write(desktop_file, space_around_delimiters=False)

    print("Desktop file: " + desktop_file_name)
    print("Installation complated successfully")
    return new_file_name

# Main logic: delete application file and .desktop file
def remove(file_name):
    base_name = os.path.basename(file_name)

    # find matching desktop file
    path_desktop_folder = os.path.expanduser(PATH_TO_DESKTOP_FILES_FOLDER)
    desktop_base_name = base_name + ".desktop"
    desktop_file_name = os.path.join(path_desktop_folder, desktop_base_name)

    # find matching icon file
    icons_folder = os.path.expanduser(PATH_TO_ICONS_FOLDER)
    image_file_path = ""
    regex_icon = re.compile('(' + base_name + '.*$)')
    for file in os.listdir(icons_folder):
        if regex_icon.match(file):
            image_file_path = os.path.join(icons_folder, file)

    if os.path.isfile(file_name):
        os.remove(file_name)
        print("Removed AppImage file: " + file_name)
        
        if os.path.isfile(desktop_file_name):
            os.remove(desktop_file_name)
            print("Removed Desktop file: " + desktop_file_name)
        
        if os.path.isfile(image_file_path):
            os.remove(image_file_path)
            print("Removed Icon file: " + image_file_path)

        print("Application removed successfully")
    else:
        print("There is no application on this path")


parser = argparse.ArgumentParser(
    description="Uncom Manager for AppImage applications.",
    epilog="Start without parameters to view help.")

parser.add_argument('-g', '--gui', action='store_true', help='Run with graphical UI, used for desktop sessions')
parser.add_argument('-l', '--launch', action='store_true', help='Launch given AppImage')

group2 = parser.add_mutually_exclusive_group(required=False)
group2.add_argument('-i', '--install', action='store_true', help='Install given AppImage')
group2.add_argument('-r', '--remove', action='store_true', help='Remove given AppImage, configuration files will be left')

parser.add_argument('file_name', type=str, help="Path to AppImage file")

args = parser.parse_args()

print("Given AppImage file: " + args.file_name)

if args.gui: # run in GUI mode
    
    # clear arguments so GTK will not trigger on them
    sys.argv = [sys.argv[0]]
    
    if args.launch:
        launch(args.file_name)
    elif args.install:
        app = Application("install")
        exit_status = app.run(sys.argv)
        sys.exit(exit_status)
    elif args.remove:
        app = Application("remove")
        exit_status = app.run(sys.argv)
        sys.exit(exit_status)
    else:
        app = Application("welcome")
        exit_status = app.run(sys.argv)
        sys.exit(exit_status)
else: # run in command line mode
    if args.install:
        install(args.file_name)
        if args.launch:
            launch(args.file_name)
    elif args.launch:
            launch(args.file_name)
    elif args.remove:
        remove(args.file_name)

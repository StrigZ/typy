from gi.repository import Adw, GLib, Gtk

from constants import _


def show_settings(window):
    dialog = Adw.PreferencesDialog()
    page = Adw.PreferencesPage()
    dialog.add(page)

    group = Adw.PreferencesGroup(title=_("Typing"))
    page.add(group)

    reset_row = Adw.ActionRow(title=_("Reset stats"))
    reset_button = Gtk.Button(label=_("Reset"), valign=Gtk.Align.CENTER)
    reset_button.connect("clicked", lambda *a: window.char_stats.reset_data())
    reset_row.add_suffix(reset_button)
    group.add(reset_row)

    dialog.present(window)

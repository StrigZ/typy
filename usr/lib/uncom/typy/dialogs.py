from gi.repository import Adw, GLib, Gtk

from constants import _
from stats import reset_missed_char_counts


def show_completion_popup(window, callback_restart):
    dialog = Gtk.AlertDialog()
    dialog.set_message(_("Finished!"))
    dialog.set_detail(_("You completed the typing test."))
    dialog.set_buttons([_("Restart"), _("Close")])
    dialog.set_default_button(0)
    dialog.set_cancel_button(1)

    def on_response(source, result, *_data):
        try:
            button_index = dialog.choose_finish(result)
        except GLib.Error:
            return
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

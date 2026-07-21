from gi.repository import Adw, GLib

import stats
from constants import _
from window import WindowMain


class Application(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.uncom.typy")
        GLib.set_application_name(_("typy"))
        self.connect("shutdown", lambda *a: stats.save_missed_char_counts())

    def do_activate(self):
        window = WindowMain(application=self)
        window.present()

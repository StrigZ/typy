from gi.repository import Adw, GLib

from constants import _
from window import WindowMain


class Application(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.uncom.typy")
        GLib.set_application_name("typy")

    def do_activate(self):
        window = WindowMain(application=self)
        self.connect("shutdown", lambda *a: window.typing_field.char_stats.save_data())
        window.present()

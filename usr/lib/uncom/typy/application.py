from gi.repository import Adw, GLib
from window import WindowMain


class Application(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.uncom.typy")
        GLib.set_application_name("typy")

    def do_activate(self):
        window = WindowMain(application=self)
        self.connect(
            "shutdown", lambda *a: window.typing_controller.char_stats.save_data()
        )
        window.present()

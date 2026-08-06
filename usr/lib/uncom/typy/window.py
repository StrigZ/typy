from gi.repository import Gdk, Gtk

from constants import _, STYLE_CSS
from typing_controller import TypingController

from settings_dialog import show_settings
from stats_dialog import show_stats


class WindowMain(Gtk.ApplicationWindow):
    def __init__(self, **kargs):
        super().__init__(**kargs, title="typy")
        self.set_resizable(True)
        self.set_default_size(700, 300)
        self.set_size_request(600, 300)

        self.load_css()
        self._build_ui()

        activate_controller = Gtk.EventControllerKey()
        activate_controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        activate_controller.connect("key-pressed", self.on_activate_key_pressed)
        self.add_controller(activate_controller)

    def _build_ui(self):
        main = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=32,
            margin_start=24,
            margin_end=24,
            margin_top=24,
            margin_bottom=24,
        )
        self.set_child(main)

        self.typing_controller = TypingController(hexpand=True, vexpand=True)
        main.append(self.typing_controller)

        deactivate_click_gesture = Gtk.GestureClick()
        deactivate_click_gesture.connect("pressed", lambda *a: self.set_focus(None))
        main.add_controller(deactivate_click_gesture)

        buttons_box = Gtk.Box(halign=Gtk.Align.END, spacing=8)

        stats_button = Gtk.Button(label=_("Stats"))
        stats_button.connect(
            "clicked",
            lambda *a: show_stats(
                self,
                self.typing_controller.stats_bar.daily_goal,
                self.typing_controller.stats_bar.performance_stats,
            ),
        )
        buttons_box.append(stats_button)

        settings_button = Gtk.Button(icon_name="emblem-system-symbolic")
        settings_button.connect(
            "clicked", lambda *a: show_settings(self, self.typing_controller)
        )
        buttons_box.append(settings_button)

        main.append(buttons_box)

        self.connect("notify::is-active", self._on_window_active_changed)

    def _on_window_active_changed(self, window, param):
        if not self.is_active():
            self.typing_controller.deactivate()

    def on_activate_key_pressed(self, controller, keyval, keycode, state):
        if (
            keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter)
            and not self.typing_controller.is_focus()
        ):
            self.typing_controller.typing_area.grab_focus()
            return True
        return False

    def load_css(self):
        display = Gdk.Display.get_default()
        if display is None:
            return

        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(STYLE_CSS)

        Gtk.StyleContext.add_provider_for_display(
            display,
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

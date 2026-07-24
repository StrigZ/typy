from gi.repository import Gdk, Gtk

from constants import _, STYLE_CSS
from dialogs import show_settings
from typing_field import TypingField


class WindowMain(Gtk.ApplicationWindow):
    def __init__(self, **kargs):
        super().__init__(**kargs, title="typy")
        self.set_resizable(False)
        self.set_default_size(500, 300)

        self.load_css()
        self._build_ui()

        activate_controller = Gtk.EventControllerKey()
        activate_controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        activate_controller.connect("key-pressed", self.on_activate_key_pressed)
        self.add_controller(activate_controller)

    def _build_ui(self):
        main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        main.props.margin_start = 25
        main.props.margin_end = 25
        main.props.margin_top = 25
        main.props.margin_bottom = 25
        self.set_child(main)

        self.typing_field = TypingField(hexpand=True, vexpand=True)
        main.append(self.typing_field)

        deactivate_click_gesture = Gtk.GestureClick()
        deactivate_click_gesture.connect("pressed", lambda *a: self.set_focus(None))
        main.add_controller(deactivate_click_gesture)

        settings_button = Gtk.Button(label=_("Settings"))
        settings_button.connect("clicked", lambda *a: show_settings(self))
        main.append(settings_button)

    def on_activate_key_pressed(self, controller, keyval, keycode, state):
        if (
            keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter)
            and not self.typing_field.is_focus()
        ):
            self.typing_field.grab_focus()
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

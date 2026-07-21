from gi.repository import Gdk, GLib, Gtk

import stats
from constants import _, COMMON_WORDS


class TypingField(Gtk.Overlay):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_focusable(True)
        self.add_css_class("typing-field-container")

        self.missed_keys_indices = set()
        self.string_to_type = self.generate_string_to_type()
        self.string_to_type_pointer = 0

        self._build_ui()
        self.update_highlights()

        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self.on_key_pressed)
        self.add_controller(key_controller)

        focus_controller = Gtk.EventControllerFocus()
        focus_controller.connect("enter", lambda *a: self.on_focus_enter())
        focus_controller.connect("leave", lambda *a: self.on_focus_leave())
        self.add_controller(focus_controller)

        click_gesture = Gtk.GestureClick()
        click_gesture.connect("pressed", self.on_clicked)
        self.add_controller(click_gesture)

    def _build_ui(self):
        content = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10,
            css_classes=["typing-field"],
        )

        self.string_to_type_label = Gtk.Label()
        self.string_to_type_label.set_text(self.string_to_type)
        self.string_to_type_label.add_css_class("string-to-type")
        self.string_to_type_label.props.wrap = True
        self.string_to_type_label.props.justify = Gtk.Justification.CENTER
        content.append(self.string_to_type_label)

        self.key_display_label = Gtk.Label()
        self.key_display_label.add_css_class("key-display")
        content.append(self.key_display_label)

        self.set_child(content)

        self.hint_label = Gtk.Label(
            label=_("Click or press Enter to start typing"),
            halign=Gtk.Align.CENTER,
            valign=Gtk.Align.CENTER,
            css_classes=["dim-label"],
        )
        self.add_overlay(self.hint_label)

    def on_clicked(self, gesture, n_press, x, y):
        self.grab_focus()
        gesture.set_state(Gtk.EventSequenceState.CLAIMED)

    def on_focus_enter(self):
        self.add_css_class("active")
        self.hint_label.set_visible(False)

    def on_focus_leave(self):
        self.remove_css_class("active")
        self.hint_label.set_visible(True)
        self.reset_current_string()

    def generate_string_to_type(self):
        return stats.generate_string(COMMON_WORDS)

    def update_highlights(self):
        parts = []
        for i, ch in enumerate(self.string_to_type):
            escaped = GLib.markup_escape_text(ch)

            if i < self.string_to_type_pointer:
                color = "#e53935" if i in self.missed_keys_indices else "#4caf50"
                parts.append(f'<span foreground="{color}">{escaped}</span>')
            elif i == self.string_to_type_pointer:
                parts.append(
                    f'<span foreground="#888888" underline="single">{escaped}</span>'
                )
            else:
                parts.append(f'<span foreground="#888888">{escaped}</span>')

        self.string_to_type_label.set_markup("".join(parts))

    def on_key_pressed(self, controller, keyval, keycode, state):
        if self.string_to_type_pointer >= len(self.string_to_type):
            return True

        unicode_val = Gdk.keyval_to_unicode(keyval)
        if not unicode_val:
            return True

        char = chr(unicode_val)
        self.key_display_label.set_text(char)

        curr_char = self.string_to_type[self.string_to_type_pointer]

        if curr_char == char:
            self.string_to_type_pointer += 1
            if stats.missed_char_counts.get(curr_char, 0) > 0:
                stats.missed_char_counts[curr_char] -= 1
            if self.string_to_type_pointer == len(self.string_to_type):
                self.start_new_string()
        else:
            self.missed_keys_indices.add(self.string_to_type_pointer)
            stats.missed_char_counts[curr_char] += 1

        self.update_highlights()
        return True

    def start_new_string(self):
        stats.save_missed_char_counts()
        self.string_to_type = self.generate_string_to_type()
        self.reset_current_string()

    def reset_current_string(self):
        self.string_to_type_pointer = 0
        self.missed_keys_indices.clear()
        self.key_display_label.set_text("")
        self.update_highlights()

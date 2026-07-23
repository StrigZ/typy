import time

from gi.repository import Gdk, GLib, Gtk

from constants import _, COMMON_WORDS
from char_stats import CharStats
import random

MISS_WEIGHT = 2
SLOW_WEIGHT = 1


class TypingField(Gtk.Overlay):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_focusable(True)
        self.add_css_class("typing-field-container")

        self.char_stats = CharStats()

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

        self.key_time_start = time.monotonic()

    def _build_ui(self):
        content = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10,
            css_classes=["typing-field"],
        )

        self.string_to_type_label = Gtk.Label(
            css_classes=["string-to-type"], wrap=True, justify=Gtk.Justification.CENTER
        )
        self.string_to_type_label.set_text(self.string_to_type)
        content.append(self.string_to_type_label)

        self.key_display_label = Gtk.Label(css_classes=["key-display"])
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
        self.key_time_start = time.monotonic()

    def on_focus_leave(self):
        self.remove_css_class("active")
        self.hint_label.set_visible(True)
        self.reset_current_string()

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

        now = time.monotonic()
        elapsed = now - self.key_time_start
        self.key_time_start = now

        char = chr(unicode_val)
        self.key_display_label.set_text(char)

        curr_char = self.string_to_type[self.string_to_type_pointer]
        is_correct = curr_char == char

        if is_correct:
            self.string_to_type_pointer += 1

            if self.string_to_type_pointer == len(self.string_to_type):
                self.start_new_string()
        else:
            self.missed_keys_indices.add(self.string_to_type_pointer)

        self.char_stats.update_stat(curr_char, elapsed, is_correct)
        self.update_highlights()

        return True

    def start_new_string(self):
        self.char_stats.save_data()
        self.string_to_type = self.generate_string_to_type()
        self.reset_current_string()

    def reset_current_string(self):
        self.string_to_type_pointer = 0
        self.missed_keys_indices.clear()
        self.key_display_label.set_text("")
        self.update_highlights()
        self.key_time_start = time.monotonic()

    def generate_string_to_type(self, word_count=5):
        def word_weight(word):
            total = 1
            for c in word:
                stat = self.char_stats.get_stat(c)
                total += stat["miss"] * MISS_WEIGHT + stat["slow"] * SLOW_WEIGHT
            return total

        weights = [word_weight(w) for w in COMMON_WORDS]
        chosen = random.choices(COMMON_WORDS, weights=weights, k=word_count)
        return " ".join(chosen)

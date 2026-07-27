import time
import math
from gi.repository import Gdk, GLib, Gtk

from constants import _, WORD_LIST
from char_stats import CharStats
import random

from stats_bar import StatsBar

MISS_WEIGHT = 2
SLOW_WEIGHT = 1


class TypingField(Gtk.Box):
    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=32, **kwargs)

        self.char_stats = CharStats()
        self.stats_bar = StatsBar()
        self.append(self.stats_bar)

        self.missed_keys_indices = set()
        self.string_to_type = self.generate_string_to_type()
        self.string_to_type_pointer = 0

        self._build_ui()
        self._attach_controllers()
        self.update_highlights()

        self.key_time_start = time.monotonic()
        self.string_time_start = time.monotonic()

    def on_clicked(self, gesture, n_press, x, y):
        self.words_container.grab_focus()
        gesture.set_state(Gtk.EventSequenceState.CLAIMED)

    def on_focus_enter(self):
        self.words_container.add_css_class("active")
        self.hint_label.set_visible(False)
        self.key_time_start = time.monotonic()
        self.string_time_start = time.monotonic()
        self.stats_bar.start_new_string()

    def on_focus_leave(self):
        self.words_container.remove_css_class("active")
        self.hint_label.set_visible(True)
        self.reset_current_string()

    def activate(self):
        self.words_container.grab_focus()

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
        self.key_time_start = now

        char = chr(unicode_val)
        self.key_display_label.set_text(char)

        curr_char = self.string_to_type[self.string_to_type_pointer]
        is_correct = curr_char == char
        string_length = len(self.string_to_type)

        self.stats_bar.record_keystroke(is_correct)
        self.char_stats.update_stat(curr_char, now - self.key_time_start, is_correct)

        if is_correct:
            self.string_to_type_pointer += 1
            is_string_finished = self.string_to_type_pointer == string_length

            if is_string_finished:
                self.stats_bar.update_perfomance_stats(string_length)
                self.stats_bar.update_daily_goal_stats(now - self.string_time_start)

                self.char_stats.save_data()

                self.start_new_string()
        else:
            self.missed_keys_indices.add(self.string_to_type_pointer)

        self.update_highlights()

        return True

    def start_new_string(self):
        self.string_to_type = self.generate_string_to_type()
        self.reset_current_string()

    def reset_current_string(self):
        self.string_to_type_pointer = 0
        self.missed_keys_indices.clear()
        self.key_display_label.set_text("")
        self.update_highlights()
        self.key_time_start = time.monotonic()
        self.string_time_start = time.monotonic()

    def _get_word_weight(self, word: str, freq: int):
        freq_score = math.log10(freq + 1)

        mistake_score = 0
        for c in word:
            stat = self.char_stats.get_stat(c)
            mistake_score += stat["miss"] * MISS_WEIGHT + stat["slow"] * SLOW_WEIGHT

        return freq_score + mistake_score

    def generate_string_to_type(self, word_count=5):
        weights = [self._get_word_weight(w, freq) for w, freq in WORD_LIST]
        chosen = [
            w for w, freq in random.choices(WORD_LIST, weights=weights, k=word_count)
        ]
        return " ".join(chosen)

    def _build_ui(self):
        self._build_words_container()

    def _build_words_container(self):
        self.words_container = Gtk.Overlay(
            css_classes=["typing-field-container"], focusable=True
        )
        content = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=24,
            css_classes=["typing-field"],
        )

        self.string_to_type_label = Gtk.Label(
            css_classes=["string-to-type"], wrap=True, justify=Gtk.Justification.CENTER
        )
        self.string_to_type_label.set_text(self.string_to_type)
        content.append(self.string_to_type_label)

        self.key_display_label = Gtk.Label(css_classes=["key-display"])
        content.append(self.key_display_label)

        self.words_container.set_child(content)

        self.hint_label = Gtk.Label(
            label=_("Click or press Enter to start typing"),
            halign=Gtk.Align.CENTER,
            valign=Gtk.Align.CENTER,
            css_classes=["dim-label"],
        )
        self.words_container.add_overlay(self.hint_label)

        self.append(self.words_container)

    def _attach_controllers(self):
        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self.on_key_pressed)
        self.words_container.add_controller(key_controller)

        focus_controller = Gtk.EventControllerFocus()
        focus_controller.connect("enter", lambda *a: self.on_focus_enter())
        focus_controller.connect("leave", lambda *a: self.on_focus_leave())
        self.words_container.add_controller(focus_controller)

        click_gesture = Gtk.GestureClick()
        click_gesture.connect("pressed", self.on_clicked)
        self.words_container.add_controller(click_gesture)

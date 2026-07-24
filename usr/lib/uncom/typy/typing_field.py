import time
import math
from gi.repository import Gdk, GLib, Gtk

from constants import _, WORD_LIST
from char_stats import CharStats
import random

from performance_stats_ui import PerformanceStatsUI
from performance_stats import PerformanceStats
from daily_goal import DailyGoal

MISS_WEIGHT = 2
SLOW_WEIGHT = 1


class TypingField(Gtk.Overlay):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_focusable(True)
        self.add_css_class("typing-field-container")

        self.char_stats = CharStats()
        self.performance_stats = PerformanceStats()
        self.daily_goal = DailyGoal()

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
        self.string_time_start = time.monotonic()

    def _build_ui(self):
        content = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10,
            css_classes=["typing-field"],
        )

        self.performance_stats_ui = PerformanceStatsUI()
        content.append(self.performance_stats_ui)

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
        self.string_time_start = time.monotonic()
        self.performance_stats.start_new_string()

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
        self.key_time_start = now

        char = chr(unicode_val)
        self.key_display_label.set_text(char)

        curr_char = self.string_to_type[self.string_to_type_pointer]
        is_correct = curr_char == char
        string_length = len(self.string_to_type)

        self.performance_stats.record_keystroke(is_correct)
        self.char_stats.update_stat(curr_char, now - self.key_time_start, is_correct)

        if is_correct:
            self.string_to_type_pointer += 1
            is_string_finished = self.string_to_type_pointer == string_length

            if is_string_finished:
                self.performance_stats_ui.update(
                    self.performance_stats.get_current_wpm(string_length),
                    self.performance_stats.get_current_accuracy(),
                )

                self.performance_stats.update_and_save_averages(string_length)
                self.performance_stats.start_new_string()

                self.daily_goal.increment(now - self.string_time_start)

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

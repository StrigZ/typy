import math
import random
import time

from gi.repository import Gdk, Gtk

from char_stats import CharStats
from constants import WORD_LIST
from stats_bar import StatsBar
from typing_area import TypingArea

MISS_WEIGHT = 2
SLOW_WEIGHT = 1


class TypingController(Gtk.Box):
    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=32, **kwargs)

        self._char_stats = CharStats()

        self._stats_bar = StatsBar()
        self.append(self._stats_bar)

        self._string_to_type = self._generate_string_to_type()
        self._string_to_type_pointer = 0
        self._missed_keys_indices = set()

        self._typing_area = TypingArea()
        self.append(self._typing_area)
        self._render()

        self._attach_controllers()

        self._key_time_start = time.monotonic()
        self._string_time_start = time.monotonic()

    def activate(self):
        self._typing_area.focus()

    def save_char_stats(self):
        self._char_stats.save_data()

    def _on_clicked(self, gesture, n_press, x, y):
        self._typing_area.focus()
        gesture.set_state(Gtk.EventSequenceState.CLAIMED)

    def _on_focus_enter(self, controller):
        self._stats_bar.start_new_string()
        self._typing_area.unblur()

    def _on_focus_leave(self, controller):
        self._typing_area.blur()
        self._typing_area.clear_display_character()
        self._start_new_string()

    def _on_key_pressed(self, controller, keyval, keycode, state):
        current_string_length = len(self._string_to_type)

        if self._string_to_type_pointer >= current_string_length:
            return True

        unicode_val = Gdk.keyval_to_unicode(keyval)
        if not unicode_val:
            return True

        now = time.monotonic()
        elapsed = now - self._key_time_start
        self._key_time_start = now

        char = chr(unicode_val)
        self._typing_area.update_display_character(char)

        curr_char = self._string_to_type[self._string_to_type_pointer]
        is_correct = curr_char == char

        self._stats_bar.record_keystroke(is_correct)
        self._char_stats.update_stat(curr_char, elapsed, is_correct)

        if is_correct:
            self._string_to_type_pointer += 1

            if self._string_to_type_pointer == current_string_length:
                self._stats_bar.update_perfomance_stats(current_string_length)
                self._stats_bar.update_daily_goal_stats(now - self._string_time_start)
                self._char_stats.save_data()
                self._start_new_string()
        else:
            self._missed_keys_indices.add(self._string_to_type_pointer)

        self._render()
        return True

    def _start_new_string(self):
        self._string_to_type = self._generate_string_to_type()
        self._string_to_type_pointer = 0
        self._missed_keys_indices.clear()
        self._string_time_start = time.monotonic()
        self._typing_area.clear_display_character()
        self._render()

    def _render(self):
        self._typing_area.render(
            self._string_to_type,
            self._string_to_type_pointer,
            self._missed_keys_indices,
        )

    def _attach_controllers(self):
        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self._on_key_pressed)
        self._typing_area.add_controller(key_controller)

        focus_controller = Gtk.EventControllerFocus()
        focus_controller.connect("enter", self._on_focus_enter)
        focus_controller.connect("leave", self._on_focus_leave)
        self._typing_area.add_controller(focus_controller)

        click_gesture = Gtk.GestureClick()
        click_gesture.connect("pressed", self._on_clicked)
        self._typing_area.add_controller(click_gesture)

    def _get_word_weight(self, word: str, freq: int):
        freq_score = math.log10(freq + 1)
        mistake_score = 0
        for c in word:
            stat = self._char_stats.get_stat(c)
            mistake_score += stat["miss"] * MISS_WEIGHT + stat["slow"] * SLOW_WEIGHT
        return freq_score + mistake_score

    def _generate_string_to_type(self, word_count=5):
        weights = [self._get_word_weight(w, freq) for w, freq in WORD_LIST]
        chosen = [
            w for w, freq in random.choices(WORD_LIST, weights=weights, k=word_count)
        ]
        return " ".join(chosen)

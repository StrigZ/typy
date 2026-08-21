import time
from string import ascii_lowercase

from app_settings import get_app_settings
from char_stats import CharStats
from gi.repository import Gdk, Gtk
from learning_progress import LearningProgress
from stats_bar import StatsBar
from string_generator import StringGenerator
from typing_area import TypingArea

app_settings = get_app_settings()


class TypingController(Gtk.Box):
    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=32, **kwargs)

        self.char_stats = CharStats()
        self.learning_progress = LearningProgress(self.char_stats)
        self.string_generator = StringGenerator(self.learning_progress, self.char_stats)

        self.stats_bar = StatsBar(self.learning_progress, self.char_stats)
        self.append(self.stats_bar)

        self._string_to_type = self.string_generator.generate()
        self._is_first_keystroke = True
        self._string_to_type_pointer = 0
        self._missed_keys_indices = set()

        self.typing_area = TypingArea()
        self.append(self.typing_area)
        self._render()

        self._attach_controllers()

        self._key_time_start = time.monotonic()
        self._string_time_start = time.monotonic()

        self.stats_bar.performance_stats.reset_counters()

        app_settings.connect(
            "notify::string-length",
            lambda *a: self._start_new_string(),
        )
        app_settings.connect(
            "notify::string-language",
            lambda *a: self._start_new_string(),
        )
        app_settings.connect(
            "notify::typing-mode",
            lambda *a: self._start_new_string(),
        )
        app_settings.connect(
            "notify::desired-wpm",
            lambda *a: self._start_new_string(),
        )

    def _on_clicked(self, gesture, n_press, x, y):
        self.typing_area.grab_focus()
        gesture.set_state(Gtk.EventSequenceState.CLAIMED)

    def _on_focus_enter(self, controller):
        self.typing_area.unblur()

    def _on_focus_leave(self, controller):
        self.typing_area.blur()
        self._reset_string_progress()

    def _on_key_pressed(self, controller, keyval, keycode, state):
        current_string_length = len(self._string_to_type)
        # index out range guard
        if self._string_to_type_pointer >= current_string_length:
            return True

        unicode_val: int = Gdk.keyval_to_unicode(keyval)

        # Not unicode value like F keys - ignored
        if not unicode_val:
            return True

        # Backspace pressed and this is not the first ch in string
        if self._string_to_type_pointer > 0 and keyval == Gdk.KEY_BackSpace:
            # check if prev ch is incorrect
            # if not, ignore
            prev_char_index = self._string_to_type_pointer - 1
            if prev_char_index not in self._missed_keys_indices:
                return True

            # go back by one index
            self._string_to_type_pointer -= 1
            # remove index from missed indices set
            self._missed_keys_indices.remove(self._string_to_type_pointer)
            # update ui
            self._render()
            return True

        char = chr(unicode_val)

        # Something that is not abc or space - ignored
        if char not in f"{ascii_lowercase} ":
            return True

        now = time.monotonic()

        # start tracking time only from the second keystroke
        # first one is ignored
        if self._is_first_keystroke:
            self.stats_bar.performance_stats.string_start_time = now
            self._string_time_start = now
            elapsed = None
        else:
            elapsed = now - self._key_time_start

        self._key_time_start = now

        self.typing_area.key_display_label.set_text(char)

        curr_char = self._string_to_type[self._string_to_type_pointer]
        is_correct = curr_char == char

        self.stats_bar.performance_stats.record_keystroke(is_correct)
        self.char_stats.update_stat(
            curr_char.lower(), elapsed, is_correct, skip_timing=self._is_first_keystroke
        )

        self._is_first_keystroke = False

        if is_correct:
            self._string_to_type_pointer += 1

            if self._string_to_type_pointer == current_string_length:
                if app_settings.typing_mode == "learning":
                    self.learning_progress.check_progress()
                    self.stats_bar.update_learning_stats()
                else:
                    self.stats_bar.update_stats(current_string_length)

                self.stats_bar.update_daily_goal(now - self._string_time_start)
                self.char_stats.save_data()
                self._start_new_string()
        else:
            self._missed_keys_indices.add(self._string_to_type_pointer)

        self._render()
        return True

    def _start_new_string(self):
        self._string_to_type = self.string_generator.generate()
        self._reset_string_progress()

    def _reset_string_progress(self):
        self._string_to_type_pointer = 0
        self._missed_keys_indices.clear()
        self._is_first_keystroke = True

        self._string_time_start = time.monotonic()
        self._key_time_start = time.monotonic()

        self.stats_bar.performance_stats.reset_counters()

        self.typing_area.key_display_label.set_text("")

        self._render()

    def _render(self):
        self.typing_area.render(
            self._string_to_type,
            self._string_to_type_pointer,
            self._missed_keys_indices,
        )

    def _attach_controllers(self):
        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self._on_key_pressed)
        self.typing_area.add_controller(key_controller)

        focus_controller = Gtk.EventControllerFocus()
        focus_controller.connect("enter", self._on_focus_enter)
        focus_controller.connect("leave", self._on_focus_leave)
        self.typing_area.add_controller(focus_controller)

        click_gesture = Gtk.GestureClick()
        click_gesture.connect("pressed", self._on_clicked)
        self.typing_area.add_controller(click_gesture)

    def deactivate(self):
        self.typing_area.blur()
        self._reset_string_progress()

    def on_char_stat_reset(self):
        self.char_stats.reset_data()
        self.learning_progress.reset()
        self.stats_bar.update_learning_stats()
        self._start_new_string()

import math
import random

from app_settings import get_app_settings
from char_stats import CharStats
from learning_progress import LearningProgress
from word_list import get_word_list

MISS_WEIGHT = 2
SLOW_WEIGHT = 1

SYNTHETIC_UNLOCK_THRESHOLD = (
    6  # below this many unlocked chars, generate synthetic words
)

app_settings = get_app_settings()
word_list = get_word_list()


class StringGenerator:
    def __init__(self, learning_progress: LearningProgress, char_stats: CharStats):
        self.learning_progress = learning_progress
        self._char_stats = char_stats

    def generate(self):
        if app_settings.typing_mode == "learning":
            return self._generate_learning_string()
        return self._generate_freeform_string()

    def _generate_freeform_string(self):
        words = []
        total_length = 0

        all_words = word_list.get_words()
        weights = (
            [self._get_word_weight(w, freq) for w, freq in all_words]
            if app_settings.typing_mode == "adaptive"
            else None
        )

        while True:
            word, _freq = random.choices(all_words, weights=weights, k=1)[0]

            added_length = len(word) + (1 if words else 0)
            if total_length + added_length > app_settings.string_length and words:
                break

            words.append(word)
            total_length += added_length

        return " ".join(words)

    def _generate_learning_string(self) -> str:
        active = self.learning_progress.get_active_chars_lower()
        # if len(active) < SYNTHETIC_UNLOCK_THRESHOLD:
        #     return self._generate_synthetic_string(active)
        return self._generate_filtered_word_string(active)

    # def _generate_synthetic_string(self, eligible: list[str]) -> str:
    #     current = self.learning_progress.get_current_learning_char_lower()
    #     others = [c for c in eligible if c != current]

    #     words = []
    #     total_length = 0
    #     while total_length < app_settings.string_length:
    #         word_len = max(3, random.randint(2, 5))
    #         extra_count = max(0, word_len - 1)  # -1 for the forced `current`
    #         extra = (
    #             random.choices(others or eligible, k=extra_count) if extra_count else []
    #         )

    #         chars = [current] + extra
    #         random.shuffle(chars)
    #         word = "".join(chars)
    #         words.append(word)
    #         total_length += len(word) + 1

    #     return " ".join(words)

    def _generate_filtered_word_string(self, eligible: list[str]) -> str:
        current = self.learning_progress.get_current_learning_char_lower()
        all_words = word_list.get_words()

        filtered = filter_locked_chars(all_words, eligible)
        containing_current = [(w, f) for w, f in filtered if current in w]

        if containing_current:
            pool = containing_current
        elif filtered:
            pool = filtered
        else:
            active = self.learning_progress.get_active_chars_lower()
            pool = filter_locked_chars(all_words, active)

        if not pool:
            return current * 5  # minimal typable fallback, not ideal but never crashes

        weights = [self._get_word_weight(w, freq) for w, freq in pool]
        words = []
        total_length = 0
        while total_length < app_settings.string_length:
            word, _freq = random.choices(pool, weights=weights, k=1)[0]
            added = len(word) + (1 if words else 0)
            if total_length + added > app_settings.string_length and words:
                break
            words.append(word)
            total_length += added
        return " ".join(words)

    def _get_word_weight(self, word: str, freq: int):
        freq_score = math.log10(freq + 1)
        mistake_score = 0
        for c in word:
            stat = self._char_stats.peek_stat(c)
            if stat:
                mistake_score += stat["miss"] * MISS_WEIGHT + stat["slow"] * SLOW_WEIGHT
        return freq_score + mistake_score


def filter_locked_chars(words: list[tuple[str, int]], unlocked_chars: list[str]):
    def filter_fn(entry: tuple[str, int]):
        word, freq = entry
        for c in word:
            if c not in unlocked_chars:
                return False

        return True

    return list(filter(filter_fn, words))

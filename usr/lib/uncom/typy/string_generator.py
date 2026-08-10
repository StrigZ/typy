import math
import random

from app_settings import get_app_settings
from word_list import get_word_list
from char_stats import CharStats

MISS_WEIGHT = 2
SLOW_WEIGHT = 1

app_settings = get_app_settings()
word_list = get_word_list()


class StringGenerator:
    def __init__(self, char_stats: CharStats):
        self._char_stats = char_stats

    def generate(self):
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

    def _get_word_weight(self, word: str, freq: int):
        freq_score = math.log10(freq + 1)
        mistake_score = 0
        for c in word:
            stat = self._char_stats.peek_stat(c)
            if stat:
                mistake_score += stat["miss"] * MISS_WEIGHT + stat["slow"] * SLOW_WEIGHT
        return freq_score + mistake_score

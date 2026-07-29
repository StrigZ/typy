import math
import random

from app_settings import get_app_settings


MISS_WEIGHT = 2
SLOW_WEIGHT = 1

app_settings = get_app_settings()


class StringGenerator:
    def __init__(self, word_list: list[tuple[str, int]], char_stats):
        self._word_list = word_list
        self._char_stats = char_stats

    def generate(self):
        words = []
        total_length = 0

        while True:
            weights = [self._get_word_weight(w, freq) for w, freq in self._word_list]
            word, _freq = random.choices(self._word_list, weights=weights, k=1)[0]

            added_length = len(word) + (1 if words else 0)  # +1 for the space
            if total_length + added_length > app_settings.get_string_length() and words:
                break

            words.append(word)
            total_length += added_length

        return " ".join(words)

    def _get_word_weight(self, word: str, freq: int) -> float:
        freq_score = math.log10(freq + 1)

        mistake_score = 0
        for c in word:
            stat = self._char_stats.get_stat(c)
            mistake_score += stat["miss"] * MISS_WEIGHT + stat["slow"] * SLOW_WEIGHT

        return freq_score + mistake_score

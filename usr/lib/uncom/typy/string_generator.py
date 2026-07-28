import math
import random

MISS_WEIGHT = 2
SLOW_WEIGHT = 1


class StringGenerator:
    def __init__(self, word_list: list[tuple[str, int]], char_stats):
        self._word_list = word_list
        self._char_stats = char_stats

    def generate(self, word_count: int = 5) -> str:
        weights = [self._get_word_weight(w, freq) for w, freq in self._word_list]
        chosen = [
            w
            for w, freq in random.choices(
                self._word_list, weights=weights, k=word_count
            )
        ]
        return " ".join(chosen)

    def _get_word_weight(self, word: str, freq: int) -> float:
        freq_score = math.log10(freq + 1)

        mistake_score = 0
        for c in word:
            stat = self._char_stats.get_stat(c)
            mistake_score += stat["miss"] * MISS_WEIGHT + stat["slow"] * SLOW_WEIGHT

        return freq_score + mistake_score

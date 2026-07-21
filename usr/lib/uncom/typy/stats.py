import json
import os
import random
from collections import defaultdict

from constants import STATS_FILE


def load_missed_char_counts():
    try:
        with open(STATS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return defaultdict(int, data)
    except (FileNotFoundError, json.JSONDecodeError):
        return defaultdict(int)


missed_char_counts = load_missed_char_counts()


def ensure_folder_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def save_missed_char_counts():
    ensure_folder_exists(os.path.dirname(STATS_FILE))
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(missed_char_counts, f)


def reset_missed_char_counts():
    missed_char_counts.clear()
    if os.path.exists(STATS_FILE):
        os.remove(STATS_FILE)


def generate_string(word_list, word_count=5):
    def word_weight(word):
        return 1 + sum(missed_char_counts.get(c, 0) for c in word)

    weights = [word_weight(w) for w in word_list]
    chosen = random.choices(word_list, weights=weights, k=word_count)
    return " ".join(chosen)

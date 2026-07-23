import csv
import os


def ensure_folder_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def delete_file_if_exists(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


def load_word_list(path):
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [(row["word"], int(row["frequency"])) for row in reader]

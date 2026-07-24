import csv
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
RAW_DIR = os.path.join(SCRIPT_DIR, "raw")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "usr", "share", "uncom", "typy", "words")


def convert(input_path, output_path, top_n=2000):
    with open(input_path, "r", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        rows = [(row["ngram"], int(row["freq"])) for row in reader][:top_n]

    with open(output_path, "w", encoding="utf-8", newline="") as f_out:
        writer = csv.writer(f_out)
        writer.writerow(["word", "frequency"])
        writer.writerows(rows)


if __name__ == "__main__":
    convert(
        os.path.join(RAW_DIR, "1grams_english.csv"),
        os.path.join(OUTPUT_DIR, "words_en.csv"),
    )
    # convert(os.path.join(RAW_DIR, "1grams_russian.csv"), os.path.join(OUTPUT_DIR, "words_ru.csv"))

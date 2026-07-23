import csv


def convert(input_path, output_path, top_n=2000):
    with open(input_path, "r", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        rows = [(row["ngram"], int(row["freq"])) for row in reader][:top_n]

    with open(output_path, "w", encoding="utf-8", newline="") as f_out:
        writer = csv.writer(f_out)
        writer.writerow(["word", "frequency"])
        writer.writerows(rows)


convert(
    "/home/strigz/typy/usr/lib/uncom/typy/words/raw/1grams_english.csv",
    "/home/strigz/typy/usr/lib/uncom/typy/words/converted/words_en.csv",
)
# convert("1grams_russian.csv", "words_ru.csv")

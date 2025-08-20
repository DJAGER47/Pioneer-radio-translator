import json
import argparse
import sys


def check_translations(input_file, percent_threshold):
    """
    Проверяет длину перевода относительно оригинала
    """
    with open(input_file, "r", encoding="utf-16le") as f:
        data = json.load(f)

    for item in data:
        if item["translation"] == "":
            continue

        original_len = len(item["original"])
        translation_len = len(item["translation"])

        if original_len < 3:
            continue

        percent_ok = True
        if original_len > 0:
            translation_percent = (translation_len * 100) / original_len
            percent_ok = translation_percent >= percent_threshold

        if not percent_ok:
            all_correct = False
            print(
                f"⚠️  {item['index']} | "
                f"Перевод ({translation_percent:.0f}%) меньше {percent_threshold}% | "
                f"'{item['original']}' -> '{item['translation']}'"
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Проверка длины переводов")
    parser.add_argument(
        "-i", "--input", required=True, help="Файл с переводами для проверки"
    )
    parser.add_argument(
        "-p",
        "--percent",
        type=int,
        default=70,
        help="Минимальный процент длины перевода от оригинала",
    )

    args = parser.parse_args()
    check_translations(args.input, args.percent)

import json
import argparse
import re
import sys


def extract_format_strings(text):
    """
    Извлекает все форматные строки из текста (например, %s, %d, %x и т.д.)
    """
    # Регулярное выражение для поиска форматных строк
    format_pattern = r"%[diouxXeEfFgGaAcspn%]"
    return re.findall(format_pattern, text)


def count_newlines(text):
    """
    Подсчитывает количество переносов строк в тексте
    """
    return text.count("\n")


def check_translations(input_file):
    """
    Проверяет корректность переводов по длине строк и соответствию форматных строк
    """

    with open(input_file, "r", encoding="utf-16le") as f:
        data = json.load(f)

    all_correct = True
    skip = 0

    for item in data:

        if item["translation"] == "":
            # print(f"⚠️ Внимание нет перевода: '{item['original']}'")
            skip += 1
            continue

        original_len = len(item["original"]) * 2
        translation_len = len(item["translation"]) * 2
        expected_size = int(item["size"], 16)

        # Проверяем соответствие длин
        size_ok = original_len == expected_size
        len_ok = (
            0 < translation_len <= original_len
        )  # Перевод может быть короче оригинала, но не пустым

        # Проверяем соответствие форматных строк
        original_formats = extract_format_strings(item["original"])
        translation_formats = extract_format_strings(item["translation"])
        formats_ok = original_formats == translation_formats

        # Проверяем количество переносов строк
        original_newlines = count_newlines(item["original"])
        translation_newlines = count_newlines(item["translation"])
        newlines_ok = original_newlines == translation_newlines

        if not (size_ok and len_ok and formats_ok and newlines_ok):
            all_correct = False
            if not formats_ok:
                print(
                    f"❌ Формат: {item['size']} | "
                    f"'{item['original']}' -> '{item['translation']}' | "
                    f"Оригинал: {original_formats} | Перевод: {translation_formats}"
                )
            elif not newlines_ok:
                print(
                    f"❌ Переносы: {item['size']} | "
                    f"'{item['original']}' -> '{item['translation']}' | "
                    f"Оригинал: {original_newlines} | Перевод: {translation_newlines}"
                )
            else:
                print(
                    f"❌ Размер: {item['size']}({original_len:03}) | "
                    f"'{item['original']}':{original_len} -> '{item['translation']}':{translation_len}"
                )
        # else:
        # print(f"✅ {item['original']} -> {item['translation']}")

    if all_correct:
        print(
            f"✅ Все переводы корректны (размер, форматные строки и переносы)! ⚠️  Пропущено {skip}"
        )
    else:
        print(
            "❌ Обнаружены ошибки в переводах (размер, форматные строки или переносы)"
        )
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Проверка корректности переводов")
    parser.add_argument(
        "-i", "--input", required=True, help="Файл с переводами для проверки"
    )

    args = parser.parse_args()
    check_translations(args.input)

import argparse
import json
import sys
import re


def read_mode(input_file, index):
    """Режим чтения: выводит запись-оригинал-текст"""
    if index < 0:
        print("Ошибка: индекс не может быть отрицательным")
        sys.exit(1)

    with open(input_file, "r", encoding="utf-16") as f:
        data = json.load(f)

    try:
        item = data[index]
    except IndexError:
        print(f"Индекс {index} вне диапазона (максимум {len(data)-1})")
        sys.exit(1)

    print(
        f"Запись #{index}: len {int(item['size'], 16)/2}"
        f"\nОригинал: {item['original']}"
        f"\nПеревод: {item['translation']}"
    )


def extract_placeholders(text):
    """Извлекает все подстановки вида %d, %x, %s и т.д. из текста"""
    # Регулярное выражение для поиска подстановок
    pattern = r"%[diouxXeEfFgGaAcspn%]"
    return re.findall(pattern, text)


def write_mode(input_file, index, new_translation):
    """Режим записи: записывает текст в поле translation с проверками"""
    if index < 0:
        print("Ошибка: индекс не может быть отрицательным")
        sys.exit(1)

    with open(input_file, "r", encoding="utf-16") as f:
        data = json.load(f)

    try:
        item = data[index]
    except IndexError:
        print(f"Индекс {index} вне диапазона (максимум {len(data)-1})")
        sys.exit(1)

    max_length = int(item["size"], 16) / 2
    if len(new_translation) > max_length:
        print(f"Новый перевод длинный-максимум {max_length}")
        sys.exit(1)

    # Проверка соответствия подстановок
    original_placeholders = extract_placeholders(item["original"])
    translation_placeholders = extract_placeholders(new_translation)

    if original_placeholders != translation_placeholders:
        print(
            f"Несовпадение подстановок между оригиналом и переводом"
            f"\nОригинал: {original_placeholders}"
            f"\nПеревод: {translation_placeholders}"
        )
        sys.exit(1)

    # Проверка количества переносов строк
    original_newlines = item["original"].count("\n")
    translation_newlines = new_translation.count("\n")

    if original_newlines != translation_newlines:
        print(
            f"Несовпадение количества переносов"
            f"\nОригинал: {original_newlines}"
            f"\nПеревод: {translation_newlines}"
        )
        sys.exit(1)

    item["translation"] = new_translation

    with open(input_file, "w", encoding="utf-16") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Успешно, переводи {index + 1}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Редактор переводов в JSON файле")
    parser.add_argument("-i", "--input", required=True, help="Входной JSON файл")
    parser.add_argument(
        "-n",
        "--index",
        required=True,
        type=int,
        help="Индекс записи для редактирования",
    )
    parser.add_argument(
        "-r",
        "--read",
        action="store_true",
        help="Режим чтения (выводит запись-оригинал-текст)",
    )
    parser.add_argument(
        "-w", "--write", help="Режим записи (записывает текст в поле translation)"
    )

    args = parser.parse_args()

    # Проверяем, что указан один из режимов -r или -w
    if not args.read and not args.write:
        print("Необходимо указать один из режимов -r или -w")
        sys.exit(1)

    if args.read and args.write:
        print("Нельзя одновременно использовать режимы -r и -w")
        sys.exit(1)

    if args.read:
        read_mode(args.input, args.index)
    elif args.write:
        write_mode(args.input, args.index, args.write)

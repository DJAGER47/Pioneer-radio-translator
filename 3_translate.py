#!/usr/bin/env python3
import argparse
import json
import struct


def main():
    parser = argparse.ArgumentParser(
        description="Replace text in binary file using translations"
    )
    parser.add_argument("-i", "--input", required=True, help="Input file")
    parser.add_argument(
        "-t", "--translations", required=True, help="JSON translations file"
    )
    parser.add_argument("-o", "--output", required=True, help="Output file")
    args = parser.parse_args()

    with open(args.translations, "r", encoding="utf-16le") as f:
        translations = json.load(f)

    with open(args.input, "rb") as f:
        data = bytearray(f.read())

    count = 0
    skip = 0
    add = 0
    for item in translations:
        if not all(
            key in item for key in ["address", "original", "size", "translation"]
        ):
            print(f"❌ Ошибка: Сломан {args.translations}")
            exit(1)

        address = int(item["address"], 16)
        original = item["original"].encode("utf-16le")
        size = int(item["size"], 16)
        translation = item["translation"].encode("utf-16le")

        original_in_file = data[address : address + size]
        if original_in_file != original:
            print(f"❌ Ошибка: Не соответствует оригинальный текст {original_in_file}")
            exit(1)

        # Verify translation size
        if len(translation) > size:
            print(f"❌ Ошибка: Перевод слишком большой {translation}")
            exit(1)

        if len(translation) == 0 or translation == "":
            # пропускаем, перевода нету
            skip += 1
            continue

        if len(translation) < size:
            # Дополняем " ", перевод короче
            translation += b"\x00" * (size - len(translation))
            add += 1

        data[address : address + size] = translation
        count += 1

    with open(args.output, "wb") as f:
        f.write(data)

    print(f"✅ Перевели строк {count}! ⚠️  Пропустили {skip}, дополняли нулями {add}")


if __name__ == "__main__":
    main()

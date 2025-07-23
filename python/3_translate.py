#!/usr/bin/env python3
import argparse
import json
import struct

def main():
    parser = argparse.ArgumentParser(description='Replace text in binary file using translations')
    parser.add_argument('-i', '--input', required=True, help='Input file')
    parser.add_argument('-t', '--translations', required=True, help='JSON translations file')
    parser.add_argument('-o', '--output', required=True, help='Output file')
    args = parser.parse_args()

    with open(args.translations, 'r', encoding='utf-16-le') as f:
        translations = json.load(f)

    with open(args.input, 'rb') as f:
        data = bytearray(f.read())

    for item in translations:
        if not all(key in item for key in ['address', 'original', 'size', 'translation']):
            print(f"❌ Ошибка: Сломан {args.translations}")
            exit(-1)

        address = int(item['address'], 16)
        original = item['original'].encode('utf-16-le')
        size = int(item['size'], 16)
        translation = item['translation'].encode('utf-16-le')


        original_in_file = data[address:address+size]
        if original_in_file != original:
            print(f"❌ Ошибка: Не соответствует оригинальный текст {original_in_file}")
            exit(-1)

        # Verify translation size
        if len(translation) > size:
            print(f"❌ Ошибка: Перевод слишком большой {translation}"
            exit(-1)

        if translation == "":
            # пропускаем, перевода нету
            continue

        if len(translation) < size:
            # Дополняем " ", перевод короче
            translation += b'\x00' * (size - len(translation))

        data[address:address+size] = translation


    with open(args.output, 'wb') as f:
        f.write(data)

if __name__ == '__main__':
    main()
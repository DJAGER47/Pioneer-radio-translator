import re
import json
import argparse


def parse_translation_file(input_file, output_file):
    with open(input_file, "r", encoding="utf-16le") as f:
        content = f.read()

    # Регулярное выражение для разбора строк
    pattern = re.compile(r"([0-9A-F]+)\t(.*?)\t(.*?)(?=\n[0-9A-F]+\t|\Z)", re.DOTALL)

    entries = []
    for match in pattern.finditer(content):
        size = match.group(1)
        original = match.group(2).replace("\r\n", "\n").strip()
        translation = match.group(3).replace("\r\n", "\n").strip()

        entries.append({"size": size, "original": original, "translation": translation})

    with open(output_file, "w", encoding="utf-16le") as f:
        json.dump(entries, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parse translation file from UTF-16 LE format"
    )
    parser.add_argument(
        "-i",
        "--input",
        default="translation.txt",
        help="Input file name (default: translation.txt)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="translation.json",
        help="Output file name (default: translation.json)",
    )

    args = parser.parse_args()
    parse_translation_file(args.input, args.output)

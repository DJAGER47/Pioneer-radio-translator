import argparse


def trim_file(input_file, output_file):
    try:
        with open(input_file, "rb") as f_in:
            # Пропускаем первые 512 байт (0x200)
            f_in.seek(0x200)
            data = f_in.read()

        with open(output_file, "wb") as f_out:
            f_out.write(data)

        print(f"Файл успешно обработан. Результат сохранен в {output_file}")

    except FileNotFoundError:
        print(f"Ошибка: файл {input_file} не найден")
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Обрезает первые 0x200 байт файла")
    parser.add_argument("-i", "--input", required=True, help="Входной файл")
    parser.add_argument("-o", "--output", required=True, help="Выходной файл")

    args = parser.parse_args()
    trim_file(args.input, args.output)

import argparse
import json
import sys

def read_mode(input_file, index):
    """Режим чтения: выводит запись-оригинал-текст"""
    if index < 0:
        print("Ошибка: индекс не может быть отрицательным")
        sys.exit(1)
    
    with open(input_file, 'r', encoding='utf-16-le') as f:
        data = json.load(f)
    
    try:
        item = data[index]
    except IndexError:
        print(f"Индекс {index} вне диапазона (максимум {len(data)-1})")
        sys.exit(1)
    
    print(f"Запись #{index}: len {int(item['size'], 16)/2}"
          f"\nОригинал: {item['original']}"
          f"\n Перевод: {item['translation']}")

def write_mode(input_file, index, new_translation):
    """Режим записи: записывает текст в поле translation с проверками"""
    if index < 0:
        print("Ошибка: индекс не может быть отрицательным")
        sys.exit(1)
    
    with open(input_file, 'r', encoding='utf-16-le') as f:
        data = json.load(f)
    
    try:
        item = data[index]
    except IndexError:
        print(f"Индекс {index} вне диапазона (максимум {len(data)-1})")
        sys.exit(1)
    
    max_length = int(item['size'], 16) / 2
    if len(new_translation) > max_length:
        print(f"Ошибка: новый перевод слишком длинный (максимум {max_length} символов)")
        sys.exit(1)
    
    item['translation'] = new_translation
    
    with open(input_file, 'w', encoding='utf-16-le') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"Запись #{index} успешно обновлена")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Редактор переводов в JSON файле')
    parser.add_argument('-i', '--input', required=True, help='Входной JSON файл')
    parser.add_argument('-n', '--index', required=True, type=int, help='Индекс записи для редактирования')
    parser.add_argument('-r', '--read', action='store_true', help='Режим чтения (выводит запись-оригинал-текст)')
    parser.add_argument('-w', '--write', help='Режим записи (записывает текст в поле translation)')
    
    args = parser.parse_args()
    
    # Проверяем, что указан один из режимов -r или -w
    if not args.read and not args.write:
        print("Ошибка: необходимо указать один из режимов -r или -w")
        sys.exit(1)
    
    if args.read and args.write:
        print("Ошибка: нельзя одновременно использовать режимы -r и -w")
        sys.exit(1)
    
    if args.read:
        read_mode(args.input, args.index)
    elif args.write:
        write_mode(args.input, args.index, args.write)
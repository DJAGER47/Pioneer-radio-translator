import json
import re
import argparse

def has_japanese(text):
    """Проверяет наличие японских символов в тексте"""
    return bool(re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', text))

def filter_and_sort_japanese(input_path, japanese_output, other_output):
    """Разделяет записи на японские и остальные"""
    try:
        with open(input_path, 'r', encoding='utf-16-le') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Ошибка: файл {input_path} не найден")
        print("Убедитесь, что вы указали правильный путь к файлу")
        return
    
    # Разделение записей
    japanese_entries = []
    other_entries = []
    
    for entry in data:
        if has_japanese(entry['original']):
            japanese_entries.append(entry)
        else:
            other_entries.append(entry)
    
    # Сортировка
    japanese_sorted = sorted(japanese_entries, key=lambda x: x['original'])
    other_sorted = sorted(other_entries, key=lambda x: x['original'])
    
    print(f"Японских строк: {len(japanese_sorted)}")
    print(f"Остальных строк: {len(other_sorted)}")
    
    # Сохранение
    with open(japanese_output, 'w', encoding='utf-16-le') as f:
        json.dump(japanese_sorted, f, ensure_ascii=False, indent=4)
    
    with open(other_output, 'w', encoding='utf-16-le') as f:
        json.dump(other_sorted, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Разделение строк на японские и остальные')
    parser.add_argument('-i', '--input', required=True, help='Входной JSON файл')
    parser.add_argument('-j', '--japanese', required=True, help='Файл для японских строк')
    parser.add_argument('-o', '--other', required=True, help='Файл для остальных строк')
    
    args = parser.parse_args()
    filter_and_sort_japanese(args.input, args.japanese, args.other)
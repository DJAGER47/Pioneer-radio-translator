import json
import argparse

def merge_translations(original_path, translated_path, output_path):
    """
    Сопоставляет оригинальные тексты и добавляет переводы
    """
    # Читаем оба файла
    with open(original_path, 'r', encoding='utf-16-le') as f:
        originals = json.load(f)
    
    with open(translated_path, 'r', encoding='utf-16-le') as f:
        translations = json.load(f)

    # Создаем словарь для быстрого поиска переводов
    trans_dict = {item['original']: item['translation'] 
                 for item in translations if item['translation']}

    # Добавляем переводы в оригинальный файл
    for item in originals:
        if item['original'] in trans_dict:
            item['translation'] = trans_dict[item['original']]

    # Сохраняем результат
    with open(output_path, 'w', encoding='utf-16-le') as f:
        json.dump(originals, f, ensure_ascii=False, indent=4)

    print(f"Сопоставлено {len(trans_dict)} переводов. Результат сохранен в {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Сопоставление готовых переводов')
    parser.add_argument('-i', '--input', required=True, help='Файл для перевода (оригиналы)')
    parser.add_argument('-t', '--translated', required=True, help='Файл с готовыми переводами')
    parser.add_argument('-o', '--output', required=True, help='Выходной файл с объединенными данными')
    
    args = parser.parse_args()
    merge_translations(args.input, args.translated, args.output)
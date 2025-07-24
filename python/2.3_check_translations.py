import json
import argparse

def check_translations(input_file):
    """
    Проверяет корректность переводов по длине строк
    """
    
    with open(input_file, 'r', encoding='utf-16-le') as f:
        data = json.load(f)
    
    all_correct = True
    skip = 0
    
    for item in data:
            
        if item['translation'] == "":
            # print(f"⚠️ Внимание нет перевода: '{item['original']}'")
            skip += 1
            continue
            
        original_len = len(item['original']) * 2
        translation_len = len(item['translation']) * 2
        expected_size = int(item['size'], 16)
        
        # Проверяем соответствие длин
        size_ok = (original_len == expected_size)
        len_ok = (0 < translation_len <= original_len)  # Перевод может быть короче оригинала, но не пустым
        
        if not (size_ok and len_ok):
            all_correct = False
            print(f"❌ Размер: {item['size']}({original_len:03}) | "
                  f"'{item['original']}':{original_len} -> '{item['translation']}':{translation_len}")
        # else:
            # print(f"✅ {item['original']} -> {item['translation']}")
    
    if all_correct:
        print(f"✅ Все переводы корректны! ⚠️  Пропущено {skip}")
    else:
        print("❌ Обнаружены ошибки в переводах")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Проверка корректности переводов')
    parser.add_argument('-i', '--input', required=True, help='Файл с переводами для проверки')
    
    args = parser.parse_args()
    check_translations(args.input)
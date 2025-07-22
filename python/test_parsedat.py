import os
import subprocess
import filecmp

def compile_c_program():
    """Компиляция оригинальной C-программы если нужно"""
    if not os.path.exists('../parsedat'):
        print("Компиляция parsedat.c...")
        result = subprocess.run(['gcc', '../C/parsedat.c', '-o', '../parsedat'], capture_output=True)
        if result.returncode != 0:
            print("Ошибка компиляции:")
            print(result.stderr.decode())
            return False
    return True

def run_tests():
    """Запуск тестов"""
    # Запуск C-версии
    if compile_c_program():
        subprocess.run(['../parsedat'], check=True)
        os.rename('parsed1.txt', 'parsed1_c.txt')
    
    # Запуск Python-версии
    subprocess.run(['python', 'parsedat_to_string.py'], check=True)
    os.rename('parsed1.txt', 'parsed1_py.txt')
    
    # Сравнение результатов
    if filecmp.cmp('parsed1_c.txt', 'parsed1_py.txt', shallow=False):
        print("✅ Тест пройден: файлы идентичны")
        return True
    else:
        print("❌ Тест не пройден: файлы различаются")
        return False

if __name__ == "__main__":
    if run_tests():
        # Удаляем временные файлы при успешном тесте
        # os.remove('parsed1_c.txt')
        # os.remove('parsed1_py.txt')
        exit(0)
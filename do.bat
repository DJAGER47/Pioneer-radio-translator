@echo off
echo ВНИМАНИЕ: Этот скрипт do.bat автоматически сконвертирован из do.sh и не был полностью протестирован!
echo Пожалуйста, проверьте его работу перед использованием.
echo.
rem Проверка наличия параметра
if "%1"=="" (
    echo Использование: %0 ^<путь_к_файлу_PS140PLT.PRG^>
    exit /b 1
)

set WORK_DIR="%~dp0work"
set PATCHED_DIR="%WORK_DIR%\patched"

del /q "%WORK_DIR%\*"

md "%WORK_DIR%"
md "%WORK_DIR%\out"
md "%WORK_DIR%\DUMP"
md "%PATCHED_DIR%"

copy %1 "%WORK_DIR%\PS140PLT.PRG"

echo --Отрезаем header 0x200
python 1_trim_file.py -i "%WORK_DIR%\PS140PLT.PRG" -o "%WORK_DIR%\output.nb0"

echo --Распаковываем образ в DUMP
dumpromx.exe -d "%WORK_DIR%\DUMP" -v -5 "%WORK_DIR%\output.nb0" > "%WORK_DIR%\output.txt"
echo --Копируем нужное и удаляем не нужное
copy "%WORK_DIR%\DUMP\initDB.dat" "%WORK_DIR%\initDB_original.dat"
rd /s /q "%WORK_DIR%\DUMP"
del "%WORK_DIR%\output.txt"

echo --Находим все строки в образе
python 2_find_str.py -i "%WORK_DIR%\initDB_original.dat" -o "%WORK_DIR%\finded_str.json"

echo --Перегоняем в json базу с 4pda (не обязательно)
python 2.1_txt2json.py -i translation.txt -o "%WORK_DIR%\4pda_translation.json"

echo --Подсовываем в текст нашей магнитолы переводы из 4pda (не обязательно)
python 2.2_merge_translations.py -i "%WORK_DIR%\finded_str.json" -t "%WORK_DIR%\4pda_translation.json" -o "%WORK_DIR%\merge_4pda.json"

echo --Добавляем к пустым переводам, перевод нейросетки
python 2.3_add_translations.py -i "%WORK_DIR%\merge_4pda.json" -t "translate_gpt.json" -o "%WORK_DIR%\merge_4pda_gpt.json"

echo --Проверяем перевод
python 2.4a_check_translations.py -i "%WORK_DIR%\merge_4pda_gpt.json"

echo --Проверяем длинну строк (опционально)
python 2.4b_check_length.py -i "%WORK_DIR%\merge_4pda_gpt.json" -p 50

echo --Подменяем переводы в базе данных
python 3_translate.py -i "%WORK_DIR%\initDB_original.dat" -t "%WORK_DIR%\merge_4pda_gpt.json" -o "%PATCHED_DIR%\initDB.dat"

echo --Подменяем в нашем образе файл
copy "%WORK_DIR%\output.nb0" "%PATCHED_DIR%\output.nb0"

cd %PATCHED_DIR% && ..\..\dumpromx.exe -a initDB.dat output.nb0
del output.nb0
ren initDB.dat.nb output.nb0
cd ..\..

echo --Создаем выходные файлы
python 4_makever.py
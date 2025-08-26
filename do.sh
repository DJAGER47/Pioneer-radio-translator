#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Использование: $0 <путь_к_файлу_PS140PLT.PRG>"
    exit 1
fi

WORK_DIR="$(pwd)/work"
PATCHED_DIR="$WORK_DIR/patched"

rm -r "$WORK_DIR/"

mkdir "$WORK_DIR"
mkdir "$WORK_DIR/out"
mkdir "$WORK_DIR/DUMP"
mkdir "$PATCHED_DIR"

cp "$1" "$WORK_DIR/PS140PLT.PRG"

echo "--Отрезаем header 0x200"
python 1_trim_file.py -i "$WORK_DIR/PS140PLT.PRG" -o "$WORK_DIR/output.nb0"

echo "--Распаковываем образ в DUMP"
wine dumpromx.exe -d "$WORK_DIR/DUMP" -v -5 "$WORK_DIR/output.nb0" > "$WORK_DIR/output.txt"
echo "--Копируем нужное и удаляем не нужное"
cp "$WORK_DIR/DUMP/initDB.dat" "$WORK_DIR/initDB_original.dat"
rm -r "$WORK_DIR/DUMP" "$WORK_DIR/output.txt"

echo "--Находим все строки в образе"
python 2_find_str.py -i "$WORK_DIR/initDB_original.dat" -o "$WORK_DIR/finded_str.json"

echo "--Перегоняем в json базу с 4pda (не обязательно)"
python 2.1_txt2json.py -i translation.txt -o "$WORK_DIR/4pda_translation.json"

echo "--Подсовываем в текст нашей магнитолы переводы из 4pda (не обязательно)"
python 2.2_merge_translations.py -i "$WORK_DIR/finded_str.json" -t "$WORK_DIR/4pda_translation.json" -o "$WORK_DIR/merge_4pda.json"

echo "--Добавляем/переписываем переводы нейросети"
python 2.3_add_translations.py -i "$WORK_DIR/merge_4pda.json" -t "translate_gpt.json" -o "$WORK_DIR/merge_4pda_gpt.json"

echo "--Проверяем перевод"
python 2.4a_check_translations.py -i "$WORK_DIR/merge_4pda_gpt.json"

echo "--Проверяем длинну строк (опционально)"
python 2.4b_check_length.py -i "$WORK_DIR/merge_4pda_gpt.json" -p 50

echo "--Подменяем переводы в базе данных"
python 3_translate.py -i "$WORK_DIR/initDB_original.dat" -t "$WORK_DIR/merge_4pda_gpt.json" -o "$PATCHED_DIR/initDB.dat"

echo "--Подменяем в нашем образе файл"
cp "$WORK_DIR/output.nb0" "$PATCHED_DIR/output.nb0"

cd $PATCHED_DIR && wine ../../dumpromx.exe -a initDB.dat output.nb0
rm output.nb0
mv initDB.dat.nb output.nb0
cd ../..

echo "--Создаем выходные файлы"
python 4_makever.py

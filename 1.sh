#!/bin/bash

WORK_DIR="$(pwd)/work"
PATCHED_DIR="$WORK_DIR/patched"

rm -r "$WORK_DIR"/*
mkdir "$WORK_DIR/DUMP"
mkdir "$PATCHED_DIR"

cp /home/plavrovskiy/Downloads/jap/AVICRZ09/PLATFORM/PS140PLT.PRG "$WORK_DIR"

# Отрезаем header 0x200
python 1_trim_file.py -i "$WORK_DIR/PS140PLT.PRG" -o "$WORK_DIR/output.nb0"
# Разпаковывем образ в DUMP
wine dumpromx.exe -d "$WORK_DIR/DUMP" -v -5 "$WORK_DIR/output.nb0" > "$WORK_DIR/output.txt"
# копируем нужное и удаляем не нужное
cp "$WORK_DIR/DUMP/initDB.dat" "$WORK_DIR/initDB_original.dat"
rm -rf "$WORK_DIR/DUMP" "$WORK_DIR/output.txt"

# Находим все строки в образе
python 2_find_str.py -i "$WORK_DIR/initDB_original.dat" -o "$WORK_DIR/finded_str.json"

# Перегоняем в json базу с 4pda (не обязательно)
python 2.1_txt2json.py -i translation.txt -o "$WORK_DIR/4pda_translation.json"
# Подсовываем в текст нашей магнитолы переводы из 4pda (не обязательно)
python 2.2_merge_translations.py -i "$WORK_DIR/finded_str.json" -t "$WORK_DIR/4pda_translation.json" -o "$WORK_DIR/merge.json"
# проверяем перевод
python 2.3_check_translations.py -i "$WORK_DIR/merge.json"
# Скрипт для нейросети и перевода
# python 2.4_edit_translation.py -n 0 -i work/merge.json -o work/merge_edit.json

# Подменяем переводы в базе данных
python 3_translate.py -i "$WORK_DIR/initDB_original.dat" -t "$WORK_DIR/merge.json" -o "$PATCHED_DIR/initDB.dat"

# Подменяем в нашем образе файл
cp "$WORK_DIR/output.nb0" "$PATCHED_DIR/output.nb0"
wine ../dumpromx.exe -a "$PATCHED_DIR/initDB.dat" "$PATCHED_DIR/output.nb0"
# # rm -f output.nb0
# mv -f initDB.dat.nb output.nb0
# ../makever
# mkdir -p NAVIVUP/AVICRZ09/PLATFORM
# cp -f PS140PLT.PRG NAVIVUP/AVICRZ09/PLATFORM/PS140PLT.PRG
# cp -f PS140PLT.VER NAVIVUP/AVICRZ09/PS140PLT.VER
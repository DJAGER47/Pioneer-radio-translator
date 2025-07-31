#!/bin/bash

# Проверка количества аргументов
if [ $# -ne 2 ]; then
    echo "Использование: $0 <файл1> <файл2>"
    exit 1
fi

FILE1="$1"
FILE2="$2"

# Проверка существования файлов
if [ ! -f "$FILE1" ]; then
    echo "Ошибка: Файл '$FILE1' не существует"
    exit 1
fi

if [ ! -f "$FILE2" ]; then
    echo "Ошибка: Файл '$FILE2' не существует"
    exit 1
fi

# Проверка хешсумм файлов через sha256
HASH1=$(sha256sum "$FILE1" | cut -d' ' -f1)
HASH2=$(sha256sum "$FILE2" | cut -d' ' -f1)

if [ "$HASH1" = "$HASH2" ]; then
    echo "Файлы идентичны (хешсуммы совпадают)"
    exit 0
fi

# Создание временных файлов для hex дампов
TEMP1=$(mktemp)
TEMP2=$(mktemp)

# Создание hex дампов первых 16 байт
xxd -g 1 -c 16 "$FILE1" > "$TEMP1"
xxd -g 1 -c 16 "$FILE2" > "$TEMP2"

# Запуск meld с файлами hex дампов
meld "$TEMP1" "$TEMP2"

# Удаление временных файлов после закрытия meld
rm -f "$TEMP1" "$TEMP2"
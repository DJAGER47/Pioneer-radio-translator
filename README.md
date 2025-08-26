# Проект локализации прошивки Pioneer / Pioneer Firmware Localization Project

## Описание проекта / Project Description

Данный проект предназначен для локализации (перевода) прошивок автомобильных магнитол Pioneer. Он позволяет извлекать текстовые строки из бинарного файла прошивки, применять к ним переводы и создавать модифицированную версию прошивки с локализованным интерфейсом.

This project is designed to localize (translate) firmware for Pioneer car stereos. It allows extracting text strings from the firmware binary file, applying translations to them, and creating a modified version of the firmware with a localized interface.

## Использование / Usage

Для запуска процесса локализации выполните:
To start the localization process, run:

```bash
./do.sh <путь_к_файлу_PS140PLT.PRG>
```

Где `<путь_к_файлу_PS140PLT.PRG>` - это путь к оригинальному файлу прошивки магнитолы Pioneer.
Where `<путь_к_файлу_PS140PLT.PRG>` is the path to the original Pioneer stereo firmware file.

## Как это работает / How it works

Процесс локализации включает следующие этапы:
The localization process includes the following stages:

1. Отрезание заголовка файла прошивки (0x200 байт)
   Trimming the firmware file header (0x200 bytes)

2. Распаковка образа с помощью dumpromx.exe
   Unpacking the image using dumpromx.exe

3. Извлечение текстовых строк из базы данных initDB.dat
   Extracting text strings from the initDB.dat database

4. Применение переводов из различных источников:
   - Переводы с форума 4pda (опционально)
   - Переводы от нейросети GPT (translate_gpt.json)
   Applying translations from various sources:
   - Translations from 4pda forum (optional)
   - Translations from GPT neural network (translate_gpt.json)

5. Проверка корректности переводов
   Verifying translation correctness

6. Замена оригинальных строк на переведенные в бинарном файле
   Replacing original strings with translated ones in the binary file

7. Создание модифицированного образа прошивки
   Creating a modified firmware image

## Отказ от ответственности / Disclaimer

### На русском языке

Данное программное обеспечение предоставляется "как есть", без каких-либо гарантий, явных или подразумеваемых, включая, но не ограничиваясь, гарантии товарной пригодности, соответствия определенному назначению и отсутствия нарушений прав. Ни при каких обстоятельствах авторы или правообладатели не несут ответственности за любые прямые, косвенные, случайные, специальные, EXEMPLARY или косвенные убытки (включая, но не ограничиваясь, приобретением заменяющих товаров или услуг; потеря данных или прибыли; или прерывание деловой активности), возникшие каким-либо образом из-за использования или иных действий с данным программным обеспечением, даже если это было сообщено о возможности таких убытков.

### In English

This software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the software.
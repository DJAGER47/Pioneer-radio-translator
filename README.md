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

## ⚠️ Отказ от ответственности / Disclaimer

### На русском языке

**Данное программное обеспечение предоставляется "как есть" без каких-либо гарантий.**

#### ⚠️ Важные предупреждения:
- **Модификация прошивки может привести к полной неработоспособности устройства**
- **Неправильное использование может вызвать необратимые повреждения магнитолы**
- **Восстановление устройства после неудачной прошивки может быть невозможно**

#### 🔧 Риски модификации прошивки:
- Потеря функциональности устройства ("окирпичивание")
- Нарушение работы системных компонентов
- Несовместимость с оригинальными обновлениями
- Потеря данных и настроек

**Автор не несет ответственности за любые повреждения или убытки, возникшие в результате использования данного программного обеспечения.**

---

### In English

**This software is provided "as is" without any warranties of any kind.**

#### ⚠️ Important Warnings:
- **Firmware modification may result in complete device malfunction**
- **Improper use may cause irreversible damage to the stereo**
- **Device recovery after failed firmware installation may be impossible**
- **Using modified firmware may void your warranty**

#### 🔧 Firmware Modification Risks:
- Device bricking (complete loss of functionality)
- System component malfunction
- Incompatibility with original updates
- Data and settings loss

**The authors are not responsible for any damage or losses resulting from the use of this software.**

---

**📄 License:** This project does not include a specific license file. Use at your own risk and responsibility.
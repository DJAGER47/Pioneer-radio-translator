import os
import re
import csv
import hashlib
import argparse
import psutil
import time
import signal
from tqdm import tqdm
from collections import defaultdict
from multiprocessing import Pool, cpu_count, Manager, Process, Event, current_process
import pathlib

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
    GUI_AVAILABLE = True
except:
    GUI_AVAILABLE = False

OUTPUT_DIR = "extracted_strings"
LOG_SUBDIR = os.path.join(OUTPUT_DIR, "logs")
LOG_FILE = os.path.join(LOG_SUBDIR, "extract_log.csv")
DUPLICATES_FILE = os.path.join(LOG_SUBDIR, "duplicate_strings.csv")
SKIPPED_FILE = os.path.join(LOG_SUBDIR, "skipped_files.txt")
MIN_LENGTH = 6

SKIP_FILES = {
    "HMI_BinaryDatabaseDisp.123",
    "HMI_BinaryDatabaseNavi.123"
}

def file_hash(path):
    h = hashlib.sha1()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def decode_utf16_strings(data):
    strings = []
    le_pattern = rb'(?:[\x20-\x7E]\x00){%d,}' % MIN_LENGTH
    for m in re.finditer(le_pattern, data):
        try:
            s = m.group(0).decode('utf-16le')
            offset = f"0x{m.start():X}"
            strings.append((s, offset, 'utf-16le'))
        except:
            continue
    be_pattern = rb'(?:\x00[\x20-\x7E]){%d,}' % MIN_LENGTH
    for m in re.finditer(be_pattern, data):
        try:
            s = m.group(0).decode('utf-16be')
            offset = f"0x{m.start():X}"
            strings.append((s, offset, 'utf-16be'))
        except:
            continue
    return strings

def contains_japanese(text):
    return any('\u3040' <= ch <= '\u30FF' or '\u4E00' <= ch <= '\u9FFF' for ch in text)

def extract_all_strings(file_path_and_flag):
    file_path, japanese_only = file_path_and_flag
    results = []
    try:
        filesize = os.path.getsize(file_path)
        with open(file_path, "rb") as f:
            data = bytearray()
            with tqdm(total=filesize, desc=f"[{current_process().name}] {os.path.basename(file_path)}", unit="B", unit_scale=True, position=0, leave=False) as pbar:
                while chunk := f.read(8192):
                    data.extend(chunk)
                    pbar.update(len(chunk))

        for m in re.finditer(rb"[ -~]{%d,}" % MIN_LENGTH, data):
            try:
                s = m.group(0).decode('utf-8')
                offset = f"0x{m.start():X}"
                results.append((s, offset, 'ascii/utf8'))
            except:
                continue

        try:
            decoded_sjis = data.decode('shift_jis', errors='ignore')
            encoded_sjis = decoded_sjis.encode('shift_jis', errors='ignore')
            for m in re.finditer(rb"[^\x00-\x1F\x7F]{%d,}" % MIN_LENGTH, encoded_sjis):
                try:
                    s = m.group(0).decode('shift_jis')
                    idx = data.find(m.group(0))
                    if idx != -1:
                        offset = f"0x{idx:X}"
                        results.append((s, offset, 'shift_jis'))
                except:
                    continue
        except:
            pass

        for encoding in ['euc_jp', 'iso2022_jp']:
            try:
                decoded = data.decode(encoding, errors='ignore')
                encoded = decoded.encode(encoding, errors='ignore')
                for m in re.finditer(rb"[^\x00-\x1F\x7F]{%d,}" % MIN_LENGTH, encoded):
                    try:
                        s = m.group(0).decode(encoding)
                        idx = data.find(m.group(0))
                        if idx != -1:
                            offset = f"0x{idx:X}"
                            results.append((s, offset, encoding))
                    except:
                        continue
            except:
                continue

        results.extend(decode_utf16_strings(data))

        if japanese_only:
            results = [(s, o, enc) for s, o, enc in results if contains_japanese(s)]

    except Exception as e:
        print(f"[!] Ошибка при обработке {file_path}: {e}")
    return (file_path, results)

def save_to_csv(strings, out_path):
    with open(out_path, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Строка", "Оффсет", "Кодировка"])
        for line, offset, encoding in strings:
            writer.writerow([line, offset, encoding])

def save_duplicates(duplicates):
    os.makedirs(LOG_SUBDIR, exist_ok=True)
    with open(DUPLICATES_FILE, "w", newline='', encoding="utf-8") as dupfile:
        writer = csv.writer(dupfile)
        writer.writerow(["Строка", "Файлы"])
        for string, files in duplicates.items():
            if len(files) > 1:
                writer.writerow([string, "; ".join(sorted(files))])

def monitor_usage(stop_event, disk_path):
    old_disk = psutil.disk_io_counters()
    try:
        while not stop_event.is_set():
            cpu = psutil.cpu_percent(interval=1)
            new_disk = psutil.disk_io_counters()
            read_bytes = new_disk.read_bytes - old_disk.read_bytes
            write_bytes = new_disk.write_bytes - old_disk.write_bytes
            print(f"[CPU] {cpu:.1f}%  [Disk Read] {read_bytes / 1024:.1f} KB/s  [Write] {write_bytes / 1024:.1f} KB/s")
            old_disk = new_disk
    except KeyboardInterrupt:
        return

def main():
    parser = argparse.ArgumentParser(description="Извлечение строк из бинарников")
    parser.add_argument("--nogui", action="store_true", help="Без GUI")
    parser.add_argument("--file", type=str, help="Извлечь из одного файла")
    parser.add_argument("--path", type=str, help="Папка с файлами")
    parser.add_argument("--output", type=str, help="Куда сохранять")
    parser.add_argument("--japanese-only", action="store_true", help="Только японские строки")
    args = parser.parse_args()

    if args.nogui:
        if args.file and args.output:
            unpack_single_file(args.file, args.japanese_only, args.output)
        elif args.path and args.output:
            run_extraction(args.path, args.japanese_only, args.output)
        else:
            print("❗ Укажите --file и --output ИЛИ --path и --output")
    elif GUI_AVAILABLE:
        launch_gui()
    else:
        print("❌ GUI недоступен. Используйте --nogui")

def run_extraction(folder_path, japanese_only, out_dir):
    global OUTPUT_DIR, LOG_SUBDIR, LOG_FILE, DUPLICATES_FILE, SKIPPED_FILE
    OUTPUT_DIR = out_dir
    LOG_SUBDIR = os.path.join(OUTPUT_DIR, "logs")
    LOG_FILE = os.path.join(LOG_SUBDIR, "extract_log.csv")
    DUPLICATES_FILE = os.path.join(LOG_SUBDIR, "duplicate_strings.csv")
    SKIPPED_FILE = os.path.join(LOG_SUBDIR, "skipped_files.txt")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(LOG_SUBDIR, exist_ok=True)

    interrupted = False
    stop_event = Event()

    def handle_interrupt(signum, frame):
        nonlocal interrupted
        interrupted = True
        stop_event.set()
        print("\n🚫 Прерывание пользователем. Завершаем...")

    signal.signal(signal.SIGINT, handle_interrupt)
    signal.signal(signal.SIGTERM, handle_interrupt)

    all_files = []
    seen_hashes = set()
    log_entries = {}
    string_occurrences = defaultdict(set)
    skipped = []

    for root, _, files in os.walk(folder_path):
        for file in sorted(files):
            if file in SKIP_FILES or file.endswith(".py") or OUTPUT_DIR in root:
                continue
            full_path = os.path.join(root, file)
            fhash = file_hash(full_path)
            if fhash in seen_hashes:
                continue
            seen_hashes.add(fhash)
            all_files.append(full_path)

    monitor = Process(target=monitor_usage, args=(stop_event, folder_path), daemon=True)
    monitor.start()

    try:
        with Pool(cpu_count()) as pool:
            for file_path, strings in tqdm(pool.imap_unordered(extract_all_strings, [(f, japanese_only) for f in all_files]), total=len(all_files), desc="Извлечение строк"):
                if not strings:
                    skipped.append(file_path)
                    continue
                base = os.path.splitext(os.path.basename(file_path))[0]
                ext = os.path.splitext(file_path)[1].lstrip('.').lower()
                out_filename = f"{base}__{ext}.csv"
                out_path = os.path.join(out_dir, out_filename)
                save_to_csv(strings, out_path)
                log_entries[file_path] = (out_filename, len(strings))
                for line, _, _ in strings:
                    string_occurrences[line].add(file_path)
    finally:
        stop_event.set()
        monitor.terminate()
        monitor.join()

    with open(LOG_FILE, "w", newline='', encoding="utf-8") as logfile:
        writer = csv.writer(logfile)
        writer.writerow(["Исходный файл", "CSV файл", "Количество строк"])
        for path, (csv_name, count) in log_entries.items():
            writer.writerow([path, csv_name, count])

    save_duplicates(string_occurrences)

    if skipped:
        with open(SKIPPED_FILE, "w", encoding="utf-8") as f:
            for s in skipped:
                f.write(s + "\n")
        print(f"\n📄 Пропущено {len(skipped)} файлов без строк. Список: {SKIPPED_FILE}")
        for s in skipped:
            print(f"  - {s}")

    print(f"\n✅ Готово. Лог: {LOG_FILE}, Повторы: {DUPLICATES_FILE}")

def launch_gui():
    root = tk.Tk()
    root.title("Извлечение строк")

    tk.Label(root, text="Выберите режим:").pack(pady=5)
    var_japanese_only = tk.BooleanVar()
    tk.Checkbutton(root, text="Только японские строки", variable=var_japanese_only).pack()

    def extract_from_dir():
        folder = filedialog.askdirectory()
        if not folder:
            return
        out_dir = filedialog.askdirectory(title="Куда сохранить результат")
        if not out_dir:
            return
        run_extraction(folder, var_japanese_only.get(), out_dir)

    def extract_from_file():
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
        out_dir = filedialog.askdirectory(title="Куда сохранить результат")
        if not out_dir:
            return
        unpack_single_file(file_path, var_japanese_only.get(), out_dir)

    tk.Button(root, text="Извлечь из папки", command=extract_from_dir).pack(pady=5)
    tk.Button(root, text="Извлечь из одного файла", command=extract_from_file).pack(pady=5)
    root.mainloop()

def unpack_single_file(file_path, japanese_only, out_dir):
    try:
        filesize = os.path.getsize(file_path)
        results = []
        with open(file_path, "rb") as f:
            data = bytearray()
            with tqdm(total=filesize, desc=f"Чтение {os.path.basename(file_path)}", unit="B", unit_scale=True) as pbar:
                while chunk := f.read(8192):
                    data.extend(chunk)
                    pbar.update(len(chunk))

        with tqdm(total=3, desc="Извлечение строк", unit="этап") as stagebar:
            for m in re.finditer(rb"[ -~]{%d,}" % MIN_LENGTH, data):
                try:
                    s = m.group(0).decode('utf-8')
                    offset = f"0x{m.start():X}"
                    results.append((s, offset, 'ascii/utf8'))
                except:
                    continue
            stagebar.update(1)

            try:
                decoded_sjis = data.decode('shift_jis', errors='ignore')
                encoded_sjis = decoded_sjis.encode('shift_jis', errors='ignore')
                for m in re.finditer(rb"[^\x00-\x1F\x7F]{%d,}" % MIN_LENGTH, encoded_sjis):
                    try:
                        s = m.group(0).decode('shift_jis')
                        idx = data.find(m.group(0))
                        if idx != -1:
                            offset = f"0x{idx:X}"
                            results.append((s, offset, 'shift_jis'))
                    except:
                        continue
            except:
                pass
            stagebar.update(1)

            results.extend(decode_utf16_strings(data))
            stagebar.update(1)

        if japanese_only:
            results = [(s, o, enc) for s, o, enc in results if contains_japanese(s)]

        if results:
            base = os.path.splitext(os.path.basename(file_path))[0]
            ext = os.path.splitext(file_path)[1].lstrip('.').lower()
            out_filename = f"{base}__{ext}.csv"
            out_path = os.path.join(out_dir, out_filename)
            save_to_csv(results, out_path)
            print(f"✅ Сохранено: {out_path}")
        else:
            print("⚠ В файле не найдено строк.")

    except Exception as e:
        print(f"❌ Ошибка при распаковке: {e}")

if __name__ == "__main__":
    main()
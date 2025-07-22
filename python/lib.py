def hex2str(input_num, output):
    tmp = f"{input_num:08X}"
    for i in range(8):
        output[2*i] = ord(tmp[i])

def extract_offset_blocklen(file_path):
    """Извлекает OFFSET и BLOCK_LEN из бинарного файла"""
    with open(file_path, 'rb') as f:
        # Читаем весь файл
        data = f.read()
        
        # Получаем OFFSET (4 байта с позиции 8)
        offset = int.from_bytes(data[8:12], byteorder='little')
        
        # Вычисляем BLOCK_LEN
        block_len = len(data) - offset
        
        return offset, block_len

# if __name__ == "__main__":
#     offset, block_len = extract_offset_blocklen("work/initDB.dat")
#     print(f"OFFSET: 0x{offset:08X}")
#     print(f"BLOCK_LEN: 0x{block_len:08X}")
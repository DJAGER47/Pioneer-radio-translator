import struct
import argparse
import json
from lib import hex2str, extract_offset_blocklen


def parse_dat_file(input_path, output_path):
    OFFSET , BLOCK_LEN = extract_offset_blocklen(input_path)
    print(f"OFFSET: 0x{OFFSET:08X}")
    print(f"BLOCK_LEN: 0x{BLOCK_LEN:08X}")
    
    strings = []
    with open(input_path, 'rb') as fin:
        
        fin.seek(OFFSET)
        data = fin.read(BLOCK_LEN)
        
        index = 0
        str_buf = bytearray(2048)
        tmp_str = bytearray(16)
        
        for i in range(0, len(data), 2):
            p = data[i:i+2]
            
            #  string start
            if p == b'\xFF\xFF':
                index = 0
                continue

            #  string end
            if p == b'\x00\x00':
                if index > 0:
                    # Skip image links
                    if (index > 8 and 
                        str_buf[index-8] == 0x2E and  # .
                        ((str_buf[index-6] == 0x67 and str_buf[index-4] == 0x69 and str_buf[index-2] == 0x66) or  # gif
                         (str_buf[index-6] == 0x62 and str_buf[index-4] == 0x6D and str_buf[index-2] == 0x70) or  # bmp
                         (str_buf[index-6] == 0x70 and str_buf[index-4] == 0x6E and str_buf[index-2] == 0x67) or  # png
                         (str_buf[index-6] == 0x6A and str_buf[index-4] == 0x70 and str_buf[index-2] == 0x67))):  # jpg
                        index = 0
                        continue
                    
                    # Skip special patterns
                    if (index > 8 and 
                        ((str_buf[0] == 0x53 and str_buf[2] == 0x54 and str_buf[4] == 0x52 and str_buf[6] == 0x5F) or  # STR_
                         (str_buf[0] == 0x4D and str_buf[2] == 0x53 and str_buf[4] == 0x47 and str_buf[6] == 0x5F) or  # MSG_
                         (str_buf[0] == 0x4D and str_buf[2] == 0x4D and str_buf[4] == 0x5F))):  # MM_
                        index = 0
                        continue
                        
                    # Skip ESC sequences and #
                    if index > 2 and (str_buf[0] == 0x1B or str_buf[0] == 0x23) and str_buf[1] == 0x00:
                        index = 0
                        continue

                    hex2str(OFFSET + i - index, tmp_str)
                    address = tmp_str.decode('utf-16le').strip('\x00')

                    hex2str(index, tmp_str)
                    size = tmp_str.decode('utf-16le').strip('\x00')

                    original = str_buf[:index].decode('utf-16le')

                    expected_len = len(original) * 2  # UTF-16 uses 2 bytes per character
                    if int(size, 16) != expected_len:
                        print(f"Warning: size {size} (hex) != expected length {expected_len} (strlen {len(original)} * 2)")
                    
                    strings.append({
                        "address": address,
                        "size": size,
                        "original": original,
                        "translation": ""
                    })
                    
                index = 0
                continue
                
            if index < len(str_buf) - 1:
                str_buf[index] = p[0]
                str_buf[index+1] = p[1]
                index += 2

    # Сортируем строки по полю original
    strings_sorted = sorted(strings, key=lambda x: int(x['size'], 16), reverse=True)
    
    print(f"Найдено строк: {len(strings_sorted)}")
    
    with open(output_path, 'w', encoding='utf-16-le') as fout:
        json.dump(strings_sorted, fout, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parse translation file from UTF-16 LE format')
    parser.add_argument('-i', '--input', default='translation.txt',
                       help='Input file name (default: translation.txt)')
    parser.add_argument('-o', '--output', default='translation.json',
                       help='Output file name (default: translation.json)')
    
    args = parser.parse_args()
    parse_dat_file(args.input, args.output)
import struct

def hex2str(input_num, output):
    """Аналог функции hex2str из C-кода"""
    tmp = f"{input_num:08X}"
    for i in range(8):
        output[2*i] = ord(tmp[i])

def parse_dat_file(input_path, output_path):
    OFFSET = 0x2671F4
    BLOCK_LEN = 0x3234D7 - OFFSET + 1
    
    with open(input_path, 'rb') as fin, open(output_path, 'wb') as fout:
        # Write BOM
        fout.write(b'\xFF\xFE')
        
        fin.seek(OFFSET)
        data = fin.read(BLOCK_LEN)
        
        index = 0
        str_buf = bytearray(1024)
        tmp_str = bytearray(16)
        
        for i in range(0, len(data), 2):
            p = data[i:i+2]
            
            if p == b'\xFF\xFF':
                index = 0
                continue
                
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
                    
                    # Write address
                    hex2str(OFFSET + i - index, tmp_str)
                    fout.write(tmp_str)
                    fout.write(b'\x09\x00')
                    
                    # Write length (in bytes)
                    hex2str(index, tmp_str)
                    fout.write(tmp_str)
                    fout.write(b'\x09\x00')
                    
                    # Write string content
                    fout.write(str_buf[:index])
                    fout.write(b'\x09\x00\x0D\x00\x0A\x00')
                    
                index = 0
                continue
                
            if index < len(str_buf) - 1:
                str_buf[index] = p[0]
                str_buf[index+1] = p[1]
                index += 2

if __name__ == "__main__":
    parse_dat_file("work/initDB.dat", "parsed1.txt")
import struct
import os

crc32_table = [
    0x00000000, 0x77073096, 0xEE0E612C, 0x990951BA, 0x076DC419, 0x706AF48F, 0xE963A535, 0x9E6495A3, 0x0EDB8832, 0x79DCB8A4, 0xE0D5E91E, 0x97D2D988,
    0x09B64C2B, 0x7EB17CBD, 0xE7B82D07, 0x90BF1D91, 0x1DB71064, 0x6AB020F2, 0xF3B97148, 0x84BE41DE, 0x1ADAD47D, 0x6DDDE4EB, 0xF4D4B551, 0x83D385C7,
    0x136C9856, 0x646BA8C0, 0xFD62F97A, 0x8A65C9EC, 0x14015C4F, 0x63066CD9, 0xFA0F3D63, 0x8D080DF5, 0x3B6E20C8, 0x4C69105E, 0xD56041E4, 0xA2677172,
    0x3C03E4D1, 0x4B04D447, 0xD20D85FD, 0xA50AB56B, 0x35B5A8FA, 0x42B2986C, 0xDBBBC9D6, 0xACBCF940, 0x32D86CE3, 0x45DF5C75, 0xDCD60DCF, 0xABD13D59,
    0x26D930AC, 0x51DE003A, 0xC8D75180, 0xBFD06116, 0x21B4F4B5, 0x56B3C423, 0xCFBA9599, 0xB8BDA50F, 0x2802B89E, 0x5F058808, 0xC60CD9B2, 0xB10BE924,
    0x2F6F7C87, 0x58684C11, 0xC1611DAB, 0xB6662D3D, 0x76DC4190, 0x01DB7106, 0x98D220BC, 0xEFD5102A, 0x71B18589, 0x06B6B51F, 0x9FBFE4A5, 0xE8B8D433,
    0x7807C9A2, 0x0F00F934, 0x9609A88E, 0xE10E9818, 0x7F6A0DBB, 0x086D3D2D, 0x91646C97, 0xE6635C01, 0x6B6B51F4, 0x1C6C6162, 0x856530D8, 0xF262004E,
    0x6C0695ED, 0x1B01A57B, 0x8208F4C1, 0xF50FC457, 0x65B0D9C6, 0x12B7E950, 0x8BBEB8EA, 0xFCB9887C, 0x62DD1DDF, 0x15DA2D49, 0x8CD37CF3, 0xFBD44C65,
    0x4DB26158, 0x3AB551CE, 0xA3BC0074, 0xD4BB30E2, 0x4ADFA541, 0x3DD895D7, 0xA4D1C46D, 0xD3D6F4FB, 0x4369E96A, 0x346ED9FC, 0xAD678846, 0xDA60B8D0,
    0x44042D73, 0x33031DE5, 0xAA0A4C5F, 0xDD0D7CC9, 0x5005713C, 0x270241AA, 0xBE0B1010, 0xC90C2086, 0x5768B525, 0x206F85B3, 0xB966D409, 0xCE61E49F,
    0x5EDEF90E, 0x29D9C998, 0xB0D09822, 0xC7D7A8B4, 0x59B33D17, 0x2EB40D81, 0xB7BD5C3B, 0xC0BA6CAD, 0xEDB88320, 0x9ABFB3B6, 0x03B6E20C, 0x74B1D29A,
    0xEAD54739, 0x9DD277AF, 0x04DB2615, 0x73DC1683, 0xE3630B12, 0x94643B84, 0x0D6D6A3E, 0x7A6A5AA8, 0xE40ECF0B, 0x9309FF9D, 0x0A00AE27, 0x7D079EB1,
    0xF00F9344, 0x8708A3D2, 0x1E01F268, 0x6906C2FE, 0xF762575D, 0x806567CB, 0x196C3671, 0x6E6B06E7, 0xFED41B76, 0x89D32BE0, 0x10DA7A5A, 0x67DD4ACC,
    0xF9B9DF6F, 0x8EBEEFF9, 0x17B7BE43, 0x60B08ED5, 0xD6D6A3E8, 0xA1D1937E, 0x38D8C2C4, 0x4FDFF252, 0xD1BB67F1, 0xA6BC5767, 0x3FB506DD, 0x48B2364B,
    0xD80D2BDA, 0xAF0A1B4C, 0x36034AF6, 0x41047A60, 0xDF60EFC3, 0xA867DF55, 0x316E8EEF, 0x4669BE79, 0xCB61B38C, 0xBC66831A, 0x256FD2A0, 0x5268E236,
    0xCC0C7795, 0xBB0B4703, 0x220216B9, 0x5505262F, 0xC5BA3BBE, 0xB2BD0B28, 0x2BB45A92, 0x5CB36A04, 0xC2D7FFA7, 0xB5D0CF31, 0x2CD99E8B, 0x5BDEAE1D,
    0x9B64C2B0, 0xEC63F226, 0x756AA39C, 0x026D930A, 0x9C0906A9, 0xEB0E363F, 0x72076785, 0x05005713, 0x95BF4A82, 0xE2B87A14, 0x7BB12BAE, 0x0CB61B38,
    0x92D28E9B, 0xE5D5BE0D, 0x7CDCEFB7, 0x0BDBDF21, 0x86D3D2D4, 0xF1D4E242, 0x68DDB3F8, 0x1FDA836E, 0x81BE16CD, 0xF6B9265B, 0x6FB077E1, 0x18B74777,
    0x88085AE6, 0xFF0F6A70, 0x66063BCA, 0x11010B5C, 0x8F659EFF, 0xF862AE69, 0x616BFFD3, 0x166CCF45, 0xA00AE278, 0xD70DD2EE, 0x4E048354, 0x3903B3C2,
    0xA7672661, 0xD06016F7, 0x4969474D, 0x3E6E77DB, 0xAED16A4A, 0xD9D65ADC, 0x40DF0B66, 0x37D83BF0, 0xA9BCAE53, 0xDEBB9EC5, 0x47B2CF7F, 0x30B5FFE9,
    0xBDBDF21C, 0xCABAC28A, 0x53B39330, 0x24B4A3A6, 0xBAD03605, 0xCDD70693, 0x54DE5729, 0x23D967BF, 0xB3667A2E, 0xC4614AB8, 0x5D681B02, 0x2A6F2B94,
    0xB40BBE37, 0xC30C8EA1, 0x5A05DF1B, 0x2D02EF8D
]

class HeaderType:
    def __init__(self):
        self.magic = 0xa55a5aa5       # 4 bytes
        self.len = 192                # 4 bytes (размер структуры)
        self.version = 0x07010000     # 4 bytes
        self.volume = 2               # 4 bytes
        self.zero1 = 0                # 4 bytes
        self.a2c = 0x2c               # 4 bytes
        self.nb0_length = 0           # 4 bytes (длина payload файла)
        self.nb0_crc = 0              # 4 bytes (CRC32 payload файла)
        self.version1 = 0x07010000    # 4 bytes
        self.volume1 = 2              # 4 bytes
        self.zero2 = 0                # 4 bytes
        self.nfiles = 1               # 4 bytes
        self.dirdepth = 1             # 4 bytes
        self.dirname = bytearray(64)  # 64 bytes
        self.filestoprocess = 1       # 4 bytes
        self.filename = bytearray(56) # 56 bytes
        self.file_length = 0          # 4 bytes
        self.file_crc = 0             # 4 bytes
        self.magic1 = 0xa55a5aa5      # 4 bytes
        self.ver_crc = 0              # 4 bytes (CRC до magic1 включительно)
        # Общий размер структуры: 192 байт

    def __bytes__(self):
        import struct
        # Упаковываем все поля структуры в правильном порядке
        data = struct.pack('<IIIIIIIIIIIII',
            self.magic,
            self.len,
            self.version,
            self.volume,
            self.zero1,
            self.a2c,
            self.nb0_length,
            self.nb0_crc,
            self.version1,
            self.volume1,
            self.zero2,
            self.nfiles,
            self.dirdepth)
        
        # Добавляем строковые поля и следующие за ними поля
        data += bytes(self.dirname)
        data += struct.pack('<I', self.filestoprocess)
        data += bytes(self.filename)
        data += struct.pack('<III',
            self.file_length,
            self.file_crc,
            self.magic1)
        
        # Завершаем упаковку последнего поля
        data += struct.pack('<I', self.ver_crc)
        
        # Проверяем размер (должен быть 192 байт)
        if len(data) != 192:
            print(f"[ERROR] Invalid header size: {len(data)} bytes (expected 192)")
            
        return data

class HeaderTypePrg:
    def __init__(self):
        # Полная копия структуры из C версии
        self.magic = 0xa55a5aa5          # 4 bytes
        self.file_length = 0             # 4 bytes
        self.file_crc = 0                # 4 bytes
        self.version = 0x07010000        # 4 bytes (фиксированное значение)
        self.volume = 2                  # 4 bytes (фиксированное значение)
        self.zero1 = 0                   # 4 bytes
        self.filename = bytearray(16)    # 16 bytes
        self.filedate = bytearray(24)    # 24 bytes
        self.zeros1 = [0, 0]             # 8 bytes
        self.ffs0 = [0xFFFFFFFF] * 14    # 56 bytes
        self.magic1 = 0xa55a5aa5         # 4 bytes
        self.zero2 = 0                   # 4 bytes
        self.file_length_prg = 0         # 4 bytes
        self.file_crc1 = 0               # 4 bytes
        self.magic2 = [0x88471000, 0x88471004, 0x10000006] # 12 bytes (фиксированные значения)
        self.ffs1 = [0xFFFFFFFF] * 16    # 64 bytes
        self.ffs2 = [0xFFFFFFFF] * 16    # 64 bytes
        self.ffs3 = [0xFFFFFFFF] * 16    # 64 bytes
        self.ffs4 = [0xFFFFFFFF] * 16    # 64 bytes
        self.ffs5 = [0xFFFFFFFF] * 16    # 64 bytes
        self.ffs6 = [0xFFFFFFFF] * 8     # 32 bytes
        self.ver_crc = 0                 # 4 bytes
        # Общий размер структуры: 512 байт

def wscpy(dest, src):
    i = 0
    for c in src:
        dest[i] = ord(c)
        i += 2

def crc32b(data, length):
    crc = 0xFFFFFFFF
    if isinstance(data, bytearray):
        data = bytes(data)
    for i in range(length):
        crc = (crc >> 8) ^ crc32_table[(crc ^ data[i]) & 0xFF]
    return (~crc) & 0xFFFFFFFF  # Изменено для точного соответствия C версии

def checksum32(data, length):
    print(f"[DEBUG] checksum32 input: len={length}, data={data[:16]}...")  # Логируем входные данные
    crc = 0
    tmp = 0
    length = length // 4
    
    if length > 0:
        for i in range(length):
            tmp = 0
            for j in range(4):
                tmp |= (data[i*4 + j] << (8 * j))
            crc += tmp
            if i == length-1:  # Логируем последнюю итерацию
                print(f"[DEBUG] Last block: i={i}, tmp={hex(tmp)}, crc={hex(crc)}")
    
    result = crc & 0xFFFFFFFF
    print(f"[DEBUG] checksum32 result: {hex(result)}")
    return result

def main():
    # Проверка размера структуры
    h = HeaderType()
    struct_size = len(bytes(h))
    print(f"[DEBUG] HeaderType size: {struct_size} bytes")
    if struct_size != 192:
        print("[WARNING] Header size mismatch! Expected 192 bytes")

    h_prg = HeaderTypePrg()
    h = HeaderType()
    
    dir = "PLATFORM"
    datfile = "PS140PLT.PRG"
    nb0file = "output.nb0"
    pltname = "PS140PLT.PRG"
    pltdate = "2021/04/06_10:04:53+540"
    
    # PRG header creation
    with open(nb0file, 'rb') as fin1:
        fin1.seek(0, 2)
        h_prg.file_length = fin1.tell()
        fin1.seek(0)
        p1 = fin1.read(h_prg.file_length)
        
    # Initialize all fields explicitly to match C version
    h_prg.file_crc = checksum32(p1, h_prg.file_length)
    h_prg.version = 0x07010000
    h_prg.volume = 2
    h_prg.zero1 = 0
    h_prg.filename = bytearray(16)  # Fixed size as in C version
    h_prg.filename[:len(pltname)] = pltname.encode('ascii')
    h_prg.filedate = bytearray(24)  # Fixed size as in C version
    h_prg.filedate[:len(pltdate)] = pltdate.encode('ascii')
    h_prg.zeros1 = [0, 0]
    h_prg.ffs0 = [0xFFFFFFFF] * 14
    h_prg.magic1 = 0xa55a5aa5
    h_prg.zero2 = 0
    h_prg.file_length_prg = h_prg.file_length
    h_prg.file_crc1 = h_prg.file_crc
    h_prg.magic2 = [0x88471000, 0x88471004, 0x10000006]
    h_prg.ffs1 = [0xFFFFFFFF] * 16
    h_prg.ffs2 = [0xFFFFFFFF] * 16
    h_prg.ffs3 = [0xFFFFFFFF] * 16
    h_prg.ffs4 = [0xFFFFFFFF] * 16
    h_prg.ffs5 = [0xFFFFFFFF] * 16
    h_prg.ffs6 = [0xFFFFFFFF] * 8
    
    # Calculate PRG header CRC
    h_prg_bytes = bytearray()
    for field in [h_prg.magic, h_prg.file_length, h_prg.file_crc, h_prg.version, h_prg.volume, h_prg.zero1]:
        h_prg_bytes.extend(struct.pack('<I', field))
    h_prg_bytes.extend(h_prg.filename)
    h_prg_bytes.extend(h_prg.filedate)
    for zero in h_prg.zeros1:
        h_prg_bytes.extend(struct.pack('<I', zero))
    for ffs in h_prg.ffs0:
        h_prg_bytes.extend(struct.pack('<I', ffs))
    h_prg_bytes.extend(struct.pack('<I', h_prg.magic1))
    h_prg_bytes.extend(struct.pack('<I', h_prg.zero2))
    h_prg_bytes.extend(struct.pack('<I', h_prg.file_length_prg))
    h_prg_bytes.extend(struct.pack('<I', h_prg.file_crc1))
    for magic in h_prg.magic2:
        h_prg_bytes.extend(struct.pack('<I', magic))
    for ffs in h_prg.ffs1:
        h_prg_bytes.extend(struct.pack('<I', ffs))
    for ffs in h_prg.ffs2:
        h_prg_bytes.extend(struct.pack('<I', ffs))
    for ffs in h_prg.ffs3:
        h_prg_bytes.extend(struct.pack('<I', ffs))
    for ffs in h_prg.ffs4:
        h_prg_bytes.extend(struct.pack('<I', ffs))
    for ffs in h_prg.ffs5:
        h_prg_bytes.extend(struct.pack('<I', ffs))
    for ffs in h_prg.ffs6:
        h_prg_bytes.extend(struct.pack('<I', ffs))
    
    h_prg.ver_crc = checksum32(h_prg_bytes, len(h_prg_bytes))
    
    # Добавляем поле ver_crc в байтовое представление структуры
    h_prg_bytes.extend(struct.pack('<I', h_prg.ver_crc))
    
    # Write PRG file
    with open(datfile, 'wb') as fout1:
        fout1.write(h_prg_bytes)
        fout1.write(p1)
    
    # VER file creation
    h.magic = 0xa55a5aa5
    h.len = 192  # sizeof(h)
    h.version = 0x07010000
    h.volume = 2
    h.zero1 = 0
    h.a2c = 0x2c
    h.nb0_length = h_prg.file_length
    h.nb0_crc = h_prg.file_crc
    h.version1 = 0x07010000
    h.volume1 = 2
    h.zero2 = 0
    h.nfiles = 1
    h.dirdepth = 1
    wscpy(h.dirname, dir)
    h.filestoprocess = 1
    wscpy(h.filename, datfile)
    
    with open(datfile, 'rb') as fin:
        fin.seek(0, 2)
        h.file_length = fin.tell()
        fin.seek(0)
        p = fin.read(h.file_length)
    
    h.file_crc = crc32b(p, h.file_length)
    h.magic1 = 0xa55a5aa5
    
    # Calculate VER header CRC using our __bytes__ method
    h_bytes = bytearray(bytes(h))
    
    # Логирование дампа структуры перед расчетом CRC
    print("Python VER structure dump:")
    for i in range(0, len(h_bytes), 16):
        chunk = h_bytes[i:i+16]
        print(f"{i:04x}: {' '.join(f'{b:02x}' for b in chunk)}")
    
    # Вычисляем CRC для всей структуры, кроме последних 4 байтов (поля ver_crc)
    h.ver_crc = crc32b(h_bytes[:-4], len(h_bytes) - 4)
    print(f"Python VER header CRC: {hex(h.ver_crc)}")
    print(f"Python VER data CRC: {hex(h.file_crc)}")
    print(f"Python VER header size: {len(h_bytes)}")
    
    # Обновляем поле ver_crc в байтовом представлении структуры
    h_bytes[-4:] = struct.pack('<I', h.ver_crc)
    
    # Write VER file
    with open("PS140PLT.VER", 'wb') as fout:
        fout.write(h_bytes)

if __name__ == "__main__":
    main()
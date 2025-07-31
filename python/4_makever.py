import struct
import os
from lib import checksum32, crc32b


class HeaderType:
    def __init__(self):
        self.magic = 0xa55a5aa5       # 4 bytes
        self.len = 192                # 4 bytes (размер структуры)
        self.version = 0              # 4 bytes
        self.volume = 0               # 4 bytes
        self.zero1 = 0                # 4 bytes
        self.a2c = 0x2c               # 4 bytes
        self.nb0_length = 0           # 4 bytes (длина payload файла)
        self.nb0_crc = 0              # 4 bytes (CRC32 payload файла)
        self.version1 = 0             # 4 bytes
        self.volume1 = 0              # 4 bytes
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

    def set_version(self, version):
        self.version = version
        self.version1 = version

    def set_volume(self, volume):
        self.volume = volume
        self.volume1 = volume

    def __bytes__(self):
        import struct
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
        data += bytes(self.dirname)
        data += struct.pack('<I', self.filestoprocess)
        data += bytes(self.filename)
        data += struct.pack('<III',
            self.file_length,
            self.file_crc,
            self.magic1)
        data += struct.pack('<I', self.ver_crc) 
        return data

class HeaderTypePrg:
    def __init__(self):
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


def main():
    header = HeaderType()
    header_prg = HeaderTypePrg()
    
    dir = "PLATFORM"
    datfile = "PS140PLT.PRG"
    nb0file = "output.nb0"
    pltname = "PS140PLT.PRG"
    pltdate = "2021/04/06_10:04:53+540"
    
    # PRG header creation
    with open(nb0file, 'rb') as fin1:
        fin1.seek(0, 2)
        header_prg.file_length = fin1.tell()
        fin1.seek(0)
        p1 = fin1.read(header_prg.file_length)

    header_prg.file_crc = checksum32(p1, header_prg.file_length)
    header_prg.version = 0x07010000
    header_prg.volume = 2
    header_prg.zero1 = 0
    header_prg.filename = bytearray(16)
    header_prg.filename[:len(pltname)] = pltname.encode('ascii')
    header_prg.filedate = bytearray(24)
    header_prg.filedate[:len(pltdate)] = pltdate.encode('ascii')
    header_prg.zeros1 = [0, 0]
    header_prg.ffs0 = [0xFFFFFFFF] * 14
    header_prg.magic1 = 0xa55a5aa5
    header_prg.zero2 = 0
    header_prg.file_length_prg = header_prg.file_length
    header_prg.file_crc1 = header_prg.file_crc
    header_prg.magic2 = [0x88471000, 0x88471004, 0x10000006]
    header_prg.ffs1 = [0xFFFFFFFF] * 16
    header_prg.ffs2 = [0xFFFFFFFF] * 16
    header_prg.ffs3 = [0xFFFFFFFF] * 16
    header_prg.ffs4 = [0xFFFFFFFF] * 16
    header_prg.ffs5 = [0xFFFFFFFF] * 16
    header_prg.ffs6 = [0xFFFFFFFF] * 8
    
    # Calculate PRG header CRC
    h_prg_bytes = bytearray()
    for field in [header_prg.magic, header_prg.file_length, header_prg.file_crc, header_prg.version, header_prg.volume, header_prg.zero1]:
        h_prg_bytes.extend(struct.pack('<I', field))
    h_prg_bytes.extend(header_prg.filename)
    h_prg_bytes.extend(header_prg.filedate)
    for zero in header_prg.zeros1:
        h_prg_bytes.extend(struct.pack('<I', zero))
    for ffs in header_prg.ffs0:
        h_prg_bytes.extend(struct.pack('<I', ffs))
    h_prg_bytes.extend(struct.pack('<I', header_prg.magic1))
    h_prg_bytes.extend(struct.pack('<I', header_prg.zero2))
    h_prg_bytes.extend(struct.pack('<I', header_prg.file_length_prg))
    h_prg_bytes.extend(struct.pack('<I', header_prg.file_crc1))
    for magic in header_prg.magic2:
        h_prg_bytes.extend(struct.pack('<I', magic))
    for ffs in header_prg.ffs1:
        h_prg_bytes.extend(struct.pack('<I', ffs))
    for ffs in header_prg.ffs2:
        h_prg_bytes.extend(struct.pack('<I', ffs))
    for ffs in header_prg.ffs3:
        h_prg_bytes.extend(struct.pack('<I', ffs))
    for ffs in header_prg.ffs4:
        h_prg_bytes.extend(struct.pack('<I', ffs))
    for ffs in header_prg.ffs5:
        h_prg_bytes.extend(struct.pack('<I', ffs))
    for ffs in header_prg.ffs6:
        h_prg_bytes.extend(struct.pack('<I', ffs))
    
    header_prg.ver_crc = checksum32(h_prg_bytes, len(h_prg_bytes))
    
    # Добавляем поле ver_crc в байтовое представление структуры
    h_prg_bytes.extend(struct.pack('<I', header_prg.ver_crc))
    
    # Write PRG file
    with open(datfile, 'wb') as fout1:
        fout1.write(h_prg_bytes)
        fout1.write(p1)
    
    # VER file creation
    header.magic = 0xa55a5aa5
    header.len = 192  # sizeof(header)
    header.version = 0x07010000
    header.volume = 2
    header.zero1 = 0
    header.a2c = 0x2c
    header.nb0_length = header_prg.file_length
    header.nb0_crc = header_prg.file_crc
    header.version1 = 0x07010000
    header.volume1 = 2
    header.zero2 = 0
    header.nfiles = 1
    header.dirdepth = 1
    wscpy(header.dirname, dir)
    header.filestoprocess = 1
    wscpy(header.filename, datfile)
    
    with open(datfile, 'rb') as fin:
        fin.seek(0, 2)
        header.file_length = fin.tell()
        fin.seek(0)
        p = fin.read(header.file_length)
    
    header.file_crc = crc32b(p, header.file_length)
    header.magic1 = 0xa55a5aa5
    
    # Calculate VER header CRC using our __bytes__ method
    h_bytes = bytearray(bytes(header))
    
    # Вычисляем CRC для всей структуры, кроме последних 4 байтов (поля ver_crc)
    header.ver_crc = crc32b(h_bytes[:-4], len(h_bytes) - 4)
    
    # Обновляем поле ver_crc в байтовом представлении структуры
    h_bytes[-4:] = struct.pack('<I', header.ver_crc)
    
    # Write VER file
    with open("PS140PLT.VER", 'wb') as fout:
        fout.write(h_bytes)

if __name__ == "__main__":
    main()
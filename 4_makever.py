import struct
import os
from lib import checksum32, crc32b, extract_file_metadata


class HeaderTypeVer:
    def __init__(self):
        self.magic = 0xA55A5AA5
        self.len = 192  # размер структуры
        self.version = 0
        self.volume = 0
        self.zero1 = 0
        self.a2c = 0x2C
        self.nb0_length = 0  # длина payload файла
        self.nb0_crc = 0  # CRC32 payload файла
        self.version1 = 0
        self.volume1 = 0
        self.zero2 = 0
        self.nfiles = 1
        self.dirdepth = 1
        self.dirname = bytearray(64)
        self.filestoprocess = 1
        self.filename = bytearray(56)
        self.file_length = 0
        self.file_crc = 0
        self.magic1 = 0xA55A5AA5
        self.ver_crc = 0  # CRC до magic1 включительно
        # Общий размер структуры: 192 байт

    def set_version(self, version):
        self.version = version
        self.version1 = version

    def set_volume(self, volume):
        self.volume = volume
        self.volume1 = volume

    def __bytes__(self):
        data = struct.pack(
            "<IIIIIIIIIIIII",
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
            self.dirdepth,
        )
        data += bytes(self.dirname)
        data += struct.pack("<I", self.filestoprocess)
        data += bytes(self.filename)
        data += struct.pack("<III", self.file_length, self.file_crc, self.magic1)
        self.ver_crc = crc32b(data, len(data))
        data += struct.pack("<I", self.ver_crc)
        return data


class HeaderTypePrg:
    def __init__(self):
        self.magic = 0xA55A5AA5
        self.file_length = 0
        self.file_crc = 0
        self.version = 0
        self.volume = 0
        self.zero1 = 0
        self.filename = bytearray(16)
        self.filedate = bytearray(24)
        self.zeros1 = [0, 0]
        self.ffs0 = [0xFFFFFFFF] * 14  # 56 bytes
        self.magic1 = 0xA55A5AA5
        self.zero2 = 0
        self.file_length_prg = 0
        self.file_crc1 = 0  #
        self.magic2 = [
            0x88471000,
            0x88471004,
            0x10000006,
        ]  # 12 bytes (фиксированные значения)
        self.ffs1 = [0xFFFFFFFF] * 16  # 64 bytes
        self.ffs2 = [0xFFFFFFFF] * 16  # 64 bytes
        self.ffs3 = [0xFFFFFFFF] * 16  # 64 bytes
        self.ffs4 = [0xFFFFFFFF] * 16  # 64 bytes
        self.ffs5 = [0xFFFFFFFF] * 16  # 64 bytes
        self.ffs6 = [0xFFFFFFFF] * 8  # 32 bytes
        self.ver_crc = 0
        # Общий размер структуры: 512 байт

    def __bytes__(self):
        import struct

        data = struct.pack(
            "<IIIIII",
            self.magic,
            self.file_length,
            self.file_crc,
            self.version,
            self.volume,
            self.zero1,
        )
        data += bytes(self.filename)
        data += bytes(self.filedate)
        data += struct.pack("<II", *self.zeros1)
        data += struct.pack("<IIIIIIIIIIIIII", *self.ffs0)
        data += struct.pack(
            "<IIII",
            self.magic1,
            self.zero2,
            self.file_length_prg,
            self.file_crc1,
        )
        data += struct.pack("<III", *self.magic2)
        data += struct.pack("<IIIIIIIIIIIIIIII", *self.ffs1)
        data += struct.pack("<IIIIIIIIIIIIIIII", *self.ffs2)
        data += struct.pack("<IIIIIIIIIIIIIIII", *self.ffs3)
        data += struct.pack("<IIIIIIIIIIIIIIII", *self.ffs4)
        data += struct.pack("<IIIIIIIIIIIIIIII", *self.ffs5)
        data += struct.pack("<IIIIIIII", *self.ffs6)

        self.ver_crc = checksum32(data, len(data))
        data += struct.pack("<I", self.ver_crc)
        return data


def main():
    header_ver = HeaderTypeVer()
    header_prg = HeaderTypePrg()

    out_dir = "out/"
    nb0_file = "work/patched/output.nb0"
    dir_name = "PLATFORM"
    prg_name = "PS140PLT.PRG"
    ver_name = "PS140PLT.VER"
    version, volume, pltdate = extract_file_metadata("work/" + prg_name)

    print(f"Версия: 0x{version:08X}")
    print(f"Том: {volume}")
    print(f"Дата: {pltdate}")

    # -------------------------------------------------------------------------
    # PRG file creation
    header_prg.file_length = os.path.getsize(nb0_file)
    with open(nb0_file, "rb") as f:
        nb0file_byte = f.read()
    header_prg.file_crc = checksum32(nb0file_byte, header_prg.file_length)
    header_prg.version = version
    header_prg.volume = volume
    header_prg.filename[: len(prg_name)] = prg_name.encode("ascii")
    header_prg.filedate[: len(pltdate)] = pltdate.encode("ascii")
    header_prg.file_length_prg = header_prg.file_length
    header_prg.file_crc1 = header_prg.file_crc

    with open(out_dir + prg_name, "wb") as f:
        f.write(bytearray(bytes(header_prg)))
        f.write(nb0file_byte)

    # -------------------------------------------------------------------------
    # VER file creation
    header_ver.set_version(version)
    header_ver.set_volume(volume)
    header_ver.nb0_length = header_prg.file_length
    header_ver.nb0_crc = header_prg.file_crc
    header_ver.dirname[: len(dir_name) * 2] = dir_name.encode("utf-16le")
    header_ver.filename[: len(prg_name) * 2] = prg_name.encode("utf-16le")
    header_ver.file_length = os.path.getsize(out_dir + prg_name)
    with open(out_dir + prg_name, "rb") as f:
        prg_byte = f.read()
    header_ver.file_crc = crc32b(prg_byte, header_ver.file_length)

    with open(out_dir + ver_name, "wb") as f:
        f.write(bytearray(bytes(header_ver)))


if __name__ == "__main__":
    main()

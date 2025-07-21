#!/bin/bash
cp /home/plavrovskiy/Downloads/jap/AVICRZ09/PLATFORM/PS140PLT.PRG .

wine ../sfk199-x64.exe partcopy PS140PLT.PRG -allfrom 0x200 output.nb0 -yes
mkdir DUMP
wine ../dumpromx.exe -d DUMP -v -5 output.nb0 > output.txt
cp DUMP/initDB.dat .
# rm -rf DUMP

cp ../translate translate
cp ../translation.txt translation.txt
./translate

cp -f initDB_out.dat initDB.dat
wine ../dumpromx.exe -a initDB.dat output.nb0
# rm -f output.nb0
mv -f initDB.dat.nb output.nb0
../makever
mkdir -p NAVIVUP/AVICRZ09/PLATFORM
cp -f PS140PLT.PRG NAVIVUP/AVICRZ09/PLATFORM/PS140PLT.PRG
cp -f PS140PLT.VER NAVIVUP/AVICRZ09/PS140PLT.VER
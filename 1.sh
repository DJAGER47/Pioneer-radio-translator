#!/bin/bash
cp /home/plavrovskiy/Downloads/jap/AVICRZ09/PLATFORM/PS140PLT.PRG work

python python/trim_file.py -i work/PS140PLT.PRG -o work/output.nb0
mkdir work/DUMP
wine dumpromx.exe -d work/DUMP -v -5 work/output.nb0 > work/output.txt
cp work/DUMP/initDB.dat work/
# rm -rf DUMP

python python/parsedat_to_string.py 

# cp ../translate translate
# cp ../translation.txt translation.txt
# ./translate

# cp -f initDB_out.dat initDB.dat
# wine ../dumpromx.exe -a initDB.dat output.nb0
# # rm -f output.nb0
# mv -f initDB.dat.nb output.nb0
# ../makever
# mkdir -p NAVIVUP/AVICRZ09/PLATFORM
# cp -f PS140PLT.PRG NAVIVUP/AVICRZ09/PLATFORM/PS140PLT.PRG
# cp -f PS140PLT.VER NAVIVUP/AVICRZ09/PS140PLT.VER
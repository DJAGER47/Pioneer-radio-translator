#!/bin/bash

rm -r work/*

cp /home/plavrovskiy/Downloads/jap/AVICRZ09/PLATFORM/PS140PLT.PRG work

python python/1_trim_file.py -i work/PS140PLT.PRG -o work/output.nb0
mkdir work/DUMP
wine dumpromx.exe -d work/DUMP -v -5 work/output.nb0 > work/output.txt
cp work/DUMP/initDB.dat work/
rm -rf work/DUMP

python python/2_find_str.py -i work/initDB.dat -o work/finded_str.json
python python/2.1_txt2json.py -i translation.txt -o work/4pda_translation.json
python python/2.2_merge_translations.py -i work/finded_str.json -t work/4pda_translation.json -o work/merge.json
python python/2.3_check_translations.py -i work/merge.json

python python/3_translate.py -i work/initDB.dat -t work/merge.json -o work/initDB_patch.dat

# cp -f initDB_out.dat initDB.dat
# wine ../dumpromx.exe -a initDB.dat output.nb0
# # rm -f output.nb0
# mv -f initDB.dat.nb output.nb0
# ../makever
# mkdir -p NAVIVUP/AVICRZ09/PLATFORM
# cp -f PS140PLT.PRG NAVIVUP/AVICRZ09/PLATFORM/PS140PLT.PRG
# cp -f PS140PLT.VER NAVIVUP/AVICRZ09/PS140PLT.VER
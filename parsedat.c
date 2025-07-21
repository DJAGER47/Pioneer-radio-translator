#define _CRT_SECURE_NO_WARNINGS  // Skip VS2017 warnings, remove for other compiler

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void hex2str(long input, char output[16]) {
	char tmpstr[9] = { 0 };
	sprintf(tmpstr, "%08X", input);
	for (int i = 0; i < 8; i++) {
		output[2 * i] = tmpstr[i];
	};
};

int main(int argc, char *argv[]) // Parse Japanese AVIC-RZ09 (and similar) data file initDB.dat and write strings with address, lenght, original string (UCS-2 LE encoding)
{
	const long OFFSET = 0x18C8D0L;   // RZ09 1.04 0x18C8D0L; RZ77 2.07 = 0x1EA87CL
	const long BLOCK_LEN = 0xAF00BL; // RZ09 1.04  0xAF00BL; RZ77 2.07 =  0xB5CDFL
	FILE *fin, *fout, *fout1;

	char *datfile = "initDB.dat";
	char fffe[2] = { 0xFF,0xFE };
	char div[2] = { 0x09, 0x00 }; //TAB=0x09  "=0x22
	char divcrlf[6] = { 0x09, 0x00, 0x0D, 0x00, 0x0A, 0x00 };
	char divcrlf1[6] = { 0x2D, 0x00, 0x0D, 0x00, 0x0A, 0x00 };
	char cr = 0x0D;
	char lf = 0x0A;
	char zero = 0x00;
	char str[1024] = { 0 };
	char tmpstr[16] = { 0 };
	
	fin = fopen(datfile, "rb");
	unsigned char *p = malloc(0xFF);

	//fout = fopen("parsed.txt", "wb");  // Parse 1st data block - plain 1-byte coding, no JP strings
	//fseek(fin, 0x0D5F10L, SEEK_SET);
	//fwrite(&div, 1, 1, fout);
	//for (unsigned int i = 0; i < 0xB69C0; i++) { //0x05FA;
	//	fread(p, 1, 1, fin);
	//	if (p[0] == 0xFF) continue;
	//	if (p[0] == 0x00) {
	//		fwrite(&div[1], 1, 1, fout);
	//		fwrite(&cr, 1, 1, fout);
	//		fwrite(&lf, 1, 1, fout);
	//		fwrite(&div[1], 1, 1, fout);
	//	} else
	//		fwrite(p, 1, 1, fout);
	//}
	//fclose(fout);
	//rewind(fin);
	
	fout1 = fopen("parsed1.txt", "wb");
	fseek(fin, OFFSET, SEEK_SET); 

	fwrite(&fffe, 2, 1, fout1); //BOM for UCS-2 LE - use Notepad++ (or other UCS-2 LE compatible editor, Chrome is OK for view strings) to see/edit results
	unsigned int index = 0;
	for (int i = 0; i < (BLOCK_LEN + 2) / 2; i++) {

		fread(p, 1, 2, fin);

		if (p[0] == 0xFF && p[1] == 0xFF) {
		//	fwrite(&divcrlf1, 6, 1, fout1); // Add divider to get FFFF sections
			index = 0;
			continue;
		};

		if (p[0] == 0x09 && p[1] == 0x00) {
			printf("Div addr = %2x\n", i * 2 + OFFSET);
		};

		if (p[0] == 0x00 && p[1] == 0x00) {
			if (index > 0) {
				if (index > 8 && str[index-8]==0x2E && str[index - 6] == 0x67 && str[index - 4] == 0x69 && str[index - 2] == 0x66) { // Skip links to images, .gif
					index = 0;
					continue;
				}
				if (index > 8 && str[index - 8] == 0x2E && str[index - 6] == 0x62 && str[index - 4] == 0x6D && str[index - 2] == 0x70) { // Skip links to images, .bmp
					index = 0;
					continue;
				}
				if (index > 8 && str[index - 8] == 0x2E && str[index - 6] == 0x70 && str[index - 4] == 0x6E && str[index - 2] == 0x67) { // Skip links to images, .png
					index = 0;
					continue;
				}
				if (index > 8 && str[index - 8] == 0x2E && str[index - 6] == 0x6A && str[index - 4] == 0x70 && str[index - 2] == 0x67) { // Skip links to images, .jpg
					index = 0;
					continue;
				}
				if (index > 8 && str[0] == 0x53 && str[2] == 0x54 && str[4] == 0x52 && str[6] == 0x5F) { // Skip "STR_" started strings
					index = 0;
					continue;
				}
				if (index > 8 && str[0] == 0x4D && str[2] == 0x53 && str[4] == 0x47 && str[6] == 0x5F) { // Skip "MSG_" started strings
					index = 0;
					continue;
				}
				if (index > 8 && str[0] == 0x4D && str[2] == 0x4D && str[4] == 0x5F) { // Skip "MM_" started strings
					index = 0;
					continue;
				}
				if (index > 2 && str[0] == 0x1B && str[1] == 0x00) { // Skip ESC sequences
					index = 0;
					continue;
				}
				if (index > 2 && str[0] == 0x23 && str[1] == 0x00) { // Skip # starts string IDs
					index = 0;
					continue;
				}
				
				long curraddr = OFFSET + i * 2 - index; // string address calc
				hex2str(curraddr, tmpstr);
				fwrite(&tmpstr, 16, 1, fout1);
				fwrite(&div, 2, 1, fout1);
				memset(tmpstr, 0, 16);
				hex2str(index, tmpstr);
				fwrite(&tmpstr, 16, 1, fout1); // string lenght
				fwrite(&div, 2, 1, fout1);
				for (unsigned int j = 0; j < index; j++)
					fwrite(&str[j], 1, 1, fout1);
				fwrite(&divcrlf, 6, 1, fout1);
				index = 0;
			};
			continue;
			//break;
		};

		str[index] = p[0];
		index++;
		str[index] = p[1];
		index++;

	};
	
	fclose(fout1);
	fclose(fin);
}
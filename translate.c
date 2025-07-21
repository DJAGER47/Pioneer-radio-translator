#define _CRT_SECURE_NO_WARNINGS

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct trans_struct {
	long len;
	char orig[1024];
	char tr1[1024];
	long tr_len;
} trans_string_struct;

char tr1[1024] = { 0 };

void hex2str(long input, char output[16]) {
	char tmpstr[9] = { 0 };
	sprintf(tmpstr, "%08lX", input);
	for (int i = 0; i < 8; i++) {
		output[2 * i] = tmpstr[i];
	};
};

long str2hex(char input[16]) {
	char tmpstr[9] = { 0 };
	long output;
	
	for (int i = 0; i < 8; i++) {
		tmpstr[i] = input[2 * i];
	};
	output = strtol(tmpstr, NULL, 16);
	return output;
};

void transfile_to_array(const unsigned char *data, long len, int line_cnt, trans_string_struct *in_arr) {
	unsigned char p_tmp[2];
	char c_str_len[16] = { 0 };
	long l_str_len = 0;
	const unsigned char *start_addr = data;
	char first_line = 1, new_line = 1, tab = 0, trans_idx = 1;
	int good_strings = 0, bad_strings = 0;
	
	if (*data == 0xFF) data++; // Skip BOM header
	if (*data == 0xFE) data++;
	
	p_tmp[0] = *data;
	data++;
	p_tmp[1] = *data;
	data++;

	int i = 0;

	while (i < line_cnt) {
		switch ((p_tmp[0] << 8) + p_tmp[1]) {
		case 0x0D00:
			p_tmp[0] = *data;
			data++;
			p_tmp[1] = *data;
			data++;
			if (p_tmp[0] == 0x0A && p_tmp[1] == 0x00) { // new line
				if (new_line == 0) i++;
				new_line = 1;
				if (i >= line_cnt) continue; //detect last line w/o data - exit from cycle
				p_tmp[0] = *data;
				data++;
				p_tmp[1] = *data;
				data++;
			}
			break;

		case 0x0900: //divider TAB detected
			p_tmp[0] = *data;
			data++;
			p_tmp[1] = *data;
			data++;
			tab = 1;
			break;

		default: // just get new 2-bytes
			if (first_line != 1) { //Not first string
				p_tmp[0] = *data;
				data++;
				p_tmp[1] = *data;
				data++;
			}
		};

		if (new_line == 1) {
			if (p_tmp[0] == 0x0D && p_tmp[1] == 0x00) { //New line again
				continue;
			}
			else
			{
				new_line = 0;
				if (first_line == 1) {
					first_line = 0;
					i = 0;
				}

				data--;
				data--;

				for (int j = 0; j < 16; j++) { // Get lenght of the original string
					c_str_len[j] = *data;
					data++;
				}
				l_str_len = str2hex(c_str_len);
				if ((l_str_len == 0) || (l_str_len > 1024)) { //if empty, not correct or too long string - mark it 0, no processing
					in_arr[i].len = 0;
					trans_idx = 0;
					bad_strings++;
				}
				else
				{
					in_arr[i].len = l_str_len;
					trans_idx = 1;
					good_strings++;
				};

				p_tmp[0] = *data;
				data++;
				p_tmp[1] = *data;
				data++;
			}

		}

		if (tab == 1) {
			int pos = 0;
			long trans_len = 0;
			do {
				if (p_tmp[0] == 0x09 && p_tmp[1] == 0x00) { // Next TAB detected, go out
					tab = 0;
					trans_idx = 2;
						continue;
					}
				if (p_tmp[0] == 0x0D && p_tmp[1] == 0x00) { // New line detected, go out
						tab = 0;
						continue;
				}
				
				if (trans_idx == 1) {
					in_arr[i].orig[pos] = p_tmp[0];
					pos++;
					in_arr[i].orig[pos] = p_tmp[1];
					pos++;
				}
				
				if (trans_idx == 2) {
					in_arr[i].tr1[pos] = p_tmp[0];
					pos++;
					in_arr[i].tr1[pos] = p_tmp[1];
					pos++;
					trans_len = trans_len + 2;
				}

				p_tmp[0] = *data;
				data++;
				p_tmp[1] = *data;
				data++;

			} while (tab);

			in_arr[i].tr_len = trans_len;

			// Print parsed string info
			printf("\nString #%d:\n", i+1);
			printf("Original length: %ld\n", in_arr[i].len);
			printf("Original text: ");
			for(int k=0; k<in_arr[i].len; k+=2) {
				if(in_arr[i].orig[k] != 0) printf("%c", in_arr[i].orig[k]);
			}
			printf("\nTranslation length: %ld\n", in_arr[i].tr_len);
			printf("Translation text: ");
			for(int k=0; k<in_arr[i].tr_len; k+=2) {
				if(in_arr[i].tr1[k] != 0) printf("%c", in_arr[i].tr1[k]);
			}
			printf("\n");
		}
		
		if ((data - start_addr) > len) break;

	}
	
	printf("Processed input strings = %d\n", line_cnt);
	printf("Good strings = %d\n", good_strings);
	printf("Bad strings (len > 1024) = %d\n", bad_strings);

};

int get_translation(long len, char *str, trans_string_struct *in_arr, int trans_line_idx_count, trans_string_struct *tr_arr) {
	
	int is_equal = 0;

	for (int i = 0; i < trans_line_idx_count; i++) {
		if ((in_arr[i].len > 0) && (len == in_arr[i].len)) {
			is_equal = 1;
			for (int j = 0; j < len; j++) {
				if (str[j] != in_arr[i].orig[j]) {
					is_equal = 0;
					break;
				}
			}
			if (is_equal) {
				*tr_arr = in_arr[i];
				//printf("%d ", i);  // uncomment to debug translated strings
				//for (int k = 0; k < tr_arr->tr_len;k++) {
				//	if(tr_arr->tr1[k] != 0x00 && tr_arr->tr1[k] != 0x0A) printf("%c", tr_arr->tr1[k]);
				//}
				//printf("\n");
				return 1;
			}
		}
	}

	return 0;
}

int main(int argc, char *argv[])
{

	const trans_string_struct empty_struct = {0,0,0};
	// 0x1CF2B8L; // RZ09 1.04 0x18C8D0L; RZ77 2.07 = 0x1EA87CL; ZH0009 = 0x147140
	// 0xB5CBFL;  // RZ09 1.04  0xAF00BL; RZ77 2.07 =  0xB5CDFL; ZH0009 =  0xACD7F
	const long OFFSET = 0x2671F4L;
	const long BLOCK_LEN = (long)0x3234D7 - OFFSET + 1;
	FILE *fin, *ftr, *fout;

	long trans_lenght, in_pos = 0, last_in_pos = 0;
	int trans_line_idx_count = 0;
	int processed_strings_cnt = 0, found_strings_cnt = 0;

	char *datfile = "initDB.dat";
	char *transfile = "translation.txt";
	char *datfileout = "initDB_out.dat";
	char fffe[2] = { 0xFF,0xFE };
	char div[2] = { 0x09, 0x00 }; //TAB 0x09  " 0x22
	char divcrlf[6] = { 0x09, 0x00, 0x0D, 0x00, 0x0A, 0x00 };
	char cr = 0x0D;
	char lf = 0x0A;
	char zero = 0x00;
	char str[1024] = { 0 };
	char tmpstr[16] = { 0 };
	
	ftr = fopen(transfile, "rb");
	fseek(ftr, 0L, SEEK_END);
	trans_lenght = ftell(ftr);
	unsigned char *p_trans = malloc(trans_lenght);
	rewind(ftr);

	unsigned char *p_tmp = malloc(0xF);
	int str_cnt = 0;

	fread(p_tmp, 1, 2, ftr); // Skip BOM header
	while (!feof(ftr)) // Counts strings in the translation file exclude empty strings
	{
		fread(p_tmp, 1, 2, ftr);
		if (p_tmp[0] == 0x0D && p_tmp[1] == 0x00)
		{
			fread(p_tmp, 1, 2, ftr);
			if (p_tmp[0] == 0x0A && p_tmp[1] == 0x00 && str_cnt > 0) {
				trans_line_idx_count++;
				str_cnt = 0;
			}
		}
		else str_cnt++;
	}

	trans_string_struct *in_arr = malloc(trans_line_idx_count * sizeof(*in_arr));
	for (int i = 0; i < trans_line_idx_count; i++) { // Initialize trans strings struct
		in_arr[i] = empty_struct;
	};

	trans_string_struct *tr_arr = malloc(sizeof(*tr_arr));
	tr_arr[0] = empty_struct;
	
	int *trans_strings_size = malloc(trans_line_idx_count * sizeof(*trans_strings_size));
	char *trans_strings_orig = malloc(trans_line_idx_count * sizeof(*trans_strings_orig));

	rewind(ftr);
	fread(p_trans, 1, trans_lenght, ftr);

	transfile_to_array(p_trans, trans_lenght, trans_line_idx_count, in_arr);
	
	fin = fopen(datfile, "rb");
	unsigned char *p_out = malloc(OFFSET);
	fread(p_out, 1, OFFSET, fin);
	rewind(fin);

	fout = fopen(datfileout, "wb");
	fwrite(p_out, 1, OFFSET, fout);
	in_pos = OFFSET;
	last_in_pos = OFFSET;
	free(p_out);

	unsigned char *p = malloc(0xFF);
	fseek(fin, OFFSET, SEEK_SET); //0x18C0D4L
	unsigned int index = 0;
	
	for (int i = 0; i < (BLOCK_LEN + 2) / 2; i++) {

		fread(p, 1, 2, fin);

		if (p[0] == 0xFF && p[1] == 0xFF) {
			index = 0;
			continue;
		};

		if (p[0] == 0x00 && p[1] == 0x00) {
			if (index > 0) {
				if (index > 8 && str[index - 8] == 0x2E && str[index - 6] == 0x67 && str[index - 4] == 0x69 && str[index - 2] == 0x66) { // Skip links to images, .gif
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

				if (get_translation(index, str, in_arr, trans_line_idx_count, tr_arr)) {
					//printf("Str lenght = %2X\n", index);
					//printf("Str = %s\n", str);
					//printf("Tr1 = %s\n", tr_arr->tr1);
					found_strings_cnt++;
					if (tr_arr->tr_len > 0) { // If translation string is empty (len == 0), skip changing the data-file
						in_pos = OFFSET + (i + 1) * 2 - (index + 2); //Input data file string start position
						//printf("Position for start writing = %2X\n", last_in_pos);
						//printf("Position for out string = %2X\n", in_pos);
						//printf("Bytes to write = %2X\n", in_pos - last_in_pos);

						long in_curr_pos = ftell(fin);
						long in_bytes_as_is = in_pos - last_in_pos;

						rewind(fin);
						fseek(fin, last_in_pos, SEEK_SET);
						unsigned char *p_out = malloc(in_bytes_as_is);
						fread(p_out, 1, in_bytes_as_is, fin);
						fseek(fout, 0L, SEEK_END);
						fwrite(p_out, 1, in_bytes_as_is, fout);
						if (tr_arr[0].len != tr_arr[0].tr_len) {
							printf("WARNING!!! Translation string is not equal to original string:\norig_len = %2lX orig = %s \ntrsn_len = %2lX tran = ", tr_arr[0].len, tr_arr[0].orig, tr_arr[0].tr_len);
							for (int k = 0; k < tr_arr[0].len;k++) {
								if(tr_arr[0].tr1[k] != 0x00) printf("%c", tr_arr[0].tr1[k]);
							}
							printf("\n");
						}
							

						//fwrite(&tr_arr[0].tr1, 1, tr_arr[0].tr_len + 2, fout); // Get len as translation file string len !!! be careful!!
						fwrite(&tr_arr[0].tr1, 1, tr_arr[0].len + 2, fout); // Get len from sorce DAT file str
						rewind(fin);
						fseek(fin, in_curr_pos, SEEK_SET);
						last_in_pos = in_curr_pos;
					}
				} 

				processed_strings_cnt++;
				index = 0;
				memset(str, 0, sizeof(str));
			};
			continue;
		};

		str[index] = p[0];
		index++;
		str[index] = p[1];
		index++;
	};

	long in_bytes_as_is = OFFSET + BLOCK_LEN + 1 - last_in_pos;
	rewind(fin);
	fseek(fin, last_in_pos, SEEK_SET);
	unsigned char *p_out1 = malloc(in_bytes_as_is);
	fread(p_out1, 1, in_bytes_as_is, fin);
	fseek(fout, 0L, SEEK_END);
	fwrite(p_out1, 1, in_bytes_as_is, fout);

	printf("Processed strings in data file = %d\n", processed_strings_cnt);
	printf("Found strings in data file = %d\n", found_strings_cnt);

	fclose(ftr);
	fclose(fin);
	fclose(fout);
}
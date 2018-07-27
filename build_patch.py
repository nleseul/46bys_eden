#!/usr/bin/python3

import os
import subprocess
import sys

import csv
from ips_util import Patch

import text_util
import gfx_util

class StringPool:
    def __init__(self, address, capacity):
        self.address = address
        self.capacity = capacity
        
        self.pool = bytearray()
        
    def can_add(self, bytes):
        return len(self.pool) + len(bytes) < self.capacity
        
    def add(self, bytes):
        start = len(self.pool) + self.address
        
        self.pool += bytes
        
        return start
        
    def get_bytes(self):
        return self.pool
        
def write_with_size_check(patch, address, available_length, data, fill_byte=b'\x00'):
    difference = available_length - len(data)
    if difference < 0:
        raise Exception('Not enough space for data! Received {0} bytes, but only have space allocated for {1}.'.format(len(data), available_length))
        
    patch.add_record(address, data)
    
    if difference > 0:
        patch.add_rle_record(address + len(data), fill_byte, difference)


def write_strings_from_csv(patch, filename, reverse_font_map, pointer_table_address, pointer_table_length, 
                           string_pool_address, string_pool_length, overflow_pool_address = None, overflow_pool_length = None,
                           column_to_encode=4, newline=b'\xfe', terminator=b'\xff', pad_to_line_count=1, pad_final_line=False):
    pointer_table_out = bytearray()
    previously_encoded = {}
    
    pools = [StringPool(string_pool_address, string_pool_length)]
    
    if overflow_pool_address is not None and overflow_pool_length is not None:
        pools.append(StringPool(overflow_pool_address, overflow_pool_length))
    
    with open(filename, 'r', encoding='shift-jis') as in_file:
        reader = csv.reader(in_file, lineterminator='\n')
        for i, row in enumerate(reader):
            #flag_map = {7: 0x2, 9: 0x4, 10: 0x8, 16: 0x8}
            #encoded_string = encode_text_interleaved(row[4], reverse_map, i != 15, flag_map[i] if i in flag_map else 0x1)
            
            #encoded_string = text_util.encode_text(row[4], reverse_font_map)
            #encoded_string = encode_text(row[4], reverse_map, pad_to_line_count=6, pad_final_line=True)
            #encoded_string = encode_text(row[4], reverse_map, newline=b'\xff\xfe', terminator=b'\xff\xff')
            encoded_string = text_util.encode_text(row[column_to_encode], reverse_font_map, 
                                                   pad_to_line_count=pad_to_line_count, pad_final_line=pad_final_line,
                                                   newline=newline, terminator=terminator)
            
            string_address = None
            if encoded_string in previously_encoded:
                string_address = previously_encoded[encoded_string]
            else:
                for pool in pools:
                    if pool.can_add(encoded_string):
                        string_address = (0xffff & pool.add(encoded_string))
                        break
                        
                if string_address is not None:
                    previously_encoded[encoded_string] = string_address
            
            if string_address is None:
                print('Text {0} didn\'t fit!'.format(row[4]))
                pointer_table_out += (0xffff).to_bytes(2, byteorder='little')
            else:
                pointer_table_out += string_address.to_bytes(2, byteorder='little')
    
    write_with_size_check(patch, pointer_table_address, pointer_table_length, pointer_table_out)
    for pool in pools:
        write_with_size_check(patch, pool.address, pool.capacity, pool.get_bytes(), fill_byte=b'\xff')
        
def write_gfx(patch, data, address, length):
    write_with_size_check(patch, address, length, gfx_util.compress(data))

def write_gfx_from_file(patch, filename, address, length):
    with open(filename, 'rb') as f:
        write_gfx(patch, f.read(), address, length)

def write_code(patch, filename, address, length):
    tmp_filename = 'build/_tmp.a65'
    result = subprocess.run(['xa', '-o', tmp_filename, '-w', filename], stderr=subprocess.PIPE)
    if result.returncode == 0:
        with open(tmp_filename, 'rb') as tmp_file:
            write_with_size_check(patch, address, length, tmp_file.read())
        os.remove(tmp_filename)
    else:
        raise Exception('Assembler failed on {0} with error code {1}:\n\nErrors:\n{2}'.format(filename, result.returncode, result.stderr.decode(sys.stderr.encoding)))


if __name__ == '__main__':
    os.makedirs('build', exist_ok=True)

    reverse_font_map = text_util.load_map_reverse('assets/text/font.tbl')

    patch = Patch()

    # New tiles for digits in font.
    patch.add_record(0x488a, b'\xB5\xB6\xB7\xB8')

    write_code(patch, 'assets/code/menu text.asm', 0x4f90, 309)

    write_strings_from_csv(patch, 'assets/text/dialog_bank_1.csv', reverse_font_map, 0x1d2b3, 29 * 2, 0x1d2ed, 6766, pad_to_line_count=6, pad_final_line=True)
    write_strings_from_csv(patch, 'assets/text/dialog_bank_2.csv', reverse_font_map, 0xfb719, 81 * 2, 0xfb7bb, 18185, 0xfa730, 944, pad_to_line_count=6, pad_final_line=True)
    write_strings_from_csv(patch, 'assets/text/dialog_bank_3.csv', reverse_font_map, 0xedfc1, 33 * 2, 0xee011, 6684, pad_to_line_count=6, pad_final_line=True)

    with open('assets/gfx/font.bin', 'rb') as font_file:
        font_data = font_file.read()
        write_gfx(patch, font_data, 0x79358, 2578)
        write_gfx(patch, font_data[0x200:0x600], 0x77c7e, 711)

    with open('build/test.ips', 'w+b') as f:
        f.write(patch.encode())
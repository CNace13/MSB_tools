#!/usr/bin/env python3

"""
  Author:        Connor Nace (PeacockSlayer)
  Date:          03/18/2021
  Last Modified: 03/20/2021
  Description:
    This script was written to generate gecko codes and patch notes
    for MSB
  Features:
    -m path to modified csv
    -p Path to csv with the previous balance patch. If generated, balance path notes will be the delta between modded and previous csvs
    -g generates patch notes for gecko codes

"""

import argparse
import csv
import os

from StatParser import StatParser

#Used to take hex values from cmd line
def auto_int(x):
    return int(x, 0)
    

DEFAULT_STATS_PATH = '../ref/msb_default.csv'
STAT_INFO_PATH     = '../ref/stat_info.json'

#Consts
cCHEM_TABLE_START = 0x3b

cGCF_EXT = '_gcf.txt'
cBPN_EXT = '_bpn.txt'

def getArgs():
    parser = argparse.ArgumentParser(usage="A helpful tool for generating gecko codes for balance patches for Mario Superstar Baseball")
    parser.add_argument('-m', '--modified_csv', required=True, type=str, help="Path to csv with modified stat value")
    parser.add_argument('-p', '--previous_version_csv', required=False, type=str, 
                        help="Path to csv with the previous balance patch. If generated, balance path notes will be the delta between modded and previous csvs")
    #General flags
    parser.add_argument('-g', '--generate_patch_notes', required=False, action='store_true', help="Generates patch notes")
    
    return parser

def build_char_lists():
    pass

#Construct Gecko codes for stat deltas.
#Append codes to file then close
def gen_gecko_codes(addr, modded_char, offset_list, gecko_file_name):
    gecko_list = list()

    gecko_file = open(gecko_file_name+cGCF_EXT, 'a')

    if len(offset_list) > 0:
        for single_stat_idx in offset_list:
            gecko_op = (0x00FFFFFF & (addr+single_stat_idx))
            gecko_op = "{0:#0{1}x}".format(gecko_op,10)[2:]
            
            raw_value = modded_char.stat_dict[single_stat_idx].value
            gecko_value = "{0:#0{1}x}".format(raw_value,10)[2:] #Gets 8 digit hex. Remove 0x
            gecko_code = gecko_op + ' ' + gecko_value + '\n'

            gecko_file.write(gecko_code)
        gecko_file.write('\n')
    gecko_file.close()

#Create human readable patch notes for each stat delta
#Append notes to file then close
def gen_balance_patch_notes(prev_char, modded_char, offset_list, gecko_file_name):
    bpn_list = list()

    bpn_file = open(gecko_file_name+cBPN_EXT, 'a')

    if len(offset_list) > 0:
        name = modded_char.name
        bpn_file.write(name + '\n')
        for single_stat_idx in offset_list:
            stat_name = prev_char.stat_dict[single_stat_idx].name

            prev_val = prev_char.stat_dict[single_stat_idx].value
            prev_value_hrv = prev_char.stat_dict[single_stat_idx].human_readable_value

            new_value = modded_char.stat_dict[single_stat_idx].value
            new_value_hrv = modded_char.stat_dict[single_stat_idx].human_readable_value

            if new_value_hrv != '':
                if new_value_hrv >= prev_value_hrv:
                    new_value_hrv = '({})'.format(new_value_hrv)
                else:
                    new_value_hrv = '({}->{})'.format(prev_value_hrv, new_value_hrv)

            delta_string = '  {}:  {}->{} {}\n'.format(stat_name, prev_val, new_value, new_value_hrv)

            bpn_file.write(delta_string)
        bpn_file.write('\n')
    bpn_file.close()
        
def cmpr_lists(in_previous_version, in_modded_version, gecko_file, generate_bpn):
    for prev_char in in_previous_version:
        for modded_char in in_modded_version:
            #Find char for each version
            if prev_char.char_id == modded_char.char_id:
                #Start comparing stats
                diff_idx_list = prev_char.cmpr_stats(modded_char)
                gen_gecko_codes(prev_char.addr, modded_char, diff_idx_list, gecko_file)
                if (generate_bpn):
                    gen_balance_patch_notes(prev_char, modded_char, diff_idx_list, gecko_file)
                

if __name__ == "__main__":
    args = getArgs()
    args = args.parse_args()

    previous_version_csv = DEFAULT_STATS_PATH
    if args.previous_version_csv != None:
        previous_version_csv = args.previous_version_csv
        
    sp = StatParser(previous_version_csv, args.modified_csv, STAT_INFO_PATH)
    default_char_list = sp.parse_chars(True)
    modified_char_list = sp.parse_chars(False)
    previous_version_base = os.path.basename(previous_version_csv)
    modded_version_base   = os.path.basename(args.modified_csv)

    gecko_file_name = '../patches/' + os.path.splitext(previous_version_base)[0]+'~'+ os.path.splitext(modded_version_base)[0]
    #patch_notes_name
    #Delete soon to be duplicate file
    try:
        os.remove(gecko_file_name+cGCF_EXT)
    except OSError:
        pass
    try:
        os.remove(gecko_file_name+cBPN_EXT)
    except OSError:
        pass
    cmpr_lists(default_char_list, modified_char_list, gecko_file_name, args.generate_patch_notes)

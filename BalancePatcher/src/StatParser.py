import csv
import json
import re

from Character import MSBChar, Stat

cCHAR_IDS = { 0x0: "Mario", 0x1: "Luigi", 0x2: "DK", 0x3: "Diddy", 0x4: "Peach", 0x5: "Daisy", 0x6: "Yoshi", 
              0x7: "Baby Mario", 0x8: "Baby Luigi", 0x9: "Bowser", 0xA: "Wario", 0xB: "Waluigi", 0xC:"Koopa-Red",
              0xD: "Toad-Red", 0xE: "Boo", 0xF: "Toadette", 0x10: "Shy Guy-Red", 0x11: "Birdo", 0x12: "Monty", 
              0x13: "Bowser Jr", 0x14: "Paratroopa-Red", 0x15: "Pianta-Blue", 0x16: "Pianta-Red", 0x17: "Pianta-Yellow",
              0x18: "Noki-Blue", 0x19: "Noki-Red", 0x1A: "Noki-Green", 0x1B: "Bro-Hammer", 0x1C: "Toadsworth", 0x1D: "Toad-Blue",
              0x1E: "Toad-Yellow", 0x1F: "Toad-Green", 0x20: "Toad-Purple", 0x21: "Magikoopa-Blue", 0x22: "Magikoopa-Red",
              0x23: "Magikoopa-Green", 0x24: "Magikoopa-Yellow", 0x25: "King Boo", 0x26: "Petey", 0x27: "Dixie", 
              0x28: "Goomba", 0x29: "Paragoomba", 0x2A: "Koopa-Green", 0x2B: "Paratroopa-Green", 0x2C: "Shy Guy-Blue", 
              0x2D: "Shy Guy-Yellow", 0x2E: "Shy Guy-Green", 0x2F: "Shy Guy-Black", 0x30: "Dry Bones-Gray", 0x31: "Dry Bones-Green", 
              0x32: "Dry Bones-Red", 0x33: "Dry Bones-Blue", 0x34: "Bro-Fire", 0x35: "Bro-Boomer"}

#Consts
cCHEM_TABLE_START = 0x3b

class StatParser:
    def __init__(self, default_csv, modified_csv, stat_json):
        self.default_csv  = default_csv
        self.modified_csv = modified_csv
        self.stat_json    = stat_json

        with open(self.stat_json) as f:
            self.data = json.load(f)
    
    def getStrFromValues(self, offset, in_value):
        human_readable_value = ''
        chem_link_char = 0
        if offset >= cCHEM_TABLE_START:
            chem_link_char_id = offset - cCHEM_TABLE_START
            offset = cCHEM_TABLE_START 
        for entry in self.data:
            if int(str(entry['id']), 16) == offset:
                #If this is a chemistry value
                if offset == cCHEM_TABLE_START:
                    human_readable_value = cCHAR_IDS[chem_link_char_id]
                    return human_readable_value
                #Get dict of valid strs and their values
                for valid_str_dict in entry['vld_inputs']:
                    dict_key   = list(valid_str_dict.keys())[0]
                    dict_value = list(valid_str_dict.values())[0]
                    #If its a single type we can return as soon as we get a match
                    if entry['type'] == 'Single':
                        if dict_value == in_value:
                            human_readable_value = dict_key
                            return human_readable_value
                    #If its multiple we must build the string via bit masking
                    elif entry['type'] == 'Multiple':
                        if (dict_value & in_value):
                            if human_readable_value == '':
                                human_readable_value = dict_key
                            else:
                                human_readable_value = human_readable_value + ', ' + dict_key
                return human_readable_value 

    
    def getValueFromStr(self, json_entry, in_str):
        pass
        
    def build_char(self, csv_row):
        char_id = ''
        name = ''
        add = 0 
        msb_char = None
        for idx, stat in enumerate(csv_row, start=-3):
            if idx == -3:
                char_id = int(str(stat), 16)
                name = cCHAR_IDS[char_id]
            elif idx == -1:
                addr = int(str(stat), 16)
                msb_char = MSBChar(char_id, name, addr)
            elif idx >= 0:
                #json_entry = get_json_entry()
                value = 0
                human_readable_value = ''
                try:
                    value = int(stat)
                except ValueError as verr: #Was passed a string. Perform lookup
                    value = str(stat)
                    val_int, human_readable_value = self.validate_str(idx, stat)
                    if val_int == -1:
                        value = 0
                        raise ValueError('Invalid String for stat' + idx)
                    else:
                        value = val_int
                #Final validation to make sure we are bewteen values
                value, name = self.validate_val(idx, value)
                if value != None:
                    human_readable_value = self.getStrFromValues(idx, value)
                    stat_obj = Stat(idx, name, value, human_readable_value)
                    msb_char.add_stat(idx, stat_obj)
        return msb_char

    def parse_chars(self, default):
        char_list = list()
        path = ''
        if default:
            path = self.default_csv
        else:
            path = self.modified_csv
        with open(path, 'r', newline='') as csv_f:
            csv_reader = csv.reader(csv_f, delimiter=',')
            for line, row in enumerate(csv_reader):
                if line == 0:
                    continue
                else:
                    char_list.append(self.build_char(row))
        return char_list
                        
    def validate_val(self, offset, in_value):
        #print(self.data)
        for entry in self.data:
            if offset >= cCHEM_TABLE_START:
                offset = cCHEM_TABLE_START
            if int(str(entry['id']), 16) == offset:
                stat_name = entry['name']
                if (in_value >= int(entry['min']) and in_value <= int(entry['max']) ):
                    #print(entry['min'], in_value, entry['max'] )
                    return in_value, stat_name
                else:
                    raise ValueError('ID='+offset + 'Value='+str(in_value)+' not in range')
                    return 0, stat_name
        return None, None

    def validate_str(self, offset, in_string):
        for entry in self.data:
            if int(str(entry['id']), 16) == offset:
                value = 0
                human_value = ''
                #If only a single string is allowed
                if entry['type'] == 'Single':
                    input_string = in_string
                    re.sub(r'\W+', '', input_string)
                    input_string = input_string.replace(' ', '') #Get this into the regex
                    input_string = input_string.lower()
                    for valid_str_dict in entry['vld_inputs']:
                        key = list(valid_str_dict.keys())[0]
                        valid_str = key.replace(' ', '')
                        valid_str = valid_str.lower()
                        if input_string in valid_str:
                            input_string_value = valid_str_dict[key]
                            value = input_string_value
                            human_value = key
                            return value, key
                #If multiple values are allowed split them by '+' sign
                #Iterate through vld_input list of dicts. If the str from stat_csv 
                #is found in the vld_inputs dict then add the value from the dict.
                #Repeat for all strs in csv 
                elif entry['type'] == 'Multiple':
                    in_string_list = in_string.split('+')
                    for input_string in in_string_list:
                        re.sub(r'\W+', '', input_string)
                        input_string = input_string.replace(' ', '') #Get this into the regex
                        input_string = input_string.lower()
                        for valid_str_dict in entry['vld_inputs']:
                            key = list(valid_str_dict.keys())[0]
                            valid_str = key.replace(' ', '')
                            valid_str = valid_str.lower()
                            if input_string in valid_str:
                                input_string_value = valid_str_dict[key]
                                value = value + int(input_string_value)
                                if human_value == '':
                                    human_value = key
                                else:
                                    human_value = human_value + ', ' + key
                    return value, human_value[:-2]
        return None #We got to the end of the stat_json and this offset is not used


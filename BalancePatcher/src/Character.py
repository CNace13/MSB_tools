class MSBChar:
    def __init__(self, char_id, name, addr):
        self.stat_dict = dict() 
        self.char_id   = char_id
        self.name      = name
        self.addr      = addr
        #Iterate over stat string and record values at idx=0
    
    def add_stat(self, offset, stat):
        self.stat_dict[offset] = stat

    def print_stats(self):
        print(self)
        for stat in self.stat_dict.values():
            print('  ', stat)

    #Return list of offsets of different stats
    def cmpr_stats(self, modded_char):
        if not isinstance(modded_char, MSBChar):
            # don't attempt to compare against unrelated types
            return NotImplemented
        else:
            diff_idx_list = list()
            for key, stat in self.stat_dict.items():
                modded_stat = modded_char.stat_dict[key]
                if stat != modded_stat:
                    diff_idx_list.append(stat.offset)
            return diff_idx_list

                
    
    def __str__(self):
        return 'Char_ID {}  Name: {}  Addr={}'.format(hex(self.char_id), self.name, self.addr)
        

class Stat:
    def __init__(self, offset, name, value, human_readable_value=''):
        self.offset               = offset
        self.name                 = name
        self.value                = value
        self.human_readable_value = human_readable_value

    def __eq__(self, other): 
        if not isinstance(other, Stat):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return self.value == other.value

    def __str__(self):
        id_hex = str(int(str(self.offset),16))
        return '  ({})  Name: {}  Value={} ({})'.format(hex(self.offset), self.name, self.value, self.human_readable_value)
'''
Created on Mar 21, 2011

@author: arif
'''

class NamelistReader():
    '''
    Class untuk membaca file namelist.input wrf
    '''
    def __init__(self, filepath):
        self.data = {}
        self.current_section = ''
        fdat = open(filepath)
        skip = True
        for l in fdat:
            line = l.strip()
            if len(line) < 1:
                continue
            
            if line[0]=='&':
                section_name = line.strip('&')
                self.data[section_name] = {}
                skip = False
                self.current_section = section_name
            elif line[0]=='/':
                skip = True
            elif skip==False:
                val = line.split('=')
                if len(val) < 2:
                    continue
                header = val[0].strip()
                item_data = val[1].split(',')
                tmp = []
                for el_data in item_data:
                    el = el_data.strip(" \'\"")
                    if len(el) > 0:
                        tmp.append(el)
                self.data[self.current_section][header] = tmp 

class WPSNamelistReader(NamelistReader):
    """Class untuk membaca file namelist.wps"""
    def __init__(self, filepath):
        NamelistReader.__init__(self, filepath)
        self.maxdom  = int(self.data['share']['max_dom'][0])
        self.ref_lat = float(self.data['geogrid']['ref_lat'][0])
        self.ref_lon = float(self.data['geogrid']['ref_lon'][0])
        self.dom_dx = int(self.data['geogrid']['dx'][0])
        self.dom_dy = int(self.data['geogrid']['dy'][0])
        self.e_we   = []
        self.e_sn   = []
        self.parent_id         = []
        self.i_parent_start    = []
        self.j_parent_start    = []
        self.parent_grid_ratio = []
        for el in self.data['geogrid']['e_we']:
            self.e_we.append(int(el))
        for el in self.data['geogrid']['e_sn']:
            self.e_sn.append(int(el))
        for el in self.data['geogrid']['i_parent_start']:
            self.i_parent_start.append(int(el))
        for el in self.data['geogrid']['j_parent_start']:
            self.j_parent_start.append(int(el))
        for el in self.data['geogrid']['parent_grid_ratio']:
            self.parent_grid_ratio.append(int(el))
        for el in self.data['geogrid']['parent_id']:
            self.parent_id.append(int(el))

if __name__ == '__main__':
    print ' test... '
    path = 'res/namelist.wps'
    reader = NamelistReader(path)
    wpsreader = WPSNamelistReader(path)
    
    print wpsreader.dom_dx
    print wpsreader.parent_grid_ratio
    print reader.data['geogrid']
    
    

"""
Modul konversi utama
"""
import data_downscaler
import namelist_reader
import domain_data
import pupynere
import commons
import os
import cPickle
from openpyxl.reader.excel import load_workbook

def opj(path):
    """Convert paths to the platform-specific separator"""
    st = apply(os.path.join, tuple(path.split('/')))
    # HACK: on Linux, a leading / gets lost...
    if path.startswith('/'):
        st = '/' + st
    return st


class PayloadThreadProc(commons.BaseThreadProc):
    def __init__(self):
        commons.BaseThreadProc.__init__(self)
        self.save_dir        = ""
        self.namelist        = None
        self.maxdom          = 0
        self.domains         = []
        self.eg              = [] #per pollutant
        self.workbook        = None
        self.width           = 0
        self.height          = 0
        self.domain_emiss    = [] #dimensi: domain, y, x, pollutant
        self.data_list       = [] #per pollutant
        self.conv_factor     = []
        self.source_list     = []
        self.pollutant_list  = ['E_ALD', 'E_CO', 'E_CSL', 'E_ECI', 'E_ECJ', 
                               'E_ETH', 'E_HC3', 'E_HC5', 'E_HC8', 'E_HCHO', 
                               'E_ISO', 'E_KET', 'E_NH3', 'E_NO', 'E_NO3I', 
                               'E_NO3J', 'E_OL2', 'E_OLI', 'E_OLT', 'E_ORA2', 
                               'E_ORGI', 'E_ORGJ', 'E_PM25I', 'E_PM25J', 'E_PM_10', 
                               'E_SO2', 'E_SO4I', 'E_SO4J', 'E_TOL', 'E_XYL']
        self.additional_pollutan_list = [] #custom polutant id di sini
        self.pollutant_str = []
    
    def load_namelist(self):
        print "debug: Namelist processing start"
        self.progress("Reading Namelist")
        self.maxdom = self.namelist.maxdom
        for i in range(self.maxdom):
            parent = self.namelist.parent_id[i] - 1
            domain = None
            self.progress("Reading domain {0}".format(i + 1))
            if i == 0:
                #topdomain
                domain = domain_data.TopDomain()
                domain.lat = self.namelist.ref_lat
                domain.lon = self.namelist.ref_lon
                domain.w   = self.namelist.e_we[0] - 1
                domain.h   = self.namelist.e_sn[0] - 1
                domain.dx  = self.namelist.dom_dx
                domain.dy  = self.namelist.dom_dy
                domain.process_boundary()
                print "debug: TopDomain"
            else:
                #TODO, mungkin support sibling subdomain
                print "debug: SubDomain start, parent ", parent
                print i
                print self.domains[parent]
                print self.namelist.i_parent_start
                print self.namelist.j_parent_start
                print self.namelist.parent_grid_ratio
                domain = domain_data.SubDomain(self.domains[parent], self.namelist.i_parent_start[i], 
                                               self.namelist.j_parent_start[i], 
                                               self.namelist.parent_grid_ratio[i])
                print "debug: 2"
                domain.w   = self.namelist.e_we[i] - 1
                print "debug: 3"
                domain.h   = self.namelist.e_sn[i] - 1
                print "debug: 4"
                domain.process_boundary()
                print "debug: SubDomain end, parent ", parent
            
            self.domains.append(domain)
            
        print "debug: total domain:", len(self.domains)
        print "debug: Namelist processing end"
        print "------------------------------"
        
    def process_pollutant_list(self):
        print "debug: Pollutant processing start"
        self.progress("Processing pollutant list")
        
        for source in self.source_list:
            print "processing ", source.__str__()
            self.data_list.append([])
            self.conv_factor.append(source.conversion_factor)
            self.pollutant_str.append(source.pollutant)
            try:
                self.pollutant_list.index(source.pollutant)
            except:
                self.additional_pollutan_list.append(source.pollutant)
            
        print "debug: Pollutant processing end"
        print "------------------------------"

    def load_worksheet_data(self):
        print "debug: Worksheet processing start"
        self.progress("Reading Worksheet")
        
        sheet_names = self.workbook.get_sheet_names()
        
        for i, source in enumerate(self.source_list):
            self.progress("Reading data for {0} from {1}".format(source.pollutant, sheet_names[source.worksheet]))
            sheet = self.workbook.worksheets[source.worksheet]
            range_x_str = "{0}{1}:{0}{2}".format(source.x_column, source.row_start, source.row_end)
            range_y_str = "{0}{1}:{0}{2}".format(source.y_column, source.row_start, source.row_end)
            range_lat_str = "{0}{1}:{0}{2}".format(source.lat_column, source.row_start, source.row_end)
            range_lon_str = "{0}{1}:{0}{2}".format(source.lon_column, source.row_start, source.row_end)
            range_emiss_str = "{0}{1}:{0}{2}".format(source.emission_column, source.row_start, source.row_end)
            cells_x = sheet.range(range_x_str)
            cells_y = sheet.range(range_y_str)
            cells_lat = sheet.range(range_lat_str)
            cells_lon = sheet.range(range_lon_str)
            cells_emiss = sheet.range(range_emiss_str)
            
            data_len = len(cells_x)
            print "debug: Saving list data..."
            for j in range(data_len):
                tmp_x = cells_x[j][0].value
                tmp_y = cells_y[j][0].value
                tmp_lat = cells_lat[j][0].value
                tmp_lon = cells_lon[j][0].value
                tmp_conc = cells_emiss[j][0].value
                tmp_rowdata = data_downscaler.RowData(tmp_lat, tmp_lon, tmp_x, tmp_y, tmp_conc)
                self.data_list[i].append(tmp_rowdata)
            
            print "debug: Sorting list data..."
            self.data_list[i].sort(data_downscaler.compare_rowdata_m)
        
        print "debug: Worksheet processing end"
        print "------------------------------"
        
    def create_emission_group(self):
        print "debug: Emission Group processing start"
        self.progress("Constructing Emission Group")
        
        for n, data in enumerate(self.data_list):
            eg = data_downscaler.EmissGroup()
            eg.set_dimension(self.width, self.height)
            eg.conv_factor = self.conv_factor[n]
            i = 0
            for y in range(self.height):
                for x in range(self.width):
                    row_data = self.data_list[n][i]
                    tmp = data_downscaler.EmissData()
                    tmp.conc = row_data.data
                    tmp.lat = row_data.lat
                    tmp.lon = row_data.lon
                    tmp.x = row_data.x
                    tmp.y = row_data.y
                    eg.append_data(tmp)
                    i = i + 1
            
            eg.compute_boundary()
            self.eg.append(eg)            
        
        print "debug: Emission Group processing end"
        print "------------------------------"
    
    def compute_emission(self):
        print "debug: Emission interpolation start"
        
        for n_dom, domain in enumerate(self.domains):
            domain_dat = []
            for y in range(domain.h):
                y_dat = []
                for x in range(domain.w):
                    x_dat = []
                    ll, tr = domain.get_cell_boundary_latlon(x, y)
                    for n_eg, eg in enumerate(self.eg):
                        self.progress("Computing Emission for Domain {0}: {1},{2}".format(n_dom+1, x, y))
                        conc = eg.get_average_conc_latlon(ll, tr)
                        print x, y, ':', conc 
                        x_dat.append(conc)
                        if self.abort:
                            print "Aborting..."
                            self.done()
                    y_dat.append(x_dat)
                domain_dat.append(y_dat)
            self.domain_emiss.append(domain_dat)
        
        #TODO: debug
#        print "debug: Saving cache"
#        print os.getcwd()
#        cache_file = open("cache_payload", 'w')
#        cPickle.dump(self.domain_emiss, cache_file)
#        cache_file.close()
        
        print "debug: Emission interpolation end"
        print "------------------------------"
    
    def save_emission(self):
        print "debug: Emission save start"
        self.progress("Saving Result")
        #TODO: debug
#        print "debug: Reading cache"
#        print os.getcwd()
#        cache_file = open("cache_payload", 'r')
#        self.domain_emiss = cPickle.load(cache_file)
#        cache_file.close()
        
        for n in range(self.maxdom):
            domain = self.domains[n]
            filename_1 = opj("{0}/wrfchemi_00z_d{1:0>2}".format(self.save_dir, n+1))
            filename_2 = opj("{0}/wrfchemi_12z_d{1:0>2}".format(self.save_dir, n+1))
            
            #file1
            cdf_file = pupynere.netcdf_file(filename_1, 'w')
            cdf_file.createDimension('Time', 12)
            cdf_file.createDimension('south_north', domain.h)
            cdf_file.createDimension('emissions_zdim', 2)
            cdf_file.createDimension('DateStrLen', 19)
            cdf_file.createDimension('west_east', domain.w)
        
            cdf_vars = {}
            for plt in self.pollutant_list:
                cdf_vars[plt] = cdf_file.createVariable(plt, 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east'))
                cdf_vars[plt].units = 'mol km^-2 hr^-1'
            for plt in self.additional_pollutan_list:
                cdf_vars[plt] = cdf_file.createVariable(plt, 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east'))
                cdf_vars[plt].units = 'mol km^-2 hr^-1'
            cdf_vars['times'] = cdf_file.createVariable('Times', 'c', ('Time', 'DateStrLen'))

            for i in range(12): #time
                for j in range(1): #z level
                    for y in range(domain.h):
                        for x in range(domain.w):
                            for p, plt in enumerate(self.pollutant_str):
                                cdf_vars[plt][i][j][y][x] = self.domain_emiss[n][y][x][p] 
    
            cdf_file.close()
            
            #file2
            cdf_file = pupynere.netcdf_file(filename_2, 'w')
            cdf_file.createDimension('Time', 12)
            cdf_file.createDimension('south_north', domain.h)
            cdf_file.createDimension('emissions_zdim', 2)
            cdf_file.createDimension('DateStrLen', 19)
            cdf_file.createDimension('west_east', domain.w)
        
            cdf_vars = {}
            for plt in self.pollutant_list:
                cdf_vars[plt] = cdf_file.createVariable(plt, 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east'))
                cdf_vars[plt].units = 'mol km^-2 hr^-1'
            for plt in self.additional_pollutan_list:
                cdf_vars[plt] = cdf_file.createVariable(plt, 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east'))
                cdf_vars[plt].units = 'mol km^-2 hr^-1'
            cdf_vars['times'] = cdf_file.createVariable('Times', 'c', ('Time', 'DateStrLen'))

            for i in range(12): #time
                for j in range(1): #z level
                    for y in range(domain.h):
                        for x in range(domain.w):
                            for p, plt in enumerate(self.pollutant_str):
                                cdf_vars[plt][i][j][y][x] = self.domain_emiss[n][y][x][p] 
    
            cdf_file.close()
            
        print "debug: Emission save end"
        print "------------------------------"
    
    def run(self):
        self.load_namelist()
        if self.abort:
            print "Aborting..."
            self.done()
            return
        self.process_pollutant_list()
        if self.abort:
            print "Aborting..."
            self.done()
            return
        self.load_worksheet_data()
        if self.abort:
            print "Aborting..."
            self.done()
            return
        self.create_emission_group()
        if self.abort:
            print "Aborting..."
            self.done()
            return
        self.compute_emission()
        if self.abort:
            print "Aborting..."
            self.done()
            return
        self.save_emission()
        self.done()
        
    def run_old(self):
        import  time
        
        for i in range(100):
            time.sleep(0.1)
            self.progress("Tick: {0}".format(i))
            print 'tick', i
            if self.abort:
                print "Aborting..."
                break
        
        self.done()
        
        

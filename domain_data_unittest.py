
"""
unittest untuk domain_data
"""

import unittest
import domain_data
import namelist_reader

class DomainTest(unittest.TestCase):
    def setUp(self):
        path = 'res/namelist.wps'
        self.wpsreader = namelist_reader.WPSNamelistReader(path)
        
    def test_create_domain(self):
        tdm = domain_data.TopDomain()
        tdm.lat = self.wpsreader.ref_lat
        tdm.lon = self.wpsreader.ref_lon
        tdm.w   = self.wpsreader.e_we[0] - 1
        tdm.h   = self.wpsreader.e_sn[0] - 1
        tdm.dx  = self.wpsreader.dom_dx
        tdm.dy  = self.wpsreader.dom_dy
        tdm.process_boundary()
        
        cdm = domain_data.SubDomain(tdm, self.wpsreader.i_parent_start[1], 
                                    self.wpsreader.j_parent_start[1], self.wpsreader.parent_grid_ratio[1])
        cdm.w   = self.wpsreader.e_we[1] - 1
        cdm.h   = self.wpsreader.e_sn[1] - 1
        cdm.process_boundary()
        
        ccdm = domain_data.SubDomain(cdm, self.wpsreader.i_parent_start[2], 
                                    self.wpsreader.j_parent_start[2], self.wpsreader.parent_grid_ratio[2])
        ccdm.w   = self.wpsreader.e_we[2] - 1
        ccdm.h   = self.wpsreader.e_sn[2] - 1
        ccdm.process_boundary()
        
        print tdm.get_cell_boundary_latlon(0, 0)
        print cdm.get_cell_boundary_latlon(0, 0)
        print ccdm.get_cell_boundary_latlon(0, 0)
        for x in range(tdm.w):
            for y in range(tdm.h):
                print x, y, tdm.get_cell_boundary_latlon(x, y)
        print (tdm.tr_lat, tdm.tr_lon) 
          
        for x in range(cdm.w):
            for y in range(cdm.h):
                print x, y, cdm.get_cell_boundary_latlon(x, y)
        print (cdm.tr_lat, cdm.tr_lon)
           
        for x in range(ccdm.w):
            for y in range(ccdm.h):
                print x, y, ccdm.get_cell_boundary_latlon(x, y)
        print (ccdm.tr_lat, ccdm.tr_lon)        
        
    
if __name__ == "__main__":
    unittest.main()
    
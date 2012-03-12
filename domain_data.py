
"""
Berisi class-class untuk mengatur domain

penggunaan:
- buat object TopDomain (misal tdm = TopDomain() ) 
  isi nilai lat, lon, w, h, dan dx dy lalu panggil tdm.process_boundary() 
- buat object SubDomain (misal cdm = SubDomain(tdm, 20, 20, 3) )
  isi nilai w dan h, lalu panggil cdm.process_boundary()
- SubDomain dapat memiliki parent berupa TopDomain atau SubDomain lain (nesting)

-- gunakan cdm.get_cell_boundary_latlon(25,25) untuk mendapatkan koordinat
   pojok kiri bawah dan pojok kanan atas sel(25,25) dalam latlon

TODO: get_cell_boundary_utm harus dimodif agar dapat menerima parameter zone dan hem
_________________
Arif Widi Nugroho
arif@hexarius.com
"""

import utm

class Domain():
    def __init__(self):
        self.w    = None # ukuran sel arah horizontal (mis: 90 --> e_we - 1)
        self.h    = None # ukuran sel arah vertikal (mis: 90 --> e_sn - 1)
        self.dx   = None # delta x (meter)
        self.dy   = None
        self.lat  = None
        self.lon  = None
        self.x    = None # easting
        self.y    = None # northing
        self.zone = None
        self.hem  = None
        
        self.ll_lat = None # latitude pojok kiri bawah (lower left)
        self.ll_lon = None # longitude pojok kiri bawah
        self.tr_lat = None # latitude pojok kanan atas (top right)
        self.tr_lon = None # longitude pojok kanan atas
        
        self.ll_x = None # easting pojok kiri bawah
        self.ll_y = None # northing pojok kiri bawag
        self.tr_x = None # pojok kanan atas
        self.tr_y = None
        
        self.processed_to_utm = False
        
    def process_to_utm(self, force=False):
        """ 
        Memproses lat/lon menjadi x, y, zone & hem
        Harus dipanggil sebelum menggunakan fungsi-fungsi yang ada dalam subclass
        """
        if (force == False) and self.processed_to_utm:
            return False
        flag = False
        try:
            self.zone, self.hem = utm.get_zone_hem(self.lat, self.lon)
            self.x, self.y      = utm.convert_to_utm(self.lat, self.lon)
            flag                = True
            self.processed_to_utm = True
        except Exception as ex:
            print 'Exception: process_to_utm -->', ex
        return flag
        
class TopDomain(Domain):
    def __init__(self):
        Domain.__init__(self)
    
    def process_boundary(self):
        self.process_to_utm()
        dx = (self.w / 2) * self.dx
        dy = (self.h / 2) * self.dy
        
        ll_x = self.x - dx
        ll_y = self.y - dy
        tr_x = self.x + dx
        tr_y = self.y + dy
        
        self.ll_x = ll_x
        self.ll_y = ll_y
        self.tr_x = tr_x
        self.tr_y = tr_y
        
        self.ll_lat, self.ll_lon = utm.convert_to_latlon(ll_x, ll_y, self.zone, self.hem)
        self.tr_lat, self.tr_lon = utm.convert_to_latlon(tr_x, tr_y, self.zone, self.hem)
    
    def get_cell_boundary_latlon(self, x, y):
        #posisi sel dimulai dari 0
        dx = ((self.w / 2) - x ) * self.dx
        dy = ((self.h / 2) - y ) * self.dy
        
        ll_x = self.x - dx
        ll_y = self.y - dy
        tr_x = self.x - dx + self.dx
        tr_y = self.y - dy + self.dy
        
        ll = utm.convert_to_latlon(ll_x, ll_y, self.zone, self.hem)
        tr = utm.convert_to_latlon(tr_x, tr_y, self.zone, self.hem)
        #[ [lat, lon], [lat, lon] ]
        return ll, tr
    
    def get_cell_boundary_utm(self, x, y, zone=None, hem=None):
        if zone==None:
            zone = self.zone
        if hem==None:
            hem = self.hem
        ll, tr = self.get_cell_boundary_latlon(x, y)
        utm_ll = utm.convert_to_utm_fixzone(ll[0], ll[1], zone, hem)
        utm_tr = utm.convert_to_utm_fixzone(tr[0], tr[1], zone, hem)
        return utm_ll, utm_tr
    
    def get_cell_boundary_utm_old(self, x, y):
        #posisi sel dimulai dari 0
        dx = ((self.w / 2) - x ) * self.dx
        dy = ((self.h / 2) - y ) * self.dy
        
        ll_x = self.x - dx
        ll_y = self.y - dy
        tr_x = self.x - dx + self.dx
        tr_y = self.y - dy + self.dy
        # [ [x, y], [x, y] ]
        return (ll_x, ll_y), (tr_x, tr_y)
    
class SubDomain(Domain):
    def __init__(self, parent, parent_start_x, parent_start_y, ratio):
        Domain.__init__(self)
        self.ratio   = ratio # grid ratio
        self.parent_start_x   = parent_start_x # starting grid relatif terhadap domain induk
        self.parent_start_y   = parent_start_y
        self.processed_to_utm = True
        self.parent = parent
        try:
            self.init()
        except Exception as ex:
            print "Subdomain initialization error: ", ex
        
    def init(self):
        #menentukan boundary subdomain dari data domain induk
        bnd = self.parent.get_cell_boundary_utm(self.parent_start_x, self.parent_start_y)
        self.ll_x = bnd[0][0]
        self.ll_y = bnd[0][1]
        bnd = self.parent.get_cell_boundary_latlon(self.parent_start_x, self.parent_start_y)
        self.ll_lat = bnd[0][0]
        self.ll_lon = bnd[0][1]
        self.zone = self.parent.zone
        self.hem = self.parent.hem
        self.dx = self.parent.dx / self.ratio
        self.dy = self.parent.dy / self.ratio
        
    def process_boundary(self):
        #menentukan boundary subdomain dari data domain induk
        dx = self.w * self.dx
        dy = self.h * self.dy
        
        self.tr_x = self.ll_x + dx
        self.tr_y = self.ll_y + dy
        
        self.tr_lat, self.tr_lon = utm.convert_to_latlon(self.tr_x, self.tr_y, self.zone, self.hem)
        
        #titik tengah domain
        self.x = self.ll_x + self.dx * (self.w / 2)
        self.y = self.ll_y + self.dy * (self.h / 2)
        self.lat, self.lon = utm.convert_to_latlon(self.x, self.y, self.zone, self.hem)
        
    def get_cell_boundary_latlon(self, x, y):
        #posisi sel dimulai dari 0
        dx = x * self.dx
        dy = y * self.dy
        
        ll_x = self.ll_x + dx
        ll_y = self.ll_y + dy
        tr_x = self.ll_x + dx + self.dx
        tr_y = self.ll_y + dy + self.dy
        
        ll = utm.convert_to_latlon(ll_x, ll_y, self.zone, self.hem)
        tr = utm.convert_to_latlon(tr_x, tr_y, self.zone, self.hem)
        #[ [lat, lon], [lat, lon] ]
        return ll, tr
    
    def get_cell_boundary_utm(self, x, y, zone=None, hem=None):
        if zone==None:
            zone = self.zone
        if hem==None:
            hem = self.hem
        ll, tr = self.get_cell_boundary_latlon(x, y)
        utm_ll = utm.convert_to_utm_fixzone(ll[0], ll[1], zone, hem)
        utm_tr = utm.convert_to_utm_fixzone(tr[0], tr[1], zone, hem)
        return utm_ll, utm_tr
    
    def get_cell_boundary_utm_old(self, x, y):
        #posisi sel dimulai dari 0
        dx = x * self.dx
        dy = y * self.dy
        
        ll_x = self.ll_x + dx
        ll_y = self.ll_y + dy
        tr_x = self.ll_x + dx + self.dx
        tr_y = self.ll_y + dy + self.dy
        
        ll = (ll_x, ll_y)
        tr = (tr_x, tr_y)
        #[ [x, y], [x, y] ]
        return ll, tr
        
if __name__ == '__main__':
    dm = TopDomain()
    dm.lat = -7.0
    dm.lon = 107.0
    dm.h = 90
    dm.w = 90
    dm.dx = 9000
    dm.dy = 9000
    
#    dm.process_to_utm()
    dm.process_boundary()
    print dm.ll_lat, dm.ll_lon
    print dm.tr_lat, dm.tr_lon
#    print dm.get_cell_boundary_utm(20, 20)
    print dm.get_cell_boundary_latlon(89, 89)
    print dm.dx, dm.dy
    print '-----------------------'
    
    cdm = SubDomain(dm, 0, 0, 3)
    cdm.w = 90
    cdm.h = 90
    cdm.process_boundary()
#    print cdm.ll_x, cdm.ll_y, cdm.tr_x, cdm.tr_y
    print cdm.ll_lat, cdm.ll_lon, cdm.tr_lat, cdm.tr_lon
#    print cdm.x, cdm.y, cdm.lat, cdm.lon
    
    print cdm.get_cell_boundary_utm(89,89)
    print cdm.dx, cdm.dy
    print '-----------------------'
    
    ccdm = SubDomain(cdm, 0, 0, 3)
    ccdm.w = 90
    ccdm.h = 90
    ccdm.process_boundary()
#    print cdm.ll_x, cdm.ll_y, cdm.tr_x, cdm.tr_y
    print ccdm.ll_lat, ccdm.ll_lon, ccdm.tr_lat, ccdm.tr_lon
#    print cdm.x, cdm.y, cdm.lat, cdm.lon
    
    print ccdm.get_cell_boundary_utm(89,89)
    print ccdm.dx, ccdm.dy
    print '-----------------------'
    
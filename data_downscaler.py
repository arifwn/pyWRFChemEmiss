
"""
Berisi Class dan fungsi untuk memanipulasi data emisi

Penggunaan:
- buat object EmissGroup, ini merupakan grup untuk masing2 kelompok emisi
- tentukan dimensi EmissGroup dengan fungsi set_dimension()
- buat object EmissData(), isi dengan data konsentrasi dan posisi sel
- tambahkan object EmissData ke dalam EmissGroup melalui append_data()
- setelah semua data ditambahkan, panggil compute_boundary() 
   
-- untuk mendapatkan sel individual gunakan get_data(x, y)
-- untuk mendapatkan boundary sel gunakan get_data_boundary_latlon(x, y) dan _utm

TODO: Buat rutin downscalernya
_________________
Arif Widi Nugroho
arif@hexarius.com
"""

import utm

RDD = 6

class RowData():
    def __init__(self, lat, lon, x, y, data):
        self.lat  = lat
        self.lon  = lon
        self.x    = x
        self.y    = y
        self.data = data

def compare_rowdata(a, b):
    if (a.lon == b.lon) and (a.lat == b.lat):
        return 0
    if (a.lat < b.lat):
        return -1
    if (a.lat == b.lat) and (a.lon < b.lon):
        return -1
    return 1

def compare_rowdata_m(a, b):
    if (a.x == b.x) and (a.y == b.y):
        return 0
    if (a.y < b.y):
        return -1
    if (a.y == b.y) and (a.x < b.x):
        return -1
    return 1


class EmissData():
    """ data suatu sel disimpan sebagai object dari class ini"""
    def __init__(self):
        self.lat  = None
        self.lon  = None
        self.x    = None
        self.y    = None
        self.conc = None

#misc function

def point_is_inside(point, ll, tr):
    if (point[0] >= ll[0]) and (point[0] <= tr[0]) and (point[1] >= ll[1]) and (point[1] <= tr[1]):
        return True
    else:
        return False

def is_intersect(ll_a, tr_a, ll_b, tr_b, get_type=False):
    """return True bila A dan B berpotongan """
    inter = False
    t = 0
    if (ll_a[0]==ll_b[0]) and (ll_a[1]==ll_b[1]) and (tr_a[0]==tr_b[0]) and (tr_a[1]==tr_b[1]):
        if get_type:
            return True, 2
        else:
            return True
    
    point   = [False, False, False, False, False, False, False, False]
    n_point = 0
    
    #1. cek apakah garis bawah kotak a berpotongan dengan garis vertikal kiri
    #kotak b
    if (ll_b[0] >= ll_a[0]) and (ll_b[0] <= tr_a[0]) and (ll_a[1] >= ll_b[1]) and (ll_a[1] <= tr_b[1]):
        point[0] = True
        n_point = n_point + 1
    
    #2. cek apakah garis bawah kotak a berpotongan dengan garis vertikal kanan
    #kotak b
    if (tr_b[0] >= ll_a[0]) and (tr_b[0] <= tr_a[0]) and (ll_a[1] >= ll_b[1]) and (ll_a[1] <= tr_b[1]):
        point[1] = True
        n_point = n_point + 1
    
    #3. cek apakah garis atas kotak a berpotongan dengan garis vertikal kiri
    #kotak b
    if (ll_b[0] >= ll_a[0]) and (ll_b[0] <= tr_a[0]) and (tr_a[1] >= ll_b[1]) and (tr_a[1] <= tr_b[1]):
        point[2] = True
        n_point = n_point + 1
    
    #4 .cek apakah garis atas kotak a berpotongan dengan garis vertikal kanan
    #kotak b
    if (tr_b[0] >= ll_a[0]) and (tr_b[0] <= tr_a[0]) and (tr_a[1] >= ll_b[1]) and (tr_a[1] <= tr_b[1]):
        point[3] = True
        n_point = n_point + 1
    
    #5. cek apakah garis vertikal kiri kotak a berpotongan dengan garis bawah
    #kotak b
    if (ll_b[1] >= ll_a[1]) and (ll_b[1] <= tr_a[1]) and (ll_a[0] >= ll_b[0]) and (ll_a[0] <= tr_b[0]):
        point[4] = True
        n_point = n_point + 1
    
    #6. cek apakah garis vertikal kiri kotak a berpotongan dengan garis atas
    #kotak b
    if (tr_b[1] >= ll_a[1]) and (tr_b[1] <= tr_a[1]) and (ll_a[0] >= ll_b[0]) and (ll_a[0] <= tr_b[0]):
        point[5] = True
        n_point = n_point + 1
    
    #7. cek apakah garis vertikal kanan kotak a berpotongan dengan garis bawah
    #kotak b
    if (ll_b[1] >= ll_a[1]) and (ll_b[1] <= tr_a[1]) and (tr_a[0] >= ll_b[0]) and (tr_a[0] <= tr_b[0]):
        point[6] = True
        n_point = n_point + 1
    
    #8. cek apakah garis vertikal kanan kotak a berpotongan dengan garis atas
    #kotak b
    if (tr_b[1] >= ll_a[1]) and (tr_b[1] <= tr_a[1]) and (tr_a[0] >= ll_b[0]) and (tr_a[0] <= tr_b[0]):
        point[7] = True
        n_point = n_point + 1
    
#    print n_point, point
    
    if n_point == 0 :
        if (point_is_inside(ll_a, ll_b, tr_b) or point_is_inside(ll_b, ll_a, tr_a) ):
            #tipe 2: n_point=0, berpotongan
#            print "type 2"
            t = 2
            inter = True
        else:
            #tipe 1: n_point=0, tidak berpotongan
#            print "type 1"
            t = 1
            inter = False
    
    # tipe 3 & 4
    elif n_point == 2:
#        print "type 3 or 4"
        #    pojok kanan atas           pojok kiri atas            pojok kanan bawah           pojok kiri bawah
        if (point[2] and point[6]) or (point[3] and point[4]) or (point[0] and point[7]) or (point[1] and point[5]):
#            print "type 3"
            t = 3
            inter = True
        elif (point[0] and point[1]) or (point[2] and point[3]) or (point[4] and point[5]) or (point[6] and point[7]) or \
        (point[0] and point[2]) or (point[1] and point[3]) or (point[4] and point[6]) or (point[5] and point[7]):
#            print "type 4 / tipe 2"
            if point_is_inside(ll_a, ll_b, tr_b) and point_is_inside(tr_a, ll_b, tr_b) or \
            point_is_inside(ll_b, ll_a, tr_a) and point_is_inside(ll_b, ll_a, tr_a):
                t = 2
            else:
                t = 4
            inter = True
    
    # tipe 5
    elif n_point == 4:
        if point_is_inside(ll_a, ll_b, tr_b) and point_is_inside(tr_a, ll_b, tr_b) or \
        point_is_inside(ll_b, ll_a, tr_a) and point_is_inside(ll_b, ll_a, tr_a):
#            print "type 2"
            t = 2
            inter = True
        else:
#            print "type 5"
            t = 5
            inter = True
    elif n_point > 4:
#        print "type 2"
        t = 2
        inter = True
    else:
#        print "no intersection"
        inter = False
    
    if get_type:
        return inter, t
    else:
        return inter

def intersect(ll_a, tr_a, ll_b, tr_b, area_size=None):
    """mengembalikan luas area potongan antara kotak a dan b,
    return 0 bila tidak berpotongan
    ll dan tr: tuple (x, y)"""
    
    size_a = (tr_a[0] - ll_a[0]), (tr_a[1] - ll_a[1])
    size_b = (tr_b[0] - ll_b[0]), (tr_b[1] - ll_b[1])
    area_a = round( size_a[0] * size_a[1], RDD)
    area_b = round( size_b[0] * size_b[1], RDD)
    corner_a = ll_a, (tr_a[0], ll_a[1]), (ll_a[0], tr_a[1]), tr_a
    corner_b = ll_b, (tr_b[0], ll_b[1]), (ll_b[0], tr_b[1]), tr_b
    inter, t = is_intersect(ll_a, tr_a, ll_b, tr_b, True)
#    print inter, t
#    print corner_a, corner_b
    
#    print size_a
    
    if t == 1:
        return 0.0
    elif t == 2:
#        print 'a b: ', (area_a, area_b)
        if area_size != None:
            return area_size
        elif area_a < area_b:
            return area_a
        else:
            return area_b
    elif t == 3:
        cr_1 = (0, 0)
        cr_2 = (0, 0)
        for point in corner_a:
            if point_is_inside(point, ll_b, tr_b): 
                cr_1 = point
        for point in corner_b:
            if point_is_inside(point, ll_a, tr_a): 
                cr_2 = point
        area = (cr_1[0] - cr_2[0]) * (cr_1[1] - cr_2[1])
#        print cr_1, cr_2, area
        return round(area, RDD)
    elif t == 4:
    #TODO: masih ada bugnya!!!!!
        cr = []
        cr_ = []
        is_a = False
        for point in corner_a:
            if point_is_inside(point, ll_b, tr_b): 
                cr.append(point)
        if len(cr)==2:
            is_a = True
        for point in corner_b:
            if point_is_inside(point, ll_a, tr_a): 
                cr_.append(point)
        if len(cr_)==2:
            is_a = False
            cr = cr_
            
        is_x = False #True: x sama
#        print ll_a, tr_a, ll_b, tr_b
        if cr[0][0] == cr[1][0]:
            is_x = True
        
        if is_a:
#            print "a in b"
#            print cr
            if is_x:
                len_1 = abs(cr[0][1] - cr[1][1])
                len_2 = 0
                if (ll_b[0] >= ll_a[0]) and (ll_b[0] <= tr_a[0]):
                    len_2 = abs(tr_a[0] - ll_b[0])
                elif (tr_b[0] >= ll_a[0]) and (tr_b[0] <= tr_a[0]):
                    len_2 = abs(tr_b[0] - ll_a[0])
#                print len_1, len_2
                return round( len_1 * len_2, RDD)
            else:
                len_1 = abs(cr[0][0] - cr[1][0])
                len_2 = 0
                if (ll_b[1] >= ll_a[1]) and (ll_b[1] <= tr_a[1]):
                    len_2 = abs(tr_a[1] - ll_b[1])
                elif (tr_b[1] >= ll_a[1]) and (tr_b[1] <= tr_a[1]):
                    len_2 = abs(tr_b[1] - ll_a[1])
#                print len_1, len_2
                return round( len_1 * len_2, RDD)
        else:
#            print "b in a"
#            print cr
            if is_x:
                len_1 = abs(cr[0][1] - cr[1][1])
                len_2 = 0
                if (ll_a[0] >= ll_b[0]) and (ll_a[0] <= tr_b[0]):
                    len_2 = abs(tr_b[0] - ll_a[0])
                elif (tr_a[0] >= ll_b[0]) and (tr_a[0] <= tr_b[0]):
                    len_2 = abs(tr_a[0] - ll_b[0])
#                print len_1, len_2
                return round( len_1 * len_2, RDD)
            else:
                len_1 = abs(cr[0][0] - cr[1][0])
                len_2 = 0
                if (ll_a[1] >= ll_b[1]) and (ll_a[1] <= tr_b[1]):
                    len_2 = abs(tr_b[1] - ll_a[1])
                elif (tr_a[1] >= ll_b[1]) and (tr_a[1] <= tr_b[1]):
                    len_2 = abs(tr_a[1] - ll_b[1])
#                print len_1, len_2
                return round( len_1 * len_2, RDD)
        
    elif t == 5:
        llc_a = ll_a
        trc_a = tr_a
        llc_b = ll_b
        trc_b = tr_b
        if llc_a[0] < llc_b[0]:
            #tukar
            llc_a = ll_b
            trc_a = tr_b
            llc_b = ll_a
            trc_b = tr_a
        
        #pojok kiri bawah
        cr1 = llc_a[0], llc_b[1]
        #pojok kanan bawah
        cr2 = trc_a[0], llc_b[1]
        #pojok kiri atas
        cr3 = llc_a[0], trc_b[1]
        #pojok kanan atas
        cr4 = trc_a[0], trc_b[1]
        len1 = cr2[0] - cr1[0]
        len2 = cr3[1] - cr1[1]
        
#        print cr1, cr2, cr3, cr4
#        print len1, len2
        
        return round( len_1 * len_2, RDD)
    else:
#        print "type:", t, inter
        return 0.0
    
    

class EmissGroup():
    def __init__(self):
        self.data = []
        self.x_counter = 0
        self.y_counter = -1
        self.n_counter = 0
        self.dx        = 0.0 #ukuran sel
        self.dy        = 0.0 #ukuran sel
        self.dx_deg    = 0.0 #ukuran sel dalam derajat 
        self.dy_deg    = 0.0 #ukuran s
        
        self.ll_lat = 0.0
        self.ll_lon = 0.0
        self.ll_x   = 0.0
        self.ll_y   = 0.0
        self.tr_lat = 0.0
        self.tr_lon = 0.0
        self.tr_x   = 0.0
        self.tr_y   = 0.0
        
        self.lat  = 0.0 #middle coordinate
        self.lon  = 0.0
        self.zone = 0 # utm zone untuk sel di tengah2 grup
        self.hem  = 0
        
        self.cell_area = 0.0 #luas area sel (m^2)
        
        # field berikut otomatis diupdate saat memasukkan data
        self.min_conc = 0.0
        self.max_conc = 0.0
        self.avg_conc = 0.0 #konsentrasi rata-rata
        
        self.default_conc = 0.0
        self.conv_factor  = 1.0 #conversion factor
        
    def set_dimension(self, width, height):
        self.w = width
        self.h = height
    
    def compute_dx(self):
        """menghitung dx dan dy (m) dari data yang sudah dimasukkan"""
        if (self.w < 1) or (self.h < 1):
            print "Error, insufficient data"
            return False
        
        flag_dx = False
        flag_dy = False
        dx = 0
        dy = 0
        
        if self.w < 2:
            print "WARNING: cannot compute dx"
        else:
            flag_dx = True
        if self.h < 2:
            print "WARNING: cannot compute dy"
        else:
            flag_dy = True
        
        if (flag_dx == False) and (flag_dy == False):
            print "Cannot compute compute dx and dy!"
            return False
        
        if flag_dx:
            #hitung dx
            max = self.w - 2
            base_x = self.data[0][0].x
            prev = base_x
            total_x = 0.0
            n = 0
            for i, data in enumerate(self.data[0]):
                n = n + 1
                total_x = total_x + (data.x - prev)
                prev = data.x
                if i == max:
                    break
            dx = float(total_x) / float(max) 
            self.dx = dx
            
        if flag_dy:
            #hitung dx
            max = self.h - 2
            base_y = self.data[0][0].y
            prev = base_y
            total_y = 0.0
            n = 0
            for i, col in enumerate(self.data):
                data = col[0]
                n = n + 1
                total_y = total_y + (data.y - prev)
                prev = data.y
                if i == max:
                    break
            dy = float(total_y) / float(max) 
            self.dy = dy
        
        if flag_dx == False:
            print "Assuming dx == dy"
            self.dx = dy
            
        if flag_dy == False:
            print "Assuming dy == dx"
            self.dy = dx
        
    def compute_dx_deg(self):
        """menghitung dx_deg dan dy_deg (derajat) dari data yang sudah dimasukkan"""
        if (self.w < 1) or (self.h < 1):
            print "Error, insufficient data"
            return False
        
        flag_dx = False
        flag_dy = False
        dx = 0
        dy = 0
        
        if self.w < 2:
            print "WARNING: cannot compute dx_deg"
        else:
            flag_dx = True
        if self.h < 2:
            print "WARNING: cannot compute dy_deg"
        else:
            flag_dy = True
        
        if (flag_dx == False) and (flag_dy == False):
            print "Cannot compute compute dx_deg and dy_deg!"
            return False
        
        if flag_dx:
            #hitung dx
            max = self.w - 2
            base_x = self.data[0][0].lon
            prev = base_x
            total_x = 0.0
            n = 0
            for i, data in enumerate(self.data[0]):
                n = n + 1
                total_x = total_x + (data.lon - prev)
                prev = data.lon
                if i == max:
                    break
            dx = float(total_x) / float(max) 
            self.dx_deg = dx
        if flag_dy:
            #hitung dx
            max = self.h - 2
            base_y = self.data[0][0].lat
            prev = base_y
            total_y = 0.0
            n = 0
            for i, col in enumerate(self.data):
                data = col[0]
                n = n + 1
                total_y = total_y + (data.lat - prev)
                prev = data.lat
                if i == max:
                    break
            dy = float(total_y) / float(max)  
            self.dy_deg = dy
        
        if flag_dx == False:
            print "Assuming dx_deg == dy_deg"
            self.dx_deg = dy
            
        if flag_dy == False:
            print "Assuming dy_deg == dx_deg"
            self.dy_deg = dx
            
    def append_data(self, data):
        self.n_counter = self.n_counter + 1
        if self.x_counter == 0:
            self.data.append([])
            self.y_counter = self.y_counter + 1
            if self.y_counter == 0:
                self.max_conc = data.conc
                self.min_conc = data.conc
        self.data[self.y_counter].append(data)
        self.x_counter = self.x_counter + 1
        if self.x_counter == self.w:
            self.x_counter = 0
        #min/max conc
        if self.max_conc < data.conc:
            self.max_conc = data.conc
        if self.min_conc > data.conc:
            self.min_conc = data.conc
        self.avg_conc = (self.avg_conc * float(self.n_counter - 1) + data.conc) / float(self.n_counter) 
    
    def set_data(self, x, y, data):
        fl = False
        try:
            self.data[y][x] = data
            fl = True
        except Exception as e:
            print e
        return fl
    
    def get_data(self, x, y):
        return self.data[y][x]    
    
    def get_data_boundary_utm(self, x, y, zone=None, hem=None):
        """ 
        mengembalikan koordinat pojok kiri bawah dan kanan atas data(x, y)
        dalam meter (utm)"""

        if (zone==None) or (hem==None):
            zone = self.zone
            hem = self.hem
            
        bnd = self.return_boundary_utm_nosave(zone, hem)
        ll_x = bnd[0] + (x * self.dx)
        ll_y = bnd[1] + (y * self.dy)
        tr_x = ll_x + self.dx 
        tr_y = ll_y + self.dy
#        print round((tr_x - ll_x), RDD) == self.dx
#        tr_x = bnd[0] + ((x + 1) * self.dx)
#        tr_y = bnd[1] + ((y + 1) * self.dy)
        
        return (ll_x, ll_y), (tr_x, tr_y)
        
    def get_data_boundary_latlon(self, x, y, flip=False):
        """mengembalikan koordinat pojok kiri bawah dan kanan atas data(x, y)
           dalam derajat"""
        data   = self.data[y][x]
        ll_lat = data.lat
        ll_lon = data.lon
        tr_lat = ll_lat + self.dy_deg
        tr_lon = ll_lon + self.dx_deg
        
        if flip:
            return (ll_lon, ll_lat), (tr_lon, tr_lat)
        else:
            return (ll_lat, ll_lon), (tr_lat, tr_lon)
    
    def get_average_conc(self):
        """
        menghitung rata-rata konsentrasi.
        lebih akurat dibandingkan self.avg_conc
        """
        total = 0.0
        for row in self.data:
            for cell in row:
                total = total + cell.conc
        
        return (total / float(self.n_counter)) * self.conv_factor
    
    def compute_boundary(self):
        """menghitung boundary latlon dan utm, cukup dipanggil sekali saja"""
        self.compute_boundary_latlon()
        self.compute_middle_latlon()
        self.compute_boundary_utm(self.zone, self.hem)
        self.cell_area = round( self.dx * self.dy , RDD)
    
    def return_boundary_utm_nosave(self, zone, hem):
        """menghitung koordinat pojok kiri bawah dan pojok kanan atas seluruh data"""
        ll_data = self.data[0][0]
        tr_data = self.data[self.h - 1][self.w - 1]
        ll_x, ll_y = utm.convert_to_utm_fixzone(ll_data.lat, ll_data.lon, zone, hem)
        tr_x, tr_y = utm.convert_to_utm_fixzone(tr_data.lat, tr_data.lon, zone, hem)
        tr_x = tr_x + self.dx
        tr_y = tr_y + self.dy
        
        return (ll_x, ll_y, tr_x, tr_y)
    
    def compute_boundary_utm(self, zone, hem):
        """menghitung koordinat pojok kiri bawah dan pojok kanan atas seluruh data"""
        self.compute_dx()
        bnd = self.return_boundary_utm_nosave(zone, hem)
        self.ll_x = bnd[0]
        self.ll_y = bnd[1]
        self.tr_x = bnd[2]
        self.tr_y = bnd[3]
        
    def return_boundary_latlon_nosave(self):
        """menghitung koordinat pojok kiri bawah dan pojok kanan atas seluruh data"""

        ll_data = self.data[0][0]
        tr_data = self.data[self.h - 1][self.w - 1]
        ll_lat  = ll_data.lat
        ll_lon  = ll_data.lon
        tr_lat  = tr_data.lat + self.dy_deg
        tr_lon  = tr_data.lon + self.dx_deg
        
        return (ll_lat, ll_lon, tr_lat, tr_lon)
        
    def compute_boundary_latlon(self):
        """menghitung koordinat pojok kiri bawah dan pojok kanan atas seluruh data"""
        self.compute_dx_deg()
        bnd = self.return_boundary_latlon_nosave()
        self.ll_lat  = bnd[0]
        self.ll_lon  = bnd[1]
        self.tr_lat  = bnd[2]
        self.tr_lon  = bnd[3]
    
    def compute_middle_latlon(self):
        """menghitung koordinat di tengah2 grup emisi"""
        self.lat = (self.ll_lat + self.tr_lat) / 2
        self.lon = (self.ll_lon + self.tr_lon) / 2
        self.zone, self.hem = utm.get_zone_hem(self.lat, self.lon)
    
    def get_average_conc_latlon_internal_degree(self, ll, tr):
        """
        mengembalikan konsentrasi pencemar rata2 dalam suatu area
        ll=(lat, lon)
        tr=(lat, lon)
        """
        ll_g = self.ll_lon, self.ll_lat
        tr_g = self.tr_lon, self.tr_lat
        ll_a = ll[1], ll[0]
        tr_a = tr[1], tr[0]
        
        if is_intersect(ll_a, tr_a, ll_g, tr_g, True) == False:
            #area tidak berpotongan
            return self.default_conc
        
        total_c    = 0
        total_area = 0
#        print '---------'
#        ll_cell, tr_cell = self.get_data_boundary_latlon(22, 49, True)
#        area = intersect(ll_a, tr_a, ll_cell, tr_cell)
#        print '---------'
        for y, row in enumerate(self.data):
            for x, cell in enumerate(row):
                ll_cell, tr_cell = self.get_data_boundary_latlon(x, y, True)
                try:
                    area = intersect(ll_a, tr_a, ll_cell, tr_cell)
                except:
                    print "error", x, y, ll_a, tr_a, ll_cell, tr_cell
                    print "--> ", is_intersect(ll_a, tr_a, ll_cell, tr_cell, True)
                if area == None:
                    print "none", x, y, ll_a, tr_a, ll_cell, tr_cell
#                elif area > 0:
#                    print x, y, cell.conc, area
                total_area = total_area + area
                total_c = total_c + (cell.conc * area)
        
        if total_area > 0:
            avg_c = total_c / total_area
#        print total_area, avg_c
        return avg_c * self.conv_factor
    
    def get_average_conc_latlon(self, ll, tr):
        """
        mengembalikan konsentrasi pencemar rata2 dalam suatu area
        ll=(lat, lon)
        tr=(lat, lon)
        """
        ll_g = self.ll_lon, self.ll_lat
        tr_g = self.tr_lon, self.tr_lat
        ll_a = ll[1], ll[0]
        tr_a = tr[1], tr[0]
        
        if is_intersect(ll_a, tr_a, ll_g, tr_g) == False:
            #area tidak berpotongan
            return self.default_conc

        ll_a_utm = utm.convert_to_utm_fixzone(ll[0], ll[1], self.zone, self.hem)
        tr_a_utm = utm.convert_to_utm_fixzone(tr[0], tr[1], self.zone, self.hem)
        area_a = (tr_a_utm[0] - ll_a_utm[0]) * (tr_a_utm[1] - ll_a_utm[1])
        
#        print ll_a_utm
#        print tr_a_utm
        
        total_c    = 0
        total_area = 0
        for y, row in enumerate(self.data):
            for x, cell in enumerate(row):
                ll_cell_utm, tr_cell_utm = self.get_data_boundary_utm(x, y)
                try:
                    area = intersect(ll_a_utm, tr_a_utm, ll_cell_utm, tr_cell_utm, self.cell_area)
                    
                except:
                    print "error", x, y, ll_a_utm, tr_a_utm, ll_cell_utm, tr_cell_utm
                    print "--> ", is_intersect(ll_a_utm, tr_a_utm, ll_cell_utm, tr_cell_utm, True)
                if area == None:
                    print "none", x, y, ll_a_utm, tr_a_utm, ll_cell_utm, tr_cell_utm
                total_area = total_area + area
                total_c = total_c + (cell.conc * area)
        
#        if total_area > 0:
#            avg_c = total_c / area_a
#            print area_a, total_area
        
        avg_c = self.default_conc
        if (total_area > 0) and (total_area > area_a):
#            print "scenario 1"
            avg_c = total_c / total_area
#            print ":::", area_a, total_area, ((total_area - area_a) / area_a)
        elif (total_area > 0) and (total_area < area_a):
#            print "scenario 2"
            avg_c = total_c / area_a
#            print ":::", area_a, total_area, ((total_area - area_a) / area_a)
        if avg_c < 0:
             avg_c = 0
        
        return avg_c * self.conv_factor
    
    def get_average_conc_utm(self, ll, tr):
        """mengembalikan konsentrasi pencemar rata2 dalam suatu area"""
        ll_g = self.ll_x, self.ll_y
        tr_g = self.tr_x, self.tr_y
        ll_a = ll
        tr_a = tr
#        print ll_g
#        print tr_g
#        print utm.convert_to_utm_fixzone(-6.51, 107.21, self.zone, self.hem)
#        print utm.convert_to_utm_fixzone(-6.31, 107.41, self.zone, self.hem)
        
        if is_intersect(ll_a, tr_a, ll_g, tr_g) == False:
            #area tidak berpotongan
            return self.default_conc
        
        area_a = (tr_a[0] - ll_a[0]) * (tr_a[1] - ll_a[1])
        
        debug_c_tot = 0.0
        debug_n = 0.0
        
        total_c    = 0.0
        total_area = 0.0
        for y, row in enumerate(self.data):
            for x, cell in enumerate(row):
                ll_cell, tr_cell = self.get_data_boundary_utm(x, y)
                
                try:
                    area = intersect(ll_a, tr_a, ll_cell, tr_cell, self.cell_area)
                except:
                    print "error", x, y, ll_a, tr_a, ll_cell, tr_cell
                    print "--> ", is_intersect(ll_a, tr_a, ll_cell, tr_cell, True)
                
                if area > 0:
                    debug_c_tot = debug_c_tot + cell.conc
                    debug_n = debug_n + 1
                
                if area < self.cell_area and area > 0:
                    lll = is_intersect(ll_a, tr_a, ll_cell, tr_cell, True)
#                    if (lll[1] == 4) and (tr_cell[1]>ll_a[1] ):
#                        print "kok aneh", (area, self.cell_area)
#                        print lll
#                        print ll_a, tr_a
#                        print ll_cell, tr_cell
#                        area = 0
#                    print 'dx, dy', self.dx, self.dy
#                if area > 0:
#                    print x, y, area, cell.conc
                total_area = total_area + area
                total_c = total_c + (cell.conc * area)
        
        avg_c = self.default_conc
        if (total_area > 0) and (total_area > area_a):
#            print "scenario 1"
            avg_c = total_c / total_area
#            print ":::", area_a, total_area, ((total_area - area_a) / area_a)
#            print "debug_conc:", debug_c_tot / debug_n
#            print "alternate conc:", total_c / area_a
        elif (total_area > 0) and (total_area < area_a):
#            print "scenario 2"
            avg_c = total_c / area_a
#            print ":::", area_a, total_area, ((total_area - area_a) / area_a)
#            print "debug_conc:", debug_c_tot / debug_n
#            print "alternate conc:", total_c / total_area
        
#        print "conc:", avg_c
        if avg_c < 0:
             avg_c = 0

        return avg_c * self.conv_factor
        
if __name__ == '__main__':
    dat = []
    
    eg = EmissGroup()
    eg.set_dimension(90, 90)
    for y in range(90):
        for x in range(90):
            tmp = EmissData()
            tmp.conc = y*10 + x
            tmp.lat = -7 + y*0.01
            tmp.lon = 107 + x*0.01
            tmp.x, tmp.y = utm.convert_to_utm(tmp.lat, tmp.lon)
#            print tmp.x, tmp.y
#            dat.append(tmp)
            eg.append_data(tmp)
    
#    for d in dat:
#        eg.append_data(d)
#    for b in eg.data[1]:
#        print b.lat, b.lon
#    print len(eg.data[1])
#    for a in eg.data:
#        for b in a:
#            print b.lat, b.lon
    
#    print eg.get_data(3, 1)
    print "size: ", eg.w, eg.h
    
    print '------'
    d = eg.get_data(0, 0)
    print d.lat, d.lon
    print '------'
    
    eg.compute_boundary()
    print '--------'
    print eg.ll_lat, eg.ll_lon, eg.tr_lat, eg.tr_lon
    print eg.ll_x, eg.ll_y, eg.tr_x, eg.tr_y
    print eg.zone, eg.hem, eg.lat, eg.lon
    
    print '--------'
    print eg.get_data_boundary_utm(0, 0)
    print utm.convert_to_utm(-7,107)
    print utm.convert_to_utm(-7 + 89*0.01,107)
    

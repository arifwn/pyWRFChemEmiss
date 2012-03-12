
"""Unit Test"""
import unittest
import data_downscaler
import utm

class DataDownscalerTest(unittest.TestCase):
    """ Unit test untuk model data_downscaler"""
    def setUp(self): 
        eg = data_downscaler.EmissGroup()
        eg.set_dimension(90, 90)
        for y in range(90):
            for x in range(90):
                tmp = data_downscaler.EmissData()
                tmp.conc = y*10 + x + 5.0
                tmp.lat = -7 + y*0.01
                tmp.lon = 107 + x*0.01
                tmp.x, tmp.y = utm.convert_to_utm(tmp.lat, tmp.lon)
                eg.append_data(tmp)
        self.eg = eg
    
    def tearDown(self):
        """teardown"""
        pass
        
    def test_minmax_conc(self):
        #print self.eg.min_conc, self.eg.max_conc
        self.assertAlmostEqual(self.eg.min_conc, 5.0)
        self.assertAlmostEqual(self.eg.max_conc, 890 + 89 + 5.0)
        
    def test_boundary(self):
        self.eg.compute_boundary()
        
        # dx/dy
        self.assertAlmostEqual(self.eg.dx_deg, 0.01)
        self.assertAlmostEqual(self.eg.dy_deg, 0.01)
        self.assertAlmostEqual(self.eg.dx, 1105.499985194703)
        self.assertAlmostEqual(self.eg.dy, 1106.1061631874181)
        self.assertAlmostEqual(self.eg.cell_area, self.eg.dx * self.eg.dy, 6)
        
        #lat/lon boundary
        self.assertAlmostEqual(self.eg.ll_lat, -7, 2)
        self.assertAlmostEqual(self.eg.ll_lon, 107, 2)
        self.assertAlmostEqual(self.eg.tr_lat, -6.1)
        self.assertAlmostEqual(self.eg.tr_lon, 107.9)
        
        #utm boundary
        self.assertAlmostEqual(self.eg.ll_x, 720945.8886136067)
        self.assertAlmostEqual(self.eg.ll_y, 9225781.03362488)
        self.assertAlmostEqual(self.eg.tr_x, 821008.9658143688)
        self.assertAlmostEqual(self.eg.tr_y, 9324882.588855518)
        
    def test_get_cell_data(self):
        cell = self.eg.get_data(0,1)
        self.assertAlmostEqual(cell.lat, -6.99)
        self.assertAlmostEqual(cell.lon, 107)
        self.assertAlmostEqual(cell.conc, 15)
        
    def test_get_cell_boundary(self):
        self.eg.compute_boundary()
        ll, tr = self.eg.get_data_boundary_latlon(0,1)
        self.assertAlmostEqual(ll[0], -6.99)
        self.assertAlmostEqual(ll[1], 107)
        self.assertAlmostEqual(tr[0], -6.98)
        self.assertAlmostEqual(tr[1], 107.01)
        
    def test_is_intersect(self):
        #test fingsi is inside
        point = (5.0, 5.0)
        ll = (0.0, 0.0)
        tr = (10.0, 10.0)
        ret = data_downscaler.point_is_inside(point, ll, tr)
        self.assertTrue(ret)
        point = (5.0, 15.0)
        ret = data_downscaler.point_is_inside(point, ll, tr)
        self.assertFalse(ret)
        
        #kotak a == kotak b 
        ll_a = (0.0, 0.0)
        tr_a = (10.0, 10.0)
        ll_b = (0.0, 0.0)
        tr_b = (10.0, 10.0)
        ret, t = data_downscaler.is_intersect(ll_a, tr_a, ll_b, tr_b, True)
        self.assertTrue(ret)
        self.assertEqual(t, 2)
        
        #tipe 1: titik potong=0, tidak berpotongan
        ll_a = (0.0, 0.0)
        tr_a = (10.0, 10.0)
        ll_b = (15.0, 0.0)
        tr_b = (20.0, 10.0)
        ret, t = data_downscaler.is_intersect(ll_a, tr_a, ll_b, tr_b, True)
        self.assertFalse(ret)
        self.assertEqual(t, 1)
        
        #tipe 2: titik potong=0, b di dalam a
        ll_b = (0.0, 0.0)
        tr_b = (10.0, 10.0)
        ll_a = (3.0, 3.0)
        tr_a = (6.0, 6.0)
        ret, t = data_downscaler.is_intersect(ll_a, tr_a, ll_b, tr_b, True)
        self.assertTrue(ret)
        self.assertEqual(t, 2)
        
        #tipe 2 : 
        ll_a = (0.0, 0.0)
        tr_a = (10.0, 10.0)
        ll_b = (0.0, 5.0)
        tr_b = (5.0, 10.0)
        ret, t = data_downscaler.is_intersect(ll_a, tr_a, ll_b, tr_b, True)
        self.assertTrue(ret)
        self.assertEqual(t, 2)
        
        #tipe 3 : titik potong=2, pojok
        ll_b = (0.0, 0.0)
        tr_b = (10.0, 10.0)
        ll_a = (5.0, 5.0)
        tr_a = (15.0, 15.0)
        ret, t = data_downscaler.is_intersect(ll_a, tr_a, ll_b, tr_b, True)
        self.assertTrue(ret)
        self.assertEqual(t, 3)
        
        #tipe 4 : titik potong=2
        ll_a = (0.0, 0.0)
        tr_a = (10.0, 10.0)
        ll_b = (3.0, -3.0)
        tr_b = (6.0, 6.0)
        ret, t = data_downscaler.is_intersect(ll_a, tr_a, ll_b, tr_b, True)
        self.assertTrue(ret)
        self.assertEqual(t, 4)
        
        #tipe 5: titik potong=4, potongan cross
        ll_b = (0.0, 3.0)
        tr_b = (10.0, 6.0)
        ll_a = (3.0, 0.0)
        tr_a = (6.0, 10.0)
        ret, t = data_downscaler.is_intersect(ll_a, tr_a, ll_b, tr_b, True)
        self.assertTrue(ret)
        self.assertEqual(t, 5)
        
    def test_intersect_area(self):
        ll_a = (0.0, 0.0)
        tr_a = (10.0, 10.0)
        ll_b = (5.0, 0.0)
        tr_b = (10.0, 10.0)
        ret = data_downscaler.intersect(ll_a, tr_a, ll_b, tr_b)
        self.assertAlmostEqual(ret, float(5 * 10))
        
        ll_a = (0.0, 0.0)
        tr_a = (10.0, 10.0)
        ll_b = (15.0, 0.0)
        tr_b = (20.0, 10.0)
        ret = data_downscaler.intersect(ll_a, tr_a, ll_b, tr_b)
        self.assertAlmostEqual(ret, 0)
        
        ll_a = (0.0, 0.0)
        tr_a = (10.0, 10.0)
        ll_b = (3.0, 3.0)
        tr_b = (6.0, 6.0)
        ret = data_downscaler.intersect(ll_a, tr_a, ll_b, tr_b)
        self.assertAlmostEqual(ret, 3 * 3)
        
        #type 3
        ll_a = (0.0, 0.0)
        tr_a = (10.0, 10.0)
        ll_b = (5.0, 5.0)
        tr_b = (15.0, 15.0)
        ret = data_downscaler.intersect(ll_a, tr_a, ll_b, tr_b)
        self.assertAlmostEqual(ret, 5 * 5)
        
        #type 4
#        ll_a = (0.0, 0.0)
#        tr_a = (10.0, 10.0)
#        ll_b = (5.0, 3.0)
#        tr_b = (15.0, 6.0)
#        ll_a = (0.0, 0.0)
#        tr_a = (10.0, 10.0)
#        ll_b = (3.0, 5.0)
#        tr_b = (6.0, 15.0)

#        ll_b = (0.0, 0.0)
#        tr_b = (10.0, 10.0)
#        ll_a = (5.0, 3.0)
#        tr_a = (15.0, 6.0)
        ll_b = (0.0, 0.0)
        tr_b = (10.0, 10.0)
        ll_a = (3.0, 5.0)
        tr_a = (6.0, 15.0)
        ret = data_downscaler.intersect(ll_a, tr_a, ll_b, tr_b)
        self.assertAlmostEqual(ret, 5 * 3)
        
        #type 5
        ll_b = (0.0, 3.0)
        tr_b = (10.0, 6.0)
        ll_a = (3.0, 0.0)
        tr_a = (6.0, 10.0)
        ret = data_downscaler.intersect(ll_a, tr_a, ll_b, tr_b)
        self.assertAlmostEqual(ret, 3 * 3)
    

    def test_intersect_type_4(self):
        #bawah:
        RDD = 6
        self.eg.compute_boundary()
        ll_c, tr_c = self.eg.get_data_boundary_utm(20, 20)
        ll_a = (745266.8882878901, 9278874.129457876)
        tr_a = (746372.3882730848, 9279980.235621063)
        ll_b = (745266.8882878901, 9278874.129457876)
        tr_b = (746372.3882730848, 9279980.235621063)
        ctl = round( (9279980.235621063 - 9278874.129457876) * (746372.3882730848 - 745266.8882878901), RDD)
        ret = data_downscaler.intersect(ll_a, tr_a, ll_b, tr_b)
        ret_c = data_downscaler.intersect(ll_c, tr_c, ll_c, tr_c)
#        dat = (1105.499985194703, 1106.1061631874181, 1222800.3470274603)
        dat = (self.eg.dx, self.eg.dy, self.eg.cell_area)
        self.assertAlmostEqual(ret_c, dat[2])
#        self.assertAlmostEqual(ret, dat[2])
#        self.assertAlmostEqual(ret, dat[0] * dat[1])
        self.assertAlmostEqual(tr_c[0] - ll_c[0], dat[0])
        self.assertAlmostEqual(round( (tr_c[0] - ll_c[0]) * (tr_c[1] - ll_c[1]), RDD) , round( ( dat[0] * dat[1] ), RDD))
        self.assertAlmostEqual(ret_c, round( dat[0] * dat[1], RDD))
        self.assertAlmostEqual(746372.3882730848 - 745266.8882878901, dat[0])
        self.assertAlmostEqual(9279980.235621063 - 9278874.129457876, dat[1])
        self.assertAlmostEqual(tr_c[0] - ll_c[0], dat[0])
        self.assertAlmostEqual(tr_c[1] - ll_c[1], dat[1])
        self.assertAlmostEqual(ret, ctl)
        
    
#    def test_get_average_conc_latlon(self):
#        """get_average_conc_latlon"""
#        self.eg.compute_boundary()
#        ll = -6.51, 107.21
#        tr = -6.31, 107.41 
#        conc_1 = self.eg.get_average_conc_latlon_internal_degree(ll, tr)
#        conc_2 = self.eg.get_average_conc_latlon(ll, tr)
#        self.assertAlmostEqual(conc_2, 315.561564527)
    
#    def test_get_average_conc_utm(self):
#        """get_average_conc_utm"""
#        self.eg.compute_boundary()
#        ll = 744401.9743529849, 9279883.783317205
##        tr = 754401.9743529849, 9289883.783317205
#        tr = 766636.0445709932, 9301910.55921678 
#        conc = self.eg.get_average_conc_utm(ll, tr)
#        self.assertAlmostEqual(conc, 315.561564527)
        
    def test_get_average_conc_utm(self):
        """get_average_conc_utm"""
        self.eg.compute_boundary()
        ll = self.eg.ll_x, self.eg.ll_y
        tr = self.eg.tr_x - 500, self.eg.tr_y - 500
        conc = self.eg.get_average_conc_utm(ll, tr)
        avg_c = self.eg.get_average_conc()
        print "% diff:", abs((conc-self.eg.avg_conc) / self.eg.avg_conc) * 100.0
        print "% diff:", abs((conc-avg_c) / avg_c) * 100.0
        print "avg", (self.eg.avg_conc , avg_c), ", % diff", abs((self.eg.avg_conc - avg_c) / avg_c) * 100.0
        print self.eg.n_counter
        self.assertAlmostEqual(conc, self.eg.avg_conc)
        

if __name__ == '__main__':
    unittest.main()
        
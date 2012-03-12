
import cPickle
import data_downscaler

class RowData():
    def __init__(self, lat, lon, data_list, x=0, y=0):
        self.lat  = lat
        self.lon  = lon
        self.x    = x
        self.y    = y
        self.data = data_list
 
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

def compare_rowdata_f(a, b):
    err = 0.0001
    if (abs(a.lon - b.lon) <= err) and (abs(a.lat - b.lat) <= err):
        return 0
    if ((b.lat - a.lat) >= err):
        return -1
    if (abs(a.lat - b.lat) <= err) and ((b.lon - a.lon) >= err):
        return -1
    return 1

def compare_rowdata_m_f(a, b):
    err = 0.0001
    if (abs(a.x - b.x) <= err) and (abs(a.y - b.y) <= err):
        return 0
    if ((b.y - a.y) >= err):
        return -1
    if (abs(a.y - b.y) <= err) and ((b.x - a.x) >= err):
        return -1
    return 1


 
if __name__ == '__main__':
    print 'Reading cache...'
    cache_path = "res/cache_workbook.cch"
    cache_file = open(cache_path, 'r')
    cache = cPickle.load(cache_file)
    cache_file.close()
    
    print 'Sorting...'
    cache.sort(compare_rowdata_m)
    cnt = 1
    
    eg = data_downscaler.EmissGroup()
    eg.set_dimension(99, 99)
    
    print "Storing..."
    for el in cache:
        tmp = data_downscaler.EmissData()
        tmp.conc = el.data[1]
        tmp.x = el.x
        tmp.y = el.y
        tmp.lat = el.lat
        tmp.lon = el.lon
        eg.append_data(tmp)
#        print cnt, el.lat, el.lon, ' : ', el.data
        cnt = cnt + 1
        if cnt > 99:
            cnt = 1
    
    tmp = eg.get_data(0, 0)
    print tmp.x, tmp.y, tmp.lat, tmp.lon, tmp.conc
    tmp = eg.get_data(0, 1)
    print tmp.x, tmp.y, tmp.lat, tmp.lon, tmp.conc
    
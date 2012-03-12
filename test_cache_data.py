
import cPickle
from openpyxl.reader.excel import load_workbook

class RowData():
    def __init__(self, lat, lon, data_list, x=None, y=None):
        self.lat  = lat
        self.lon  = lon
        self.x    = x
        self.y    = y
        self.data = data_list
        
if __name__ == '__main__':
    print 'caching workbook...'
    path = "res/grid_marsel-new.xlsx"
    cache_path = "res/cache_workbook"
    wb = load_workbook(path)
    sheet = wb.get_active_sheet()
    cache = []
    cells_lat = sheet.range('G2:G9802')
    cells_lon = sheet.range('F2:F9802')
    cells_no2 = sheet.range('B2:B9802')
    cells_so2 = sheet.range('C2:C9802')
    cellsx    = sheet.range('D2:D9802')
    cellsy    = sheet.range('E2:E9802')
    
    
    data_len = len(cells_lat)
    for i in range(data_len):
        row = RowData(cells_lat[i][0].value, cells_lon[i][0].value, 
                      (cells_no2[i][0].value, cells_so2[i][0].value),
                      cellsx[i][0].value, cellsy[i][0].value)
        cache.append(row)
    
    cache_file = open('res/cache_payload', 'w')
    cPickle.dump(cache, cache_file)
    cache_file.close()
    print 'Done!'
    
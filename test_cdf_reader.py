
import pupynere

if __name__ == '__main__':
    path = 'res/test_cdf'
#    path = 'res/wrfchemi_00z_d01'
#    path = 'res/wrfout_d01'
    cdf_file = pupynere.netcdf_file(path)
    print "Variables"
    v = []
    for key in cdf_file.variables:
        #print key, cdf_file.variables[key]
        v.append(key)
    v.sort()
    print v
    print 'Dimensions'
    print cdf_file.dimensions
    
    print 'so2'
    so2 = cdf_file.variables['E_SO2']
    print so2.units
    print so2.dimensions
#    print so2.getValue()
    print so2.shape
    print so2[0][1][89][89]
    #         T  z  y   x
    print so2.typecode()
    
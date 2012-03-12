
import pupynere

if __name__ == '__main__':
    print 'write netcdf file'
    path = 'res/test_cdf'
    cdf_file = pupynere.netcdf_file(path, 'w')
    cdf_file.createDimension('Time', 12)
    cdf_file.createDimension('south_north', 90)
    cdf_file.createDimension('emissions_zdim', 2)
    cdf_file.createDimension('DateStrLen', 19)
    cdf_file.createDimension('west_east', 90)
    so2 = cdf_file.createVariable('E_SO2', 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east'))
    so2.units = 'mol km^-2 hr^-1'
    olt = cdf_file.createVariable('E_OLT', 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east'))
    olt.units = 'mol km^-2 hr^-1'
    ora2 = cdf_file.createVariable('E_ORA2', 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east'))
    ora2.units = 'mol km^-2 hr^-1'
    co = cdf_file.createVariable('E_CO', 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east'))
    co.units = 'mol km^-2 hr^-1'
    eci = cdf_file.createVariable('E_ECI', 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east'))
    eci.units = 'mol km^-2 hr^-1'
    ecj = cdf_file.createVariable('E_ECJ', 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east'))
    ecj.units = 'mol km^-2 hr^-1'
    pm10 = cdf_file.createVariable('E_PM_10', 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east'))
    pm10.units = 'mol km^-2 hr^-1'
    oli = cdf_file.createVariable('E_OLI', 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east'))
    oli.units = 'mol km^-2 hr^-1'
    eth = cdf_file.createVariable('E_ETH', 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east'))
    eth.units = 'mol km^-2 hr^-1'
    pm25i = cdf_file.createVariable('E_PM25I', 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east'))
    pm25i.units = 'mol km^-2 hr^-1'
    hc5 = cdf_file.createVariable('E_HC5', 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east'))
    hc5.units = 'mol km^-2 hr^-1'
    pm25j = cdf_file.createVariable('E_PM25J', 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east'))
    pm25j.units = 'mol km^-2 hr^-1'
    hc3 = cdf_file.createVariable('E_HC3', 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east'))
    hc3.units = 'mol km^-2 hr^-1'
    hc8 = cdf_file.createVariable('E_HC8', 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east'))
    hc8.units = 'mol km^-2 hr^-1'
    no3j = cdf_file.createVariable('E_NO3J', 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east'))
    no3j.units = 'mol km^-2 hr^-1'
    no3i = cdf_file.createVariable('E_NO3I', 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east'))
    no3i.units = 'mol km^-2 hr^-1'
    ket = cdf_file.createVariable('E_KET', 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east'))
    ket.units = 'mol km^-2 hr^-1'
    orgi = cdf_file.createVariable('E_ORGI', 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east'))
    orgi.units = 'mol km^-2 hr^-1'
    hcho = cdf_file.createVariable('E_HCHO', 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east'))
    hcho.units = 'mol km^-2 hr^-1'
    csl = cdf_file.createVariable('E_CSL', 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east'))
    csl.units = 'mol km^-2 hr^-1'
    ald = cdf_file.createVariable('E_ALD', 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east'))
    ald.units = 'mol km^-2 hr^-1'
    so4i = cdf_file.createVariable('E_SO4I', 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east'))
    so4i.units = 'mol km^-2 hr^-1'
    so4j = cdf_file.createVariable('E_SO4J', 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east'))
    so4j.units = 'mol km^-2 hr^-1'
    tol = cdf_file.createVariable('E_TOL', 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east'))
    tol.units = 'mol km^-2 hr^-1'
    iso = cdf_file.createVariable('E_ISO', 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east'))
    iso.units = 'mol km^-2 hr^-1'
    ol2 = cdf_file.createVariable('E_OL2', 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east'))
    ol2.units = 'mol km^-2 hr^-1'
    xyl = cdf_file.createVariable('E_XYL', 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east'))
    xyl.units = 'mol km^-2 hr^-1'
    orgj = cdf_file.createVariable('E_ORGJ', 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east'))
    orgj.units = 'mol km^-2 hr^-1'
    no = cdf_file.createVariable('E_NO', 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east'))
    no.units = 'mol km^-2 hr^-1'
    nh3 = cdf_file.createVariable('E_NH3', 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east'))
    nh3.units = 'mol km^-2 hr^-1'
    times = cdf_file.createVariable('Times', 'c', ('Time', 'DateStrLen'))
    
    for i in range(12): #time
        for j in range(1): #z level
            for y in range(90):
                for x in range(90):
                    so2[i][j][y][x] = (y * 10) + x 
    
    cdf_file.close()
    
    
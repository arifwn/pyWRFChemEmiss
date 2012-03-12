
"""
Konversi latitude longitude ke UTM -- Lebih akurat?
Persamaan dari http://www.uwgb.edu/dutchs/usefuldata/utmformulas.htm

penggunaan:
- gunakan clean_latlon() untuk mendapatkan koordinat dalam format: 
  ( -180 < lon <= 180 ) dan (-90 < lat < 90) 
- gunakan get_zone_hem(lat, lon) untuk mendapatkan zona utm dan hemisfer dari 
  suatu koordinat, hem --> 1: utara, 2: selatan
- gunakan convert_to_utm(lat, lon) untuk mendapatkan easting dan northing dalam UTM
- gunakan convert_to_utm_fixzone(lat, lon, zone, hem) untuk mendapatkan easting dan northing dalam UTM 
  pada zona tertentu
- gunakan convert_to_latlon(easting, northing, zone, hem) untuk mendapatkan
  latitude dan longitude dari suatu koordinat UTM
_________________
Arif Widi Nugroho
arif@hexarius.com
"""

import math

def clean_lon(lon):
    if lon >= 180:
        if ((lon / 180) % 2) == 0:
            lon = lon % 360
        else:
            lon = (int(lon/180) * (lon % 180)) - 180
    return lon

def clean_latlon(lat, lon):
    lon = clean_lon(lon)
    return lat, lon

def get_zone_hem(lat, lon):
    """mengembalikan zone utm dan hemisphere"""
    
    lat, lon = clean_latlon(lat, lon)

    lon_x = abs(lon + 180)
    
    zone = int(lon_x / 6) + 1
    hem = 1 # 1: North, 2: South
    if lat < 0:
        hem = 2
    if lon == -9999.0:
        zone = 0
    if lat == -9999.0:
        hem = 0
    if zone > 60:
        zone = zone % 60
    return zone, hem


def compute_m(lat_rad, lon_rad):
    a = 6378137.0         # equatorial radius
    f = 0.0033528106643315515 # flattening
    b = a * (1 - f)
    esq = (1 - (b / a) * ( b / a))
    M = lat_rad*(1 - esq*(1.0/4.0 + esq*(3.0/64.0 + 5.0*esq/256.0)))
    M = M - math.sin(2.0*lat_rad)*(esq*(3.0/8.0 + esq*(3.0/32.0 + 45.0*esq/1024.0)))
    M = M + math.sin(4.0*lat_rad)*(esq*esq*(15.0/256.0 + esq*45.0/1024.0))
    M = M - math.sin(6.0*lat_rad)*(esq*esq*esq*(35.0/3072.0))
    M = M * a
    
    return M

def convert_to_utm(lat, lon):
    zone, hem = get_zone_hem(lat, lon)
    return convert_to_utm_fixzone(lat, lon, zone, hem)

def convert_to_utm_fixzone(lat, lon, zone, hem):
    lat_rad  = math.radians(lat)
    lon_rad  = math.radians(lon)
    lon_cent = math.radians(clean_lon(-180.0 + (6.0 * (zone - 1))) + 3.0)
    
    p        = lon_rad - lon_cent
    #central meridian di zone utm tersebut

    r_eq  = 6378137.0         # equatorial radius
    f     = 0.0033528106643315515 # flattening
    r_pol = r_eq * (1.0 - f)
    kk    = 0.9996         
    ec    = math.sqrt(1.0 - (r_pol * r_pol) / (r_eq * r_eq)) # eccentricity
    ee2   = (ec * ec)/(1.0 - ec * ec)
    
    m_val = compute_m(lat_rad, lon_rad)
    tmp_1 = r_eq / math.sqrt(1.0 - math.pow(ec * math.sin(lat_rad), 2))
    tmp_2 = math.pow(math.tan(lat_rad), 2)
    tmp_3 = ee2*math.pow(math.cos(lat_rad), 2)
    tmp_4 = p * math.cos(lat_rad)
    
    easting = kk * tmp_1 * tmp_4 * (1 + tmp_4 * tmp_4 * ((1 - tmp_2 + tmp_3) / 6.0 + tmp_4 * tmp_4 * (5.0 - 18.0 * tmp_2 + tmp_2 * tmp_2 + 72.0 * tmp_3 - 58.0 * ee2) / 120.0))
    easting = easting + 500000.0
    
    northing = kk * (m_val + tmp_1 * math.tan(lat_rad) * (tmp_4 * tmp_4 * (1.0 / 2.0 + tmp_4 * tmp_4 * ((5.0 - tmp_2 + 9.0 * tmp_3 + 4 * tmp_3 * tmp_3)/24.0 + tmp_4 * tmp_4 * (61.0 - 58.0 * tmp_2 + tmp_2 * tmp_2 + 600.0 * tmp_3 - 330.0 * ee2) / 720.0))))
    
    if northing < 0:
        #hemisfer selatan
        northing = northing + 10000000
        
    return easting, northing

def convert_to_latlon(easting, northing, zone, hem):
    # konversi dari utm ke lat/lon
    # hem: 1: utara, 2:selatan
    lon_cent = clean_lon(-180.0 + (6.0 * (zone - 1))) + 3.0
    
    r_eq  = 6378137.0         # equatorial radius
    f     = 0.0033528106643315515 # flattening
    r_pol = r_eq * (1.0 - f)
    kk    = 0.9996         
    ec    = math.sqrt(1.0 - (r_pol * r_pol) / (r_eq * r_eq)) # eccentricity
    esq   = (1 - (r_pol / r_eq) * (r_pol / r_eq))
    ee2   = ec * ec / (1.0 - ec * ec)
    ee1   = (1.0 - math.sqrt(1.0 - ec * ec))/(1.0 + math.sqrt(1.0 - ec * ec))
    m_val = northing / kk
    if hem == 2: 
        # hemisfer selatan
        m_val = (northing - 10000000.0) / kk
    
    tmp_1 = m_val / (r_eq * (1.0 - esq * (1.0 / 4.0 + esq * (3.0 / 64.0 + 5.0 * esq / 256.0))))
    tmp_2 = tmp_1 + ee1 * (3.0 / 2.0 - 27.0 * ee1 * ee1 / 32.0) * math.sin(2.0 * tmp_1) + ee1 * ee1 * (21.0 / 16.0 - 55.0 * ee1 * ee1/32.0) * math.sin(4.0 * tmp_1)
    tmp_2 = tmp_2 + ee1 * ee1 * ee1 * (math.sin(6.0 * tmp_1) * 151.0 / 96.0 + ee1 * math.sin(8.0 * tmp_1) * 1097.0 / 512.0)
    tmp_3 = ee2 * math.pow(math.cos(tmp_2), 2)
    tmp_4 = math.pow(math.tan(tmp_2), 2)
    tmp_5 = r_eq / math.sqrt(1.0 - math.pow(ec * math.sin(tmp_2), 2))
    tmp_6 = tmp_5 * (1 - ec * ec)/(1.0 - math.pow(ec*math.sin(tmp_2), 2))
    tmp_7 = (easting - 500000) / (tmp_5 * kk)
    
    
    lat_rad = (tmp_7 * tmp_7) * (1.0 / 2.0 - tmp_7 * tmp_7 * (5.0 + 3.0 * tmp_4 + 10.0 * tmp_3 - 4.0 * tmp_3 * tmp_3 - 9.0 * ee2) / 24.0)
    lat_rad = lat_rad + math.pow(tmp_7, 6) * (61.0 + 90.0 * tmp_4 + 298.0 * tmp_3 + 45.0 * tmp_4 * tmp_4 -252.0 * ee2 - 3.0 * tmp_3 * tmp_3)/720.0
    lat_rad = tmp_2 - (tmp_5 * math.tan(tmp_2) / tmp_6) * lat_rad
    
    lon_rad = tmp_7 * (1 + tmp_7 * tmp_7 * ((-1 - 2 * tmp_4 - tmp_3) / 6 + tmp_7 * tmp_7 * (5 - 2 * tmp_3 + 28 * tmp_4 - 3 * tmp_3 * tmp_3 + 8 * ee2 + 24 * tmp_4 * tmp_4) / 120)) / math.cos(tmp_2)
    
    lat = math.degrees(lat_rad)
    lon = math.degrees(lon_rad) + lon_cent
    return lat, lon

if __name__ == '__main__':
    print 'Coordinate conversion'
    lat = -7
    lon = 107
    easting = 720945.9
    northing = 9225781
    zone = 48
    hem = 2
    print get_zone_hem(lat, lon), clean_lon(-180.0 + (6.0 * (zone - 1))) + 3.0
    print convert_to_utm(lat, lon)
    print convert_to_utm_fixzone(lat, lon, 48, 2)
    print convert_to_latlon(easting, northing, zone, hem)
    
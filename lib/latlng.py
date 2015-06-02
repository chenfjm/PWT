# vim: set ts=4 et sw=4 sts=4 fileencoding=utf-8 :

import math

def rad(d):  
    """计算弧度 
    """  
    return float(d) * math.pi / 180.0  

def distance(lat1, lng1, lat2, lng2):  
    """通过经纬度计算距离 
    """  
    EARTH_RADIUS = 6378.137  

    radlat1 = rad(lat1)
    radlat2 = rad(lat2)

    a = radlat1 - radlat2
    b = rad(lng1) - rad(lng2)

    s = 2 * math.asin(math.sqrt(math.pow(math.sin(a / 2), 2) + math.cos(radlat1) * math.cos(radlat2) * math.pow(math.sin(b / 2), 2)))  
    s = s * EARTH_RADIUS  
    if s < 0:
       return '%0.1f' % -s
    else:
        return '%0.1f' % s;  

if __name__ == '__main__':

    print distance(37.480563, 121.467113, 37.480591, 121.467926)

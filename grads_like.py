import numpy             as np
import matplotlib.pyplot as plt
import cartopy.crs       as ccrs

class mapplot:

    def __init__(self, fig, ax, posit, lon, lat, lev=None, lonlim=None, latlim=None, levlim=None, center=None, **kwargs):

        self.lon = np.array(lon)
        self.lat = np.array(lat)
        self.lev = np.array(lev)

        self.set_lon(lonlim)
        self.set_lat(latlim)
        self.set_lev(levlim)

        center = self.__toList(center)
        if (len(center) == 1):
            center = center + [None]
        self.set_center(center[0], center[1])

        self.__figureProjection()
        
        self.__kwargs = kwargs

        isValid = True
        if (isinstance(posit, int):
            if (posit >= 111 and posit <= 999):
                rows  = int(posit/100)
                lines = int(posit/10) - rows*10
                idx   = posit - (rows*100 + lines*10)
            else:
                isValid = False
        elif (isinstance(posit, list)):
            if (len(posit) == 3):
                rows  = posit[0]
                lines = posit[1]
                idx   = posit[2]
            else:
                isValid = False
        else:
            isValid = False

        if (not isValid):
            raise ValueError(f'Invalid posit : {posit}')

        self.fig = fig
        self.ax  = fig.add_subplot(rows, lines, idx, projection=self.__proj)


    def set_lon(self, lonlim=None):
        lonlim = self.__toList(lonlim)
        if (lonlim[0] is None):
            begval = self.lon[0]
            endval = self.lon[-1]
            if (begval < endval):
                min = begval
                max = endval
            else:
                min = endval
                max = begval
            lonlim = [min, max]
        elif (len(lonlim) != 2):
            raise TypeError(f'Invalid Longitude Range : {lonlim}. lonlim must be an array with 2 elements')
        else:
            min = lonlim[0]
            max = lonlim[1]
            if (min > max):
                min = min - 360
                lonlim = [min, max]
        
        self.lonlim = lonlim


    def set_lat(self, latlim=None):
        latlim = self.__toList(latlim)
        if (latlim[0] is None):
            begval = self.lat[0]
            endval = self.lat[-1]
            if (begval < endval):
                min = begval
                max = endval
            else:
                min = endval
                max = begval
            latlim = [min, max]
        elif (len(latlim) != 2):
            raise TypeError(f'Invalid Latitude Range : {latlim}. latlim must be an array with 2 elements')
        else:
            min = latlim[0]
            max = latlim[1]
            if (min > max):
                min = min - 360
                latlim = [min, max]
        
        self.latlim = latlim


    def set_lev(self, levlim=None):
        if (levlim is None):
            levlim = self.lev[0]
        
        self.levlim = levlim


    def set_center(self, lon=None, lat=None):
        if (lon is None):
            lon = (self.lonlim[0] + self.lonlim[1]) * 0.5

        if (lat is None):
            lat = (self.latlim[0] + self.latlim[1]) * 0.5

        self.center = [lon, lat]


    def __figureProjection(self):
        clon = center[0]
        clat = center[1]
        projection = self.projection.lower()
        proj_list = {'platecarree': ccrs.PlateCarree(central_longitude=clon),
                     'albersequalarea': ccrs.AlbersEqualArea(central_longitude=clon, central_latitude=clat),
                     'azimuthalequidistant': ccrs.AzimuthalEquidistant(central_longitude=clon, central_latitude=clat),
                     'equidistantconic': ccrs.EquidistantConic(central_longitude=clon, central_latitude=clat),
                     'lambertconformal': ccrs.LambertConformal(central_longitude=clon, central_latitude=clat),
                     'lambertcylindrical': ccrs.LambertCylindrical(central_longitude=clon, central_latitude=clat),
                     'mercator': ccrs.Mercator(central_longitude=clon, min_latitude=self.latlim[0], max_latitude=self.latlim[1]),
                     'miller': ccrs.Miller(central_longitude=clon),
                     'mollweide': ccrs.Mollweide(central_longitude=clon),
                     'obliquemercator': ccrs.ObliqueMercator(central_longitude=clon, central_latitude=clat),
                     'orthographic': ccrs.Orthographic(central_longitude=clon, central_latitude=clat),
                     'robinson': ccrs.Robinson(central_longitude=clon),
                     'sinusoidal': ccrs.Sinusoidal(central_longitude=clon),
                     'stereographic': ccrs.Stereographic(central_latitude=clat),
                     'transversemercator': ccrs.TransverseMercator(central_longitude=clon, central_latitude=clat),
                    }

        crs_list = {'platecarree': ccrs.PlateCarree(),
                    'albersequalarea': ccrs.AlbersEqualArea(),
                    'azimuthalequidistant': ccrs.AzimuthalEquidistant(),
                    'equidistantconic': ccrs.EquidistantConic(),
                    'lambertconformal': ccrs.LambertConformal(),
                    'lambertcylindrical': ccrs.LambertCylindrical(),
                    'mercator': ccrs.Mercator(),
                    'miller': ccrs.Miller(),
                    'mollweide': ccrs.Mollweide(),
                    'obliquemercator': ccrs.ObliqueMercator(),
                    'orthographic': ccrs.Orthographic(),
                    'robinson': ccrs.Robinson(),
                    'sinusoidal': ccrs.Sinusoidal(),
                    'stereographic': ccrs.Stereographic(),
                    'transversemercator': ccrs.TransverseMercator(),
                   }
        
        self.__proj = proj_list[projection]
        self.__crs  =  crs_list[projection]


    def lonlabel(lmin, lmax, lint):
        loc  = np.arange(lmin, lmax+lint, lint)
        self.lonlab = loc


    def latlabel(lmin, lmax, lint):
        loc  = np.arange(lmin, lmax+lint, lint)
        self.latlab = loc


    def __toList(a):
        if (isinstance(a, np.ndarray):
            return a.tolist()
        elif (isinstance(a, (list, tuple))):
            return list(a)
        else:
            return [a]





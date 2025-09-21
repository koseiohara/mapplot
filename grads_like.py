import numpy             as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import cartopy.crs       as ccrs

class mapplot:

    def __init__(self, fig, posit, lon, lat, **kwargs):
        defaults = {'lev': 0.,
                    'lonlim': None,
                    'latlim': None,
                    'levlim': None,
                    'center': None,
                    'projection': 'PlateCarree',
                   }
        unknown = set(kwargs) - defaults.keys()
        if unknown:
            raise TypeError(f"Unexpected Keyword(s): {', '.join(sorted(unknown))}. Allowed keywords: fig, posit, lon, lat, {', '.join(sorted(defaults.keys()))}")
        args = defaults.copy()
        args.update(kwargs)

        self.lon = np.array(lon)
        self.lat = np.array(lat)
        self.lev = np.array(args['lev'])

        self.mglon, self.mglat = np.meshgrid(self.lon, self.lat)

        self.projection = args['projection']
        self.set_lon(args['lonlim'])
        self.set_lat(args['latlim'])
        self.set_lev(args['levlim'])
        self.center = args['center']

        self.method = 'contour'
        self.cmap   = 'bwr'
        self.colors = None

        self.__proj    = None
        self.__crs     = None

        center = self.__toList(center)
        if (len(center) == 1):
            center = center + [None]
        self.set_center(center[0], center[1])

        self.__figureProjection()
        
        self.__kwargs = args

        isValid = True
        if (isinstance(posit, int)):
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

        self.fig   = fig
        self.ax    = fig.add_subplot(rows, lines, idx, projection=self.__proj)
        self.cont  = None
        self.shade = None
        self.ccbar = None       ## Color Bar for contour
        self.scbar = None       ## Color Bar for shade

        self.ax.coastlines()


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


    def set_label(self, fontsize=10, grid=False, linewidth=1, linestyle='-', color='black', alpha=1):
        self.ax.gridlines(crs=self.__crs, linewidth=linewidth, linestyle=linestyle, color=color, alpha=alpha)
        self.ax.gridlines.xlabel_style = {'size': fontsize, 'color': 'black'}
        self.ax.gridlines.ylabel_style = {'size': fontsize, 'color': 'black'}

        self.ax.gridlines.xlines = grid
        self.ax.gridlines.ylines = grid


    def label_loc(self, which, location):
        which = which.lower()
        if (which == 'x' or which == 'lon'):
            self.ax.gridlines.xlocator = mticker.FixedLocator(location)
        elif (which == 'y' or which == 'lat'):
            self.ax.gridlines.ylocator = mticker.FixedLocator(location)


    def gxout(self, method, cmap=None, colors=None):
        method_allowed = ['contour', 'shaded']
        method = method.lower()
        if (method in method_allowed):
            self.method = method.lower()
        else:
            raise ValueError('Invalid method was given to gxout(). Options : ' + ', '.join(method_allowed))

        if (cmap is not None):
            self.cmap   = cmap
            self.colors = None

        if (colors is not None):
            self.cmap   = None
            self.colors = colors


    #def display(self, data, levels=None, extend='both', linestyles='solid', negative_linestyle='solid', **kwargs):
    #    args = dict(kwargs)
    #    args['transform'] = self.__crs

    #    if (levels is not None):
    #        args['levels'] = levels

    #    if (self.cmap is not None):
    #        args['cmap'] = self.cmap
    #    if (kwargs.get('cmap', None) is not None):
    #        args['cmap'] = kwargs['cmap']

    #    if (self.colors is not None):
    #        args['colors'] = self.colors
    #    if (kwargs.get('colors', None) is not None):
    #        args['colors'] = kwargs['colors']


    #    if (self.method == 'contour'):
    #        args['linestyles']         = linestyles
    #        args['negative_linestyle'] = negative_linestyle
    #    elif (self.method == 'shaded'):
    #        args['extend']    = extend


    #    # Plot
    #    if (self.method == 'contour'):
    #        self.__plot_contour(data, **args)
    #    elif (self.method == 'shaded'):
    #        self.__plot_shaded(data, **args)


    def display(self, data, **kwargs):
        if (self.method == 'contour'):
            defaults = {'linestyles': 'solid', 'negative_linestyle': 'solid'}
        elif (self.method == 'shaded'):
            defaults = {'extend': 'both'}
        else:
            print('DEBUG : Unexpected method')

        args = defaults.copy()
        if (self.cmap is not None):
            args['cmap'] = self.cmap

        if (self.colors is not None):
            args['colors'] = self.colors

        args.update(kwargs)

        args['transform'] = self.__crs


        if (data.ndim == 1 or data.ndim > 3):
            raise TypeError('Invalid data shape was obtained to display()')
        elif (data.ndim == 2):
            data_pass = data[:,:]
        elif (data.ndim == 3):
            data_pass = data[self.lev==self.levlim:,:]
        
        self.ax.set_extent(self.lonlim + self.latlim, crs=self.__crs)

        # Plot
        if (self.method == 'contour'):
            self.__plot_contour(data_pass, **args)
        elif (self.method == 'shaded'):
            self.__plot_shaded(data_pass, **args)
        

    def __plot_contour(self, data, **kwargs):
        
        self.cont = self.ax.contour(self.mglon,
                                    self.mglat,
                                    data      ,
                                    **kwargs  )


    def __plot_shaded(self, data, **kwargs):
        
        self.shade = self.ax.contourf(self.mglon,
                                      self.mglat,
                                      data      ,
                                      **kwargs  )


    def set_cbar(self, which='shaded', **kwargs):
        defaults = {'location': 'bottom', 'shrink': 0.9, 'aspect': 40}
        args = defaults.copy()
        args.update(kwargs)

        which = which.lower()
        if (which == 'shaded'):
            cbar = self.fig.colorbar(self.shade, ax=self.ax, **args)
        elif (which == 'contour'):
            cbar = self.fig.colorbar(self.cont , ax=self.ax, **args)
        
        if (which == 'shaded'):
            self.scbar = cbar
        elif (which == 'contour'):
            self.ccbar = cbar


    def __figureProjection(self):
        clon = self.center[0]
        clat = self.center[1]
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
        
        try:
            self.__proj = proj_list[projection]
            self.__crs  =  crs_list[projection]
        except:
            maps = []
            for proj in proj_list:
                maps = maps + ['"' + proj + '"']
            err = f'{self.projection} is not in the projection list : ' + ', '.join(maps) + '. '
            err = err + 'See the following website for the allowed projection : https://cartopy.readthedocs.io/stable/reference/projections.html'
            raise ValueError(err)


    def __toList(self, a):
        if (isinstance(a, np.ndarray)):
            return a.tolist()
        elif (isinstance(a, (list, tuple))):
            return list(a)
        else:
            return [a]





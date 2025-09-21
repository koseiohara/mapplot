import numpy             as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import cartopy.crs       as ccrs

class mapplot:

    def __init__(self, fig, posit, lon, lat, **kwargs):
        defaults = {'lev': 0.     ,                 # Vertical coordinate    : assuming ndarray
                    'lonlim': None,                 # Longitude range to be plotted : assuming list
                    'latlim': None,                 # Latitude range to be plotted : assuming list
                    'levlim': None,                 # Vertical level to be plotted : assuming scalar
                    'center': None,                 # Graph center : assuming list [lon,lat] or scalar lon
                    'projection': 'PlateCarree',    # Graph Projection
                   }
        unknown = set(kwargs) - defaults.keys()
        if unknown:
            raise TypeError(f"Unexpected Keyword(s): {', '.join(sorted(unknown))}. Allowed keywords: fig, posit, lon, lat, {', '.join(sorted(defaults.keys()))}")
        args = defaults.copy()
        args.update(kwargs)

        self.lon = np.array(lon)
        self.lat = np.array(lat)
        self.lev = np.atleast_1d(np.array(args['lev'], dtype=float))

        self.mglon, self.mglat = np.meshgrid(self.lon, self.lat)

        self.projection = args['projection']
        self.set_lon(args['lonlim'])    # Set self.lonlim
        self.set_lat(args['latlim'])    # Set self.latlim
        self.set_lev(args['levlim'])    # Set self.levlim and self.levidx
        self.center = args['center']

        self.method = 'contour'         # Default plot method as contour
        self.cmap   = 'bwr'             # Default color map as blue->white->red
        self.colors = None              # Default colors None

        self.__proj    = None
        self.__crs     = None

        center = self.__toList(args['center'])
        if (len(center) == 1):
            center = center + [None]
        self.set_center(center[0], center[1])

        self.__figureProjection()       # Set projection
        
        self.__kwargs = args            # Copy for future meintainances

        isValid = True
        # Position of ax in figure
        if (isinstance(posit, int)):
            if (posit >= 111 and posit <= 999):
                rows  = int(posit/100)
                lines = int(posit/10) - rows*10
                idx   = posit - (rows*100 + lines*10)
            else:
                isValid = False
        elif (isinstance(posit, list)):
            if (len(posit) == 3):
                rows  = int(posit[0])
                lines = int(posit[1])
                idx   = int(posit[2])
            else:
                isValid = False
        else:
            isValid = False

        if (idx < 1 or idx > rows*lines):
            isValid = False

        if (not isValid):
            raise ValueError(f'Invalid posit : {posit}')

        self.fig   = fig
        self.ax    = self.fig.add_subplot(rows, lines, idx, projection=self.__proj)
        self.cont  = None       # None until contour plot
        self.shade = None       # None until shade plot
        self.ccbar = None       ## Color Bar for contour
        self.scbar = None       ## Color Bar for shade

        self.ax.coastlines()

        self.gridlines = None
        self.__gridlines_init()


    def set_lon(self, lonlim=None):
        lonlim = self.__toList(lonlim)
        if (lonlim[0] is None):
            # Default : All area specified to the constructor
            begval = self.lon[0]
            endval = self.lon[-1]
            if (begval < endval):
                vmin = begval
                vmax = endval
            else:
                vmin = endval
                vmax = begval
            lonlim = [vmin, vmax]
        elif (len(lonlim) != 2):
            raise TypeError(f'Invalid Longitude Range : {lonlim}. lonlim must be a list with 2 elements')
        else:
            # If specified explicitly...
            vmin = lonlim[0]
            vmax = lonlim[1]
            if (vmin > vmax):
                # Rotation
                vmin = vmin - 360
                lonlim = [vmin, vmax]
        
        self.lonlim = lonlim


    def set_lat(self, latlim=None):
        latlim = self.__toList(latlim)
        if (latlim[0] is None):
            # Default : All area specified to the constructor
            begval = self.lat[0]
            endval = self.lat[-1]
            if (begval < endval):
                vmin = begval
                vmax = endval
            else:
                vmin = endval
                vmax = begval
        elif (len(latlim) != 2):
            raise TypeError(f'Invalid Latitude Range : {latlim}. latlim must be a list with 2 elements')
        else:
            vmin = latlim[0]
            vmax = latlim[1]
            if (vmin > vmax):
                # Fix the order of latlim
                tmp  = vmin
                vmin = vmax
                vmax = tmp
            if (vmin < -90.01 or vmax > 90.01):
                # vmin and vmax must be between -90 and 90
                raise ValueError(f'Invalid Latitude Range : {latlim}. Southern and Northern limit must be between -90 and 90')

        self.latlim = [vmin, vmax]


    def set_lev(self, levlim=None):
        if (levlim is None):
            # Default : lev[0]
            levlim = self.lev[0]
        
        self.levlim = levlim
        self.levidx = np.argmin(np.abs(self.lev - levlim))  # Index of the specified vertical level


    def set_center(self, lon=None, lat=None):
        if (lon is None):
            lon = (self.lonlim[0] + self.lonlim[1]) * 0.5

        if (lat is None):
            lat = (self.latlim[0] + self.latlim[1]) * 0.5

        self.center = [lon, lat]


    def set_label(self, fontsize=10, grid=False, linewidth=1, linestyle='-', color='black', alpha=1):
        # Format of tick labels and frid lines
        self.gridlines.xlabel_style = {'size': fontsize, 'color': color}
        self.gridlines.ylabel_style = {'size': fontsize, 'color': color}

        self.gridlines.xlines = grid    # Default : No grid lines
        self.gridlines.ylines = grid    # Default : No grid lines

        self.gridlines.linewidth = linewidth
        self.gridlines.linestyle = linestyle

        self.gridlines.color = color
        self.gridlines.alpha = alpha


    def label_loc(self, which, location):
        which = which.lower()
        if (which == 'x' or which == 'lon'):
            self.gridlines.xlocator = mticker.FixedLocator(location)
        elif (which == 'y' or which == 'lat'):
            self.gridlines.ylocator = mticker.FixedLocator(location)
        else:
            raise ValueError(f'Invalid parameter was obtained to label_loc() : which={which}. which must be "x"/"lon" or "y"/"lat".')


    def gxout(self, method, cmap=None, colors=None):
        # Set plot method : contour of shade/contourf
        method_allowed = ['contour', 'shaded']
        method = method.lower()
        if (method in method_allowed):
            self.method = method.lower()
        else:
            raise ValueError('Invalid method was given to gxout(). Options : ' + ', '.join(method_allowed))

        if (cmap is not None):
            self.cmap   = cmap
            self.colors = None
        # Colors has higher priority
        if (colors is not None):
            self.cmap   = None
            self.colors = colors


    # Plot contour or shade : method follows self.method
    # All arguments from matplotlib contour/contourf are available
    # But 'transform' argument cannot be changed
    def display(self, data, **kwargs):
        if (self.method == 'contour'):
            defaults = {'linestyles': 'solid'}
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
            data_pass = data[self.levidx,:,:]
            print('DEBUG : ', self.levidx)
        
        # Limit the area to be plotted
        self.ax.set_extent(self.lonlim + self.latlim, crs=self.__crs)

        print('DEBUG : ', data_pass[0,:])
        # Plot
        if (self.method == 'contour'):
            self.__plot_contour(data_pass, **args)
        elif (self.method == 'shaded'):
            self.__plot_shaded(data_pass , **args)
        

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


    # Show colorbar
    # All arguments from matplotlib colorbar are available
    def set_cbar(self, which='shaded', **kwargs):
        defaults = {'location': 'bottom', 'shrink': 0.9, 'aspect': 40, 'pad': 0.08}
        args     = defaults.copy()
        args.update(kwargs)
        if (('pad' not in kwargs) and (args['location']=='right' or args['location']=='left')):
            args['pad'] = 0.03

        which = which.lower()
        if (which == 'shaded'):
            # If shaded, show a colorbar of contourf
            if (self.shade is None):
                raise RuntimeError('No shade plot to attach a colorbar to.')
            cbar = self.fig.colorbar(self.shade, ax=self.ax, **args)
        elif (which == 'contour'):
            # If contour, show a colorbar of contour
            if (self.contour is None):
                raise RuntimeError('No contour plot to attach a colorbar to.')
            cbar = self.fig.colorbar(self.cont , ax=self.ax, **args)
        
        if (which == 'shaded'):
            self.scbar = cbar
        elif (which == 'contour'):
            self.ccbar = cbar


    def __figureProjection(self):
        clon = self.center[0]
        clat = self.center[1]
        projection = self.projection.lower()
        proj_list = {'platecarree'         : lambda: ccrs.PlateCarree(central_longitude=clon),
                     'albersequalarea'     : lambda: ccrs.AlbersEqualArea(central_longitude=clon, central_latitude=clat),
                     'azimuthalequidistant': lambda: ccrs.AzimuthalEquidistant(central_longitude=clon, central_latitude=clat),
                     'equidistantconic'    : lambda: ccrs.EquidistantConic(central_longitude=clon, central_latitude=clat),
                     'lambertconformal'    : lambda: ccrs.LambertConformal(central_longitude=clon, central_latitude=clat),
                     'lambertcylindrical'  : lambda: ccrs.LambertCylindrical(central_longitude=clon),
                     'mercator'            : lambda: ccrs.Mercator(central_longitude=clon, min_latitude=self.latlim[0], max_latitude=self.latlim[1]),
                     'miller'              : lambda: ccrs.Miller(central_longitude=clon),
                     'mollweide'           : lambda: ccrs.Mollweide(central_longitude=clon),
                     'obliquemercator'     : lambda: ccrs.ObliqueMercator(central_longitude=clon, central_latitude=clat),
                     'orthographic'        : lambda: ccrs.Orthographic(central_longitude=clon, central_latitude=clat),
                     'robinson'            : lambda: ccrs.Robinson(central_longitude=clon),
                     'sinusoidal'          : lambda: ccrs.Sinusoidal(central_longitude=clon),
                     'stereographic'       : lambda: ccrs.Stereographic(central_latitude=clat),
                     'transversemercator'  : lambda: ccrs.TransverseMercator(central_longitude=clon, central_latitude=clat),
                    }

        try:
            self.__proj = proj_list[projection]()
            #self.__crs  =  crs_list[projection]
            self.__crs  = ccrs.PlateCarree()
        except:
            maps = []
            for proj in proj_list:
                maps = maps + ['"' + proj + '"']
            err = f'{self.projection} is not in the projection list : ' + ', '.join(maps) + '. '
            err = err + 'See the following website for the allowed projection : https://cartopy.readthedocs.io/stable/reference/projections.html'
            raise ValueError(err)


    def __gridlines_init(self):
        # Initializing gridline in the constructor with the default value
        self.__gl_config = {'fontsize' : 10     ,
                            'grid'     : False  ,
                            'linewidth': 1      ,
                            'linestyle': '-'    ,
                            'color'    : 'black',
                            'alpha'    : 1.     ,
                           }
        self.gridlines = self.ax.gridlines(crs        =self.__crs                   ,
                                           linewidth  =self.__gl_config['linewidth'],
                                           linestyle  =self.__gl_config['linestyle'],
                                           color      =self.__gl_config['color']    ,
                                           alpha      =self.__gl_config['alpha']    ,
                                           draw_labels=True                         )
        self.gridlines.xlabel_style = {'size' : self.__gl_config['fontsize'],
                                       'color': self.__gl_config['color']   ,
                                      }
        self.gridlines.ylabel_style = {'size' : self.__gl_config['fontsize'],
                                       'color': self.__gl_config['color']   ,
                                      }
        
        self.gridlines.xlines = self.__gl_config['grid']    # Default : No grid lines
        self.gridlines.ylines = self.__gl_config['grid']    # Default : No grid lines

        self.gridlines.top_labels   = False
        self.gridlines.right_labels = False


    # Convert to List
    def __toList(self, a):
        if (isinstance(a, np.ndarray)):
            return a.tolist()
        elif (isinstance(a, (list, tuple))):
            return list(a)
        else:
            return [a]





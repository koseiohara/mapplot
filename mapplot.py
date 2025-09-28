import warnings
import numpy             as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import cartopy.crs       as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from cartopy.util       import add_cyclic_point

class mapplot:

    def __init__(self, fig, posit, lon, lat, **kwargs):
        defaults = {'lev': 0.     ,                 # Vertical coordinate    : assuming ndarray
                    'lonlim': None,                 # Longitude range to be plotted : assuming list
                    'latlim': None,                 # Latitude range to be plotted : assuming list
                    'levlim': None,                 # Vertical level to be plotted : assuming scalar
                    'projection': None,             # Graph Projection : assuming object
                    'resolution': 'medium',         # Map Resolution : high/h/10m, medium/m/50m, or low/l/110m
                    'central_longitude': None,      # Central longitude of map: range of longitude must not include this value
                    'verbose'          : False,     # print setting information
                   }
        unknown = set(kwargs) - defaults.keys()
        if unknown:
            raise TypeError(f"Unexpected Keyword(s): {', '.join(sorted(unknown))}. Allowed keywords: fig, posit, lon, lat, {', '.join(sorted(defaults.keys()))}")
        args = defaults.copy()
        args.update(kwargs)
        self.__kwargs = args            # Copy for future meintainances

        self.lon = np.array(lon)
        self.lat = np.array(lat)
        self.lev = np.atleast_1d(np.array(args['lev'], dtype=float))

        dummy, self.lon_cycle  = add_cyclic_point(self.lon, coord=self.lon)
        self.mglon, self.mglat = np.meshgrid(self.lon_cycle, self.lat)

        self.__proj            = args['projection']
        self.__crs             = None
        self.central_longitude = args['central_longitude']
        self.edge_longitude    = None
        
        if (self.central_longitude is not None or self.__proj is not None):
            self.__set_clon()                       #  Set self.central_longitude
            self.__set_lon_core(args['lonlim'])     # Set self.lonlim
        else:
            self.__set_lon_core(args['lonlim'])     # Set self.lonlim
            self.__set_clon()                       #  Set self.central_longitude
        self.__set_lon_check()
        self.__set_lat_core(args['latlim'])         # Set self.latlim
        self.set_lev(args['levlim'])    # Set self.levlim and self.levidx

        self.__figureProjection()       # Set projection
        self.projection = self.__proj.__class__.__name__

        self.method = 'contour'         # Default plot method as contour

        self.__cmap_default   = 'bwr'   # Default color map as blue->white->red
        self.__colors_default = None    # Default colors None
        self.cmap   = self.__cmap_default
        self.colors = self.__colors_default

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

        if (isValid):
            if (idx < 1 or idx > rows*lines):
                isValid = False

        if (not isValid):
            raise ValueError(f'Invalid posit : {posit}. Expected a 3-digit subplot code (e.g., 111) or a list [rows, cols, index] with 1 <= index <= rows*cols.')

        self.fig         = fig
        self.ax          = self.fig.add_subplot(rows, lines, idx, projection=self.__proj)
        self.cont        = None     # None until contour plot
        self.shade       = None     # None until shade plot
        self.hatch       = None     # None until hatch plot
        self.vector      = None     # None until vector plot
        self.ccbar       = None     # Color Bar for contour
        self.scbar       = None     # Color Bar for shade
        self.vector_repr = None     # Representative value of vector

        resolution = args['resolution'].lower()
        if (resolution == 'high' or resolution == 'h' or resolution == '10m'):
            self.resolution = 'high'
            cl_resolution   = '10m'
        elif (resolution == 'medium' or resolution == 'm' or resolution == '50m'):
            self.resolution = 'medium'
            cl_resolution   = '50m'
        elif (resolution == 'low' or resolution == 'l' or resolution == '110m'):
            self.resolution = 'low'
            cl_resolution   = '110m'
        else:
            raise ValueError(f'Invalid map resolution : {resolution}\n'
                             'Use one of {"high", "h", "10m", "medium", "m", "50m", "low", "l", "110m"}'
                            )
        self.ax.coastlines(resolution=cl_resolution, linewidth=0.5)

        self.gridlines = None
        self.set_extent()


    def set_lon(self, lonlim=None):
        self.__set_lon_core(lonlim)
        self.__set_lon_check()
        self.set_extent()


    def set_lat(self, latlim=None):
        self.__set_lat_core(latlim)
        self.set_extent()


    def set_lev(self, levlim=None):
        if (levlim is None):
            # Default : lev[0]
            levlim = self.lev[0]
        
        self.levlim = levlim
        self.levidx = np.argmin(np.abs(self.lev - levlim))  # Index of the specified vertical level


    def set_extent(self):
        self.ax.set_extent(self.lonlim + self.latlim, crs=self.__crs)


    def set_label(self, x=None, y=None, fontsize=10, fontcolor='black', grid=True, linewidth=0.7, linestyle=':', linecolor='grey', alpha=0.7):
        # Format of tick labels and grid lines
        self.gridlines = self.ax.gridlines(crs        =self.__crs          ,
                                           linewidth  =linewidth           ,
                                           linestyle  =linestyle           ,
                                           color      =linecolor           ,
                                           alpha      =alpha               ,
                                           draw_labels=True                ,
                                           xformatter =LongitudeFormatter(),
                                           yformatter =LatitudeFormatter() ,
                                          )
        # Specify the locations of ticks
        self.gridlines.xlocator = self.__set_ticks(x)
        self.gridlines.ylocator = self.__set_ticks(y)

        # Tick format
        self.gridlines.xlabel_style = {'size' : fontsize ,
                                       'color': fontcolor,
                                      }

        self.gridlines.ylabel_style = {'size' : fontsize ,
                                       'color': fontcolor,
                                      }

        self.gridlines.xlines = grid    # Default : grid lines on
        self.gridlines.ylines = grid    # Default : grid lines on

        # Delete Top and right ticks
        self.gridlines.top_labels   = False
        self.gridlines.right_labels = False


    def gxout(self, method, cmap=None, colors=None):
        # Set plot method : contour, shade/contourf, hatches, or vector
        method_allowed = ['contour', 'shaded', 'hatches', 'vector']
        method = method.lower()
        if (method in method_allowed):
            self.method = method
        else:
            raise ValueError('Invalid method was provided to gxout(). Options : ' + ', '.join(method_allowed))

        if (method == 'hatches'):
            self.cmap   = None
            self.colors = None
        else:
            self.cmap   = self.__cmap_default
            self.colors = self.__colors_default

        if (cmap is not None):
            self.cmap   = cmap
            self.colors = None
        # colors option has higher priority
        if (colors is not None):
            self.cmap   = None
            self.colors = colors


    # Plot contour or shade : method follows self.method
    # All arguments from matplotlib contour/contourf are available
    # 'transform' argument cannot be changed
    # "y" option is acceptable only if method=vector
    def display(self, data, y=None, **kwargs):
        # Default parameter settings for each method
        if (self.method == 'contour'):
            defaults = {'linestyles': 'solid'}
        elif (self.method == 'shaded'):
            defaults = {'extend': 'both'}
        elif (self.method == 'hatches'):
            defaults = {'size': 0.3, 'color': 'black', 'marker': '.', 'interval': 3}
        elif (self.method == 'vector'):
            defaults = {'angles': 'xy', 'scale_units': 'xy', 'width': 0.003, 'headlength': 2, 'headwidth': 2, 'color': 'black', 'regrid_shape': 30,}

        args = defaults.copy()
        if (self.cmap is not None):
            # if cmap and colors are not specified to this function
            if (('cmap' not in kwargs) and ('colors' not in kwargs)):
                args['cmap'] = self.cmap

        if (self.colors is not None):
            # if cmap and colors are not specified to this function
            if (('cmap' not in kwargs) and ('colors' not in kwargs)):
                args['colors'] = self.colors

        args.update(kwargs)

        args['transform'] = self.__crs
        if ('transform' in kwargs):
            warnings.warn('"transform" argument was overridden in display()', UserWarning)

        if (self.method != 'vector'):
            if (y is not None):
                warnings.warn('Argument "y" was provided to display(), but it is only acceptable when method="vector"', UserWarning)

        data_pass = self.__select_level(data)

        data_pass, dummy = add_cyclic_point(data_pass, coord=self.lon)

        # Plot
        if (self.method == 'contour'):
            self.__plot_contour(data_pass, **args)
        elif (self.method == 'shaded'):
            self.__plot_shaded(data_pass , **args)
        elif (self.method == 'hatches'):
            self.__plot_hatches(data_pass, **args)
        elif (self.method == 'vector'):
            y_pass = self.__select_level(y)
            y_pass, dummy = add_cyclic_point(y_pass, coord=self.lon)
            self.__plot_vector(data_pass, y_pass, **args)


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


    def __plot_hatches(self, data, **kwargs):
        if (not np.issubdtype(data.dtype, np.bool_)):
            raise TypeError('Invalid data type was provided to display(). When method="hatches", array must be a bool type')

        interval = kwargs['interval']

        # Limit density of dots
        work_lon  = self.mglon[::interval,::interval]
        work_lat  = self.mglat[::interval,::interval]
        work_data = data[::interval,::interval]
        y, x = np.where(work_data)
        work_lon = work_lon[y,x]
        work_lat = work_lat[y,x]

        args = kwargs.copy()
        if ('s' not in args):
            args['s'] = args['size']
        if ('c' not in args):
            args['c'] = args['color']
        # Delete 'interval', 'size', 'colors' and 'color'
        args.pop('interval')
        args.pop('size'  , None)
        args.pop('colors', None)
        args.pop('color' , None)
        self.hatch = self.ax.scatter(work_lon,
                                     work_lat,
                                     **args  )


    def __plot_hatches_old(self, data, **kwargs):
        if (not np.issubdtype(data.dtype, np.bool_)):
            raise TypeError('Invalid data type was provided to display(). When method="hatches", array must be a bool type')

        data = data.astype(int)
        kwargs['levels'] = [0.09,1.01]
        kwargs['colors'] = 'none'

        self.hatch = self.ax.contourf(self.mglon,
                                      self.mglat,
                                      data      ,
                                      **kwargs  )


    def __plot_vector(self, x, y, **kwargs):

        self.vector = self.ax.quiver(self.mglon,
                                     self.mglat,
                                     x         ,
                                     y         ,
                                     **kwargs  )

        # Representative length of arrows for vector legend
        lens = x*x + y*y
        percentile = np.nanpercentile(lens, 80)     # 80 percentile
        self.vector_repr = self.__round5(np.sqrt(percentile))


    # Show colorbar
    # All arguments from matplotlib colorbar are available
    def set_cbar(self, which=None, **kwargs):
        defaults = {'location': 'bottom', 'shrink': 0.9, 'aspect': 40, 'pad': 0.08}
        args     = defaults.copy()
        args.update(kwargs)
        if (('pad' not in kwargs) and (args['location']=='right' or args['location']=='left')):
            args['pad'] = 0.03

        if (which is None):
            # shaded method has higher priority
            if (self.shade is not None):
                which = 'shaded'
            elif (self.cont is not None):
                which = 'contour'
            else:
                raise RuntimeError('No plotted artist to attach a colorbar to.\n'
                                   'Call display() to draw a "shaded" (contourf) or "contour" plot first, '
                                   'or specify which"shaded"/"contour".'
                                  )

        which = which.lower()
        if (which == 'shaded'):
            # If shaded, show a colorbar of contourf
            if (self.shade is None):
                raise RuntimeError('Shade plot not found\n'
                                   'Call display() with method="shaded" (contourf) before set_cbar(which="shaded").'
                                  )
            cbar = self.fig.colorbar(self.shade, ax=self.ax, **args)
        elif (which == 'contour'):
            # If contour, show a colorbar of contour
            if (self.cont is None):
                raise RuntimeError('Contour plot not found\n'
                                   'Call display() with method="contour" before set_cbar(which="contour").'
                                  )
            cbar = self.fig.colorbar(self.cont , ax=self.ax, **args)
        else:
            raise ValueError('Invalid "which" for set_cbar(); expected "shaded" or "contour".')

        if (which == 'shaded'):
            self.scbar = cbar
        elif (which == 'contour'):
            self.ccbar = cbar


    def set_vector_legend(self, X, Y, U=None, labelpos='S', label=None, direction='x', coordinates='axes', **kwargs):
        if (self.vector is None):
            raise RuntimeError('Vector plot not found\n'
                               'Call display() with method="vector" before set_vector_legend()'
                              )

        # If U is None, length of reference is automatically chosen using self.vector_repr
        if (U is None):
            U = self.vector_repr

            if (label is None):
                if (U > 0 and U < 1000):
                    U = int(U)
                    label = f'{U}'
                elif (U >= 1000):
                    expon  = self.__digit(U)
                    signif = U * 10**(-expon)
                    label  = fr'${signif:.2f}\times 10^{{{expon}}}$'
        else:
            if (label is None):
                label = f'{U}'

        if ('angle' not in kwargs):
            direction = direction.lower()
            if (direction == 'x'):
                kwargs['angle'] = 0
            elif (direction == 'y'):
                kwargs['angle'] = 90
            else:
                raise ValueError('Invalid value was provided to argument "direction". Specify "x" or "y"')

        self.ax.quiverkey(self.vector, X=X, Y=Y, U=U, labelpos=labelpos, label=label, coordinates=coordinates, **kwargs)


    # Mark to (a) specified position(s)
    def mark(self, x, y, **kwargs):
        defaults = {'marker': 'o', 'c': 'black', 'linewidth': 0}
        args = defaults.copy()
        args.update(kwargs)
        args['transform'] = self.__crs

        self.ax.scatter(x, y, **args)


    def text(self, x, y, s, coord='latlon', **kwargs):
        args = kwargs.copy()

        coord = coord.lower()
        if (coord == 'latlon' or coord == 'll'):
            args['transform'] = self.__crs
        elif (coord == 'ax'):
            args['transform'] = ax.transAxes
        elif (coord == 'fig'):
            args['transform'] = ax.transFigure
        else:
            raise ValueError(f'Unsupported options : {coord}. "latlon", "ax", and "fig" are acceptable.')

        self.ax.text(x, y, s, **args)


    def set_xlabel(self, label, **kwargs):
        self.ax.xlabel(label, **kwargs)


    def set_ylabel(self, label, **kwargs):
        self.ax.ylabel(label, **kwargs)


    def set_title(self, title, **kwargs):
        self.ax.set_title(title, **kwargs)


    # See the following website for the allowed projection:
    # https://cartopy.readthedocs.io/stable/reference/projections.html'
    def __figureProjection(self):
        if (self.__proj is None):
            self.__proj = ccrs.PlateCarree(central_longitude=self.central_longitude)

        self.__crs  = ccrs.PlateCarree()


    # Not used
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
                                           draw_labels=False                         ,
                                           xformatter =LongitudeFormatter()         ,
                                           yformatter =LatitudeFormatter()          ,
                                          )
        self.gridlines.xlabel_style = {'size' : self.__gl_config['fontsize'],
                                       'color': self.__gl_config['color']   ,
                                      }
        self.gridlines.ylabel_style = {'size' : self.__gl_config['fontsize'],
                                       'color': self.__gl_config['color']   ,
                                      }

        self.gridlines.xlines = self.__gl_config['grid']    # Default : No grid lines
        self.gridlines.ylines = self.__gl_config['grid']    # Default : No grid lines

        self.gridlines.top_labels    = False
        self.gridlines.bottom_labels = False
        self.gridlines.right_labels  = False
        self.gridlines.left_labels   = False


    # Longitude to 0-360 coordinate
    def __lon_norm(self, lon):
        l0 = np.float64(lon[0])
        l1 = np.float64(lon[1])

        norm0 = l0 % 360.
        norm1 = l1 % 360.
        #print(f'DEBUG : lon[0]={lon[0]}, lon[1]={lon[1]} ---> norm0={norm0}, norm1={norm1}')

        return norm0, norm1


    # Estimate the central longitude
    # If this class has __proj or central_longitude, they are used for the result.
    # Otherwise, the result is estimated from longitude range (lonlim)
    def __set_clon(self):
        if (self.__proj is not None):
            self.central_longitude = self.__proj.proj4_params.get('lon_0', None)
        elif (self.central_longitude is None):
            l0 = np.float64(self.lonlim[0])
            l1 = np.float64(self.lonlim[1])

            if (l1 < l0):
                l1 = l1 + 360
            self.central_longitude = (l0 + l1) * 0.5
            #self.central_longitude = (self.lon[0] + self.lon[-1]) * 0.5

        self.edge_longitude = (self.central_longitude + 180) % 360


    # Set longitude range
    def __set_lon_core(self, lonlim):
        lonlim = self.__toList(lonlim)
        if (lonlim[0] is None):
            # Default : All area specified to the constructor
            if (self.edge_longitude is not None):
                # Avoiding the edge_longitude comming into the plot area
                begval = self.edge_longitude
                endval = begval + self.lon[-1]
            else:
                begval = self.lon[0]
                endval = self.lon[-1]

            lonlim = [begval,endval]
        elif (len(lonlim) != 2):
            raise TypeError(f'Invalid Longitude Range : {lonlim}. lonlim must be a list with 2 elements')

        vmin, vmax = self.__lon_norm(lonlim)
        if (vmin > vmax):
            vmax = vmax + 360
        
        self.lonlim = [vmin, vmax]


    def __set_lon_check(self):
        lmin = self.lonlim[0]
        lmax = self.lonlim[1]
        angle_to_lmax = (lmax - lmin) % 360
        angle_to_edge = (self.edge_longitude - lmin) % 360
        # Checking whether edge_longitude is not in the plot area
        if (angle_to_lmax > 360):
            valid = False        # NG
        elif (angle_to_lmax < angle_to_edge):
            valid = True         # OK
        elif ((self.edge_longitude - lmin) % 360 < 1.E-5):
            valid = True         # OK
        else:
            valid = False        # NG

        if (not valid):
            raise ValueError('Invalid longitude range: '
                             f'[{lmin}, {lmax}] with central_longitude={self.central_longitude} '
                             f'(edge_longitude={self.edge_longitude}). '
                             'The specified lonlim intersects the map seam (edge), which would split the plot. '
                             'Since central_longitude/edge_longitude are immutable after initialization, '
                             'recreate the instance with a different projection/central_longitude, '
                             'or adjust lonlim so it does not cross the edge. '
                             '\nNote: vmin>vmax is treated as a valid 360-degree spanning interval; values are not swapped. '
                            )


    def __set_lat_core(self, latlim=None):
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


    def __select_level(self, data):
        if (data.ndim == 1 or data.ndim > 3):
            raise ValueError(f'Invalid data shape for display(): expected 2D (lat, lon) or 3D (lev, lat, lon), got {data.shape}.')
        elif (data.ndim == 2):
            data_pass = data[:,:]
        elif (data.ndim == 3):
            data_pass = data[self.levidx,:,:]

        return data_pass


    # Set tick positions
    def __set_ticks(self, loc=None):
        if (loc is not None):
            return mticker.FixedLocator(loc)

        int_opt = [1, 2, 2.5, 3, 5, 6, 10]
        return mticker.MaxNLocator(nbins=7, steps=int_opt)


    # Convert to List
    def __toList(self, a):
        if (isinstance(a, np.ndarray)):
            return a.tolist()
        elif (isinstance(a, (list, tuple))):
            return list(a)
        else:
            return [a]


    # Round to 0, 0.5, or 1
    def __round5(self, value):
        base    = 10**self.__digit(value)
        step    = base * 0.5
        output  = step * np.floor(value/step + 0.5)
        return output


    # Get the order of value
    def __digit(self, value):
        err_fix = 1.E-12
        digit   = np.floor(np.log10(value) + err_fix)
        return int(digit)



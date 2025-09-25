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

        self.__xlabelLoc_setted = False
        self.__ylabelLoc_setted = False

        dummy, self.lon_cycle = add_cyclic_point(self.lon, coord=self.lon)
        self.mglon, self.mglat = np.meshgrid(self.lon_cycle, self.lat)

        self.__proj     = args['projection']
        self.__crs      = None
        self.central_longitude = args['central_longitude']  # Default center=180
        self.edge_longitude    = None
        
        if (self.central_longitude is not None or self.__proj is not None):
            self.__set_clon()                       #  Set self.central_longitude
            self.__set_lon_core(args['lonlim'])     # Set self.lonlim
        else:
            self.__set_lon_core(args['lonlim'])     # Set self.lonlim
            self.__set_clon()                       #  Set self.central_longitude
        self.__set_lon_check()
        self.__set_lat_core(args['latlim'])     # Set self.latlim
        self.set_lev(args['levlim'])    # Set self.levlim and self.levidx

        self.__figureProjection()       # Set projection
        self.projection = self.__proj.__class__.__name__

        self.method = 'contour'         # Default plot method as contour
        self.cmap   = 'bwr'             # Default color map as blue->white->red
        self.colors = None              # Default colors None

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

        self.fig   = fig
        self.ax    = self.fig.add_subplot(rows, lines, idx, projection=self.__proj)
        self.cont  = None       # None until contour plot
        self.shade = None       # None until shade plot
        self.ccbar = None       ## Color Bar for contour
        self.scbar = None       ## Color Bar for shade

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
        self.__gridlines_init()
        
        print(f'DEBUG : self.lonlim={self.lonlim}')
        self.ax.set_xticks(self.__set_ticks().tick_values(self.lonlim[0], self.lonlim[1]), crs=self.__crs)
        self.ax.set_yticks(self.__set_ticks().tick_values(self.latlim[0], self.latlim[1]), crs=self.__crs)


    def set_lon(self, lonlim=None):
        self.__set_lon_core(lonlim)
        check = self.__set_lon_check()
        if (not self.__xlabelLoc_setted):
            self.ax.xaxis.set_major_locator(mticker.NullLocator())
            self.ax.xaxis.set_major_formatter(mticker.NullFormatter())
            #self.ax.set_xticks([], crs=self.__crs)
            self.ax.set_xticks(self.__set_ticks().tick_values(self.lonlim[0], self.lonlim[1]), crs=self.__crs)


    def set_lat(self, latlim=None):
        self.__set_lat_core(latlim)
        if (not self.__ylabelLoc_setted):
            self.ax.yaxis.set_major_locator(mticker.NullLocator())
            self.ax.yaxis.set_major_formatter(mticker.NullFormatter())
            #self.ax.set_yticks([], crs=self.__crs)
            self.ax.set_yticks(self.__set_ticks().tick_values(self.latlim[0], self.latlim[1]), crs=self.__crs)


    def set_lev(self, levlim=None):
        if (levlim is None):
            # Default : lev[0]
            levlim = self.lev[0]
        
        self.levlim = levlim
        self.levidx = np.argmin(np.abs(self.lev - levlim))  # Index of the specified vertical level


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

        self.ax.xaxis.set_major_formatter(LongitudeFormatter())
        self.ax.yaxis.set_major_formatter(LatitudeFormatter())

        #lon_ticks = getattr(self.gridlines.xlocator, 'locs', None)
        #lat_ticks = getattr(self.gridlines.ylocator, 'locs', None)

        #print(f'DEBUG : lon_ticks={self.gridlines.xlocator}')
        #print(f'DEBUG : lat_ticks={lat_ticks}')
        #self.ax.tick_params(labelbottom=True, labelleft=True, labeltop=True, labelright=True)
        #self.ax.set_xticks(crs=self.__crs)


    def label_loc(self, which, location):
        which = which.lower()
        if (which == 'x' or which == 'lon'):
            self.gridlines.xlocator = mticker.FixedLocator(location)
            self.__xlabelLoc_setted = True
        elif (which == 'y' or which == 'lat'):
            self.gridlines.ylocator = mticker.FixedLocator(location)
            self.__ylabelLoc_setted = True
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
    # 'transform' argument cannot be changed
    def display(self, data, **kwargs):
        if (self.method == 'contour'):
            defaults = {'linestyles': 'solid'}
        elif (self.method == 'shaded'):
            defaults = {'extend': 'both'}
        #else:
            #print('DEBUG : Unexpected method')

        args = defaults.copy()
        if (self.cmap is not None):
            args['cmap'] = self.cmap

        if (self.colors is not None):
            args['colors'] = self.colors

        args.update(kwargs)

        args['transform'] = self.__crs
        # Limit the area to be plotted
        self.ax.set_extent(self.lonlim + self.latlim, crs=self.__crs)
        #print(f'DEBUG : self.ax.set_extent({self.lonlim + self.latlim}, crs=self.__crs)')



        if (data.ndim == 1 or data.ndim > 3):
            raise ValueError(f'Invalid data shape for display(): expected 2D (lat, lon) or 3D (lev, lat, lon), got {data.shape}.')
        elif (data.ndim == 2):
            data_pass = data[:,:]
        elif (data.ndim == 3):
            data_pass = data[self.levidx,:,:]
            #print('DEBUG : ', self.levidx)

        data_pass, dummy = add_cyclic_point(data_pass, coord=self.lon)
        
        # Plot
        if (self.method == 'contour'):
            self.__plot_contour(data_pass, **args)
        elif (self.method == 'shaded'):
            self.__plot_shaded(data_pass , **args)
        
        #print('DEBUG : ', data_pass[0,:])
        #self.ax.set_autoscale_on(False)


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
    def set_cbar(self, which=None, **kwargs):
        defaults = {'location': 'bottom', 'shrink': 0.9, 'aspect': 40, 'pad': 0.08}
        args     = defaults.copy()
        args.update(kwargs)
        if (('pad' not in kwargs) and (args['location']=='right' or args['location']=='left')):
            args['pad'] = 0.03

        if (which is None):
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


    # See the following website for the allowed projection:
    # https://cartopy.readthedocs.io/stable/reference/projections.html'
    def __figureProjection(self):
        if (self.__proj is None):
            self.__proj = ccrs.PlateCarree(central_longitude=self.central_longitude)

        #clon = self.__proj.proj4_params.get('lon_0', None)
        #self.central_longitude = clon
        #print('DEBUG : central_longitude=',clon)
        #if (clon is not None):
        #    self.__crs  = ccrs.PlateCarree(central_longitude=clon)
        #else:
        self.__crs  = ccrs.PlateCarree()


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

        self.gridlines.top_labels   = False
        self.gridlines.right_labels = False

        self.ax.xaxis.set_major_formatter(LongitudeFormatter())
        self.ax.yaxis.set_major_formatter(LatitudeFormatter())

        #lon_formatter = LongitudeFormatter()
        #lat_formatter = LatitudeFormatter()
        #self.ax.xaxis.set_major_formatter(lon_formatter)
        #self.ax.yaxis.set_major_formatter(lat_formatter)

        #self.ax.axes.tick_params()


    def __lon_norm(self, lon):
        l0 = np.float64(lon[0])
        l1 = np.float64(lon[1])

        #if (self.__proj is not None):
        #    self.central_longitude = self.__proj.proj4_params.get('lon_0', None)
        #elif (self.central_longitude is None):
        #    work_l0 = l0
        #    work_l1 = l1
        #    if (work_l1 < work_l0):
        #        work_l1 = work_l1 + 360
        #    self.central_longitude = (work_l0 + work_l1) * 0.5

        norm0 = l0 % 360.
        norm1 = l1 % 360.
        #print(f'DEBUG : lon[0]={lon[0]}, lon[1]={lon[1]} ---> norm0={norm0}, norm1={norm1}')

        return norm0, norm1


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


    def __set_lon_core(self, lonlim):
        lonlim = self.__toList(lonlim)
        if (lonlim[0] is None):
            # Default : All area specified to the constructor
            #begval = self.lon[0]
            #endval = self.lon[-1]
            begval = self.edge_longitude
            endval = begval + self.lon[-1]

            lonlim = [begval,endval]
        elif (len(lonlim) != 2):
            raise TypeError(f'Invalid Longitude Range : {lonlim}. lonlim must be a list with 2 elements')
        
        vmin, vmax = self.__lon_norm(lonlim)
        #print(f'DEBUG : central_longitude : {self.central_longitude}, edge_longitude: {self.edge_longitude}')
        if (vmin > vmax):
            #vmin = vmin - 360
            vmax = vmax + 360
        
        self.lonlim = [vmin, vmax]


    def __set_lon_check(self):
        lmin = self.lonlim[0]
        lmax = self.lonlim[1]
        angle_to_lmax = (lmax - lmin) % 360
        angle_to_edge = (self.edge_longitude - lmin) % 360
        if (angle_to_lmax > 360):
            valid = False        # NG
        elif (angle_to_lmax < angle_to_edge):
            valid = True         # OK
        elif (angle_to_edge - lmin < 1.E-5):
            valid = True
        else:
            valid = False        # NG
        
        #print(f'--DEBUG : longitude range : {lmin} to {lmax}')
        if (not valid):
            #print(f'--- DEBUG : Invalid longitude range : {lmin} to {lmax}. Change argument "central_longitude"')
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





# MAPPLOT

An interface to use cartopy efficiently

## Test Environment
- Python 3.12.11
- NumPy 2.2.6
- Matplotlib 3.10.6
- Cartopy 0.24.1
- Scipy 1.16.2


## Install
The source code can be installed from GitHub
```sh
$ git clone https://github.com/koseiohara/mapplot.git
$ cd mapplot
```
Modify the variable `INSTALL` in the Makefile.
The source file will be copied by `make install` command to the directory specified by `INSTALL`.
```sh
$ make inatall
```
Add that directory to the environment variables `PATH` and `PYTHONPATH`.


## Functions
- [maapplot](#init)
    - [set_lon](#set-lon)
    - [set_lat](#set-lat)
    - [set_lev](#set-lev)
    - [set_extent](#set-extent)
    - [set_label](#set-label)
    - [gxout](#gxout)
    - [display](#display)
    - [set_cbar](#set-cbar)
    - [set_vector_legend](#set-vector-legend)
    - [mark](#mark)
    - [text](#text)
    - [set_xlabel](#set-xlabel)
    - [set_ylabel](#set-ylabel)
    - [set_title](#set-title)


## mapplot<a id="init"></a>
Examples:
```python
import numpy             as np
import matplotlib.pyplot as plt
from mapplot import mapplot

lon = np.arange(  0.,     360., 1.25)
lat = np.arange(-90., 90.+1.25, 1.25)
fig = plt.figure()
mp  = mapplot(fig, posit=[1,1,1], lon=lon, lat=lat)
```
### Arguments
#### `fig`
Figure defined by
```python
fig = plt.figure()
```

#### `posit`
Position of the `Axes` in `fig`.
This parameter will be used for `fig.add_subpot()`.

#### `lon`
Longitudes of data.
Input the longitude of the entire dataset, not only the plotted area.

#### `lat`
Latitudes of data.
Input the Latitude of the entire dataset, not only the plotted area.

#### `kwargs`
In addition to the arguments explained above, this class can accept several keywords.
- `lev`  
Default : `0`  
Levels of data.
Input the levels of the entire dataset, not only the plotted area.
If data will be 2-dimensional, this argument will not be required.
- `lonlim`  
Default : `None`  
Longitudes of plotted area.
The input parameter should be a list with 2 elements: the first and second element is the western and eastern limit, respectively.
If the value of the first element has larger value than the second, the range will include the prime meridian.
For example, `lonlim=[330,30]` is the same as `lonlim=[-30,30]`.  
If this options is omitted, the longitude limit will ve the entire range of `lon`.
`lonlim` can be set using the function `set_lon`; however, if both arguments `central_longitude` and `projection` are omitted, specifying `lonlim` here allows `central_longitude` to be defined with a more appropriate value.
- `latlim`  
Default : `None`  
Latitudes of plotted area.
The input parameter should be a list with 2 elements: the first and second element is the southern and northern limit, respectively.
- `levlim`  
Default : `None`  
The level to be plotted.
If the argument `lev` does not include `levlim` value, the closest level will be chosen.
- `central_longitude`  
Default : `None`  
The central longitude to be able to be plotted.
The longitude range cannot include the longitude `central_longitude-180`.
- `projection`  
Default : `None`  
A projection function defined in `cartopy.crs`.
If omitted, `cartopy.crs.PlateCarree()` will be chosen with the `central_longitude` defined by the argument `central_longitude` or `lonlim`.
See the website of [Cartopy](https://cartopy.readthedocs.io/stable/reference/projections.html) for the acceptable functions.
- `resolution`  
Default : `"medium"`  
The resolution of the coastlines.
`"high"`/`"h"`/`"10m"`, `"medium"`/`"m"`/`"50m"`, and `"low"`/`"l"`/`"110m"` are acceptable.


## set_lon<a id="set-lon"></a>
This function allows us to change the longitude range to be plotted.
### Arguments
#### `lonlim`
Optional  
Default : `None`  
Range of the longitude to be plotted.
If omitted, the entire range of longitude will be chosen.

## set_lat<a id="set-lat"></a>
This function allows us to change the latitude range to be plotted.
### Arguments
#### `latlim`
Optional  
Default : `None`  
Range of the latitude to be plotted.
If omitted, the entire range of latitude will be chosen.

## set_lev<a id="set-lev"></a>
This function allows us to change the level to be plotted.
### Arguments
#### `levlim`
Optional  
Default : `None`  
Level to be plotted.
If omitted, the first index of `lev` will be chosen.

## set_extent<a id="set-extent"></a>
This function will explicitly limit the area using the value defined by the functions `set_lon` and `set_lat`.
Usually, this function need not be used because this is called in both `set_lon()` and `set_lat()`.
### Arguments
No arguments.

## set_label<a id="set-label"></a>
This function set the format and the positions of the x and y ticks.
### Arguments
#### `x`
Optional  
Default : `None`  
The location of x ticks.

#### `y`
Optional  
Default : `None`  
The location of y ticks.

#### `fontsize`
Optional  
Default : `10`  
The font size of x and y tick labels.

#### `fontcolor`
Optional  
Default : `black`  
The font color of x and y tick labels.

#### `grid`
Optional  
Default : `True`  
Grid lines on/off.

#### `linewidth`
Optional  
Default : `0.7`  
Width of grid lines.

#### `linestyle`
Optional  
Default : `":"`  
Style of grid lines.
See the website of [Matplotlib](https://matplotlib.org/stable/gallery/lines_bars_and_markers/linestyles.html?utm_source=chatgpt.com) for the detail of options.

#### `linecolor`
Default : `"grey"`  
Color of grid lines.

#### `alpha`
Optional  
Default : `0.7`  
Alpha value of grid lines.

## gxout<a id="gxout"></a>
Settings for the method of the next plotting.
### Arguments
#### `method`
The method of the next `display()`.
`"contour"`, `"shaded"`, `"hatches"`, or `"vector"`.

#### `cmap`
Optional  
Default : `None`  
Colormap.
If both `cmap` and `colors` areguments are `None`, `cmap="bwr"` is set.
`colors` argument has higher priority.

#### `colors`
Optional  
Default : `None`  
Colors of each level.
If both `cmap` and `colors` areguments are `None`, `cmap="bwr"` is set.
`colors` argument has higher priority.

## display<a id="display"></a>
Display a graph based on the settings provided to `gxout()`.
### Arguments
#### `data`
2- or 3-dimensional ndarray to be plotted.
Size of the first and second (if 3-dimensional, second and third) dimension must be equal to `lon` and `lat` provided to [mapplot](#mapplot).

#### `y`
Optional  
Default : `None`  
2- or 3-dimensional ndarray to be plotted.
Size of the first and second (if 3-dimensional, second and third) dimension must be equal to `lon` and `lat` provided to [mapplot](#mapplot).
Acceptable only when `method="vector"`.
y-component of the vector.

#### `kwargs`
In addition to the arguments explained above, this function can accept several keywords.
All arguments of Matplotlib's `contour`, `contourf`, `scatter`, and `quiver` functions are available for `method=``"contour"`/`"shaded"`/`"hatches"`/`"vector"`, respectively.  
Some keywords have default values.
- `contour`
    - `linestyles="solid"`
- `shaded`
    - `extend="both"`
- `hatches`
    - `size=0.3` : same as `s` option of `scatter`  
    - `color="black"` : same as `c` option of `scatter`  
    - `marker="."`  
    In addition to these arguments, density of dots can be set by `interval` options:
    - `interval`  
    Optional  
    Default : `3`  
- `vector`
    - `angles="xy"`
    - `scale_units="xy"`
    - `color="black"`
    - `width=0.003`
    - `headlength=2`
    - `headwidth=2`
    - `regrid_shape=30`

## set_cbar<a id="set-cbar"></a>
Insert a colorbar.
### Arguments
#### `which`
Optional  
Default : `None`  
`"shaded"` or `"contour"`.
If omitted, a colorbar will be added to whichever plot exists among `contour` and `shaded`.
If both of them exist, `shaded` has higher priority.

#### `kwargs`
In addition to the argument explained above, this function can accept several keywords.
All arguments of Matplotlib's `colorbar` functions are available.  
Some keywords have default values.
- `location="bottom"`
- `shrink=0.9`
- `aspect=40`
- `pad=0.08` if `location="bottom"` and `pad=0.03` if `location="right"` or `location="left"`

## set_vector_legent<a id="set-vector-legend"></a>
Insert a legend of vector.
### Arguments
#### `X`
X-position of the legend.

#### `Y`
Y-position of the legend.

#### `U`
Optional  
Default : `None`  
The length of the key.
If omitted, rounded value of the 80 percentile of vector length is used.

#### `labelpos`
Optional  
Default : `"S"`
Position of the label.
`"N"`, `"S"`, `"E"`, `"W"` for Above, below, right, left, respectively.

#### `label`
Optional  
Default : `None`  
The key label.
If omitted, the value of `U` is shown.

#### `direction`
Optional  
Default : `"x"`  
The direction of the key.
The key points to the right if `direction="x"` and to the top if `direction="y"`

#### `coordinate`
Optional  
Default : `"axes"`  
Unit of `X` and `Y` arguments.
`"axes"`, `"figure"`, `"data"`, or `"inches"`.
See the website of [Matplotlib](https://matplotlib.org/stable/api/_as_gen/matplotlib.quiver.QuiverKey.html) for the detail.

#### `kwargs`
In addition to the argument explained above, this function can accept several keywords.
All arguments of Matplotlib's `quiverkey` functions are available.  

## mark<a id="mark"></a>
Insert (a) dot(s) to the map.
### Arguments
#### `x`
Longitude at where a dot will be inserted.

#### `y`
Latitude at where a dot will be inserted.

#### `kwargs`
In addition to the argument explained above, this function can accept several keywords.
All arguments of Matplotlib's `scatter` functions are available.  
Some keywords have default values.
- `marker="o"`
- `c="black"`
- `linewidth=0`

## text<a id="text"></a>
Insert a string to the map.
### Arguments
#### `x`
Longitude at where a string will be inserted.

#### `y`
Latitude at where a string will be inserted.

#### `s`
String.

#### `coord`
Optional  
Default : `"latlon"`
Coordinate of `x` and `y` arguments.
`"latlon"`/`"ll"`, `"ax"`, or `"fig"`.

#### `kwargs`
In addition to the argument explained above, this function can accept several keywords.
All arguments of Matplotlib's `text` functions are available.  

## set_xlabel<a id="set-xlabel"></a>
A wrapper function of `matplotlib.axes.Axes.set_xlabel`
The usage is completely the same.

## set_ylabel<a id="set-ylabel"></a>
A wrapper function of `matplotlib.axes.Axes.set_ylabel`
The usage is completely the same.

## set_title<a id="set-title"></a>
A wrapper function of `matplotlib.axes.Axes.set_title`
The usage is completely the same.



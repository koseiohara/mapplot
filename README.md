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
- `resolution`  
Default : `"medium"`  
The resolution of the coastlines.
`"high"`/`"h"`/`"10m"`, `"medium"`/`"m"`/`"50m"`, and `"low"`/`"l"`/`"110m"` are acceptable.


## set_lon<a id="set-lon"></a>
This function allows us to change the longitude range to be plotted.
### Arguments
#### `lonlim`
Default : `None`  
Range of the longitude to be plotted.
If omitted, the entire range of longitude will be chosen.

## set_lat<a id="set-lat"></a>
This function allows us to change the latitude range to be plotted.
### Arguments
#### `latlim`
Default : `None`  
Range of the latitude to be plotted.
If omitted, the entire range of latitude will be chosen.

## set_lev<a id="set-lev"></a>
This function allows us to change the level to be plotted.
### Arguments
#### `levlim`
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



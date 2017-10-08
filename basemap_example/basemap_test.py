from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import *

# set filename below
rootGroup = Dataset('example_file.nc', 'r', format = "NETCDF4")
       
# create new figure
fig=plt.figure()

lons = rootGroup.variables['longitude']
lats = rootGroup.variables['latitude']
Z = rootGroup.variables['tas_0'][1000, :, :]

# setup of mollweide basemap
m = Basemap(projection='lcc',llcrnrlat=np.min(lats),urcrnrlat=np.max(lats),\
            llcrnrlon=np.min(lons),urcrnrlon=np.max(lons),resolution='l', lat_0 = lats[:].mean(), lon_0 = lons[:].mean())

lons, lats = np.meshgrid(lons, lats)

# make a filled contour plot.
result = m.contourf(lons, lats, Z, 15, linewidths=0.5, latlon=True, cmap=plt.cm.RdBu_r)
m.colorbar(result) # draw colorbar

# draw coastlines and political boundaries.
m.drawcoastlines()
m.drawcountries()

# draw parallels and meridians.
parallels = np.arange(-90.,90,10.)
m.drawparallels(parallels,labels=[1,0,0,0])
meridians = np.arange(-180.,180.,10.)
m.drawmeridians(meridians,labels=[0,0,0,1])

plt.show()

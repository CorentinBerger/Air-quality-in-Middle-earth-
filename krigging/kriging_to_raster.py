# -*- coding: utf-8 -*-
"""
Created on Tue Oct  3 15:10:07 2023

@author: Corentin BERGER
"""
import numpy as np
import pandas as pd
from pykrige.uk import UniversalKriging
from pykrige.ok import OrdinaryKriging
from scipy.ndimage import gaussian_filter
from scipy.interpolate import griddata
from osgeo import gdal, osr

# Choosing the pollutant : C_PM10, C_PM2.5, C_SO2 and C_NO2

value = "C_SO2"

#Dataframe preparation

df_grid = pd.read_csv("poll_grid.csv", usecols=["X","Y",value], sep=";", decimal=",")

df_vulcain = pd.read_csv("poll_vulcain.csv", usecols=["X","Y",value], sep=";", decimal=",")

df_city = pd.read_csv("poll_city.csv", usecols=["X","Y",value], sep=";", decimal=",")


df_grid[value] += np.random.normal(0, df_grid[value].std() * 0.2, size=len(df_grid))

df_grid = pd.concat([df_city, df_vulcain, df_grid])
#df_grid[valeur] = gaussian_filter(df_grid[valeur], sigma=0.5)

df_city = pd.concat([df_city,df_vulcain])


print("preparation: ok")

#Grid preparation

n=400

grid_y = np.linspace(df_grid["Y"].min(), df_grid["Y"].max(), n)
grid_x = np.linspace(df_grid["X"].min(), df_grid["X"].max(), n)

print("grid: ok")

# Kriging : Ordinary Kriging and Universal Kriging

OK_grid = OrdinaryKriging(df_grid["X"], df_grid["Y"], df_grid[value], variogram_model="exponential")
UK_city = UniversalKriging(df_city["X"], df_city["Y"], df_city[value], variogram_model="linear", drift_terms=["regional_linear"])

xintrp, yintrp = np.meshgrid(grid_x, grid_y)

df_out = pd.DataFrame()
df_out["X"] = xintrp.ravel()
df_out["Y"] = yintrp.ravel()

# Interpolation

z_grid, ss_grid = OK_grid.execute("points", df_out["X"], df_out["Y"])
z_city, ss_city = UK_city.execute("points", df_out["X"], df_out["Y"])

# Mean of the two results (grid and city) to obtain the final result

df_out[value] = 0.25 * z_grid.ravel() + 0.75 * z_city.ravel()

df_out = pd.concat([df_out,df_vulcain])


print("kriging: ok")

# Output to csv

df_out.to_csv("output_kriging_gaussian.csv", index=False)

print("csv: ok")

# Define a regular grid for the raster map

xi = np.linspace(min(df_out["X"]), max(df_out["X"]), 2000)
yi = np.linspace(min(df_out["Y"]), max(df_out["Y"]), 2000)
xi, yi = np.meshgrid(xi, yi)

# Interpolation

zi = griddata((df_out["X"], df_out["Y"]), df_out[value], (xi, yi), method='linear')

# Define geospatial information

xmin, ymin = min(df_out["X"]), min(df_out["Y"])
xmax, ymax = max(df_out["X"]), max(df_out["Y"])

# X and Y resolution
xres = (xmax - xmin) / len(xi[0])
yres = (ymax - ymin) / len(yi)

# Geotransform for EPSG:32631 (UTM Zone 31N)
geotransform = (xmin, xres, 0, ymin, 0, yres)

# TIFF file creation
driver = gdal.GetDriverByName('GTiff')
output_file = "map_"+value+"_lotr.tif"
dst_ds = driver.Create(output_file, len(xi[0]), len(yi), 1, gdal.GDT_Float32)
dst_ds.SetGeoTransform(geotransform)

# Set projection to EPSG:32631 (UTM Zone 31N)

srs = osr.SpatialReference()
srs.ImportFromEPSG(32631)  
dst_ds.SetProjection(srs.ExportToWkt())

# Save data to raster file
dst_ds.GetRasterBand(1).WriteArray(zi)
dst_ds = None

print("The raster file has been successfully saved under", output_file)


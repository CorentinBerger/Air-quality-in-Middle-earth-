# Air-quality-in-Middle-earth-
To rasterize SO2, NO2, PM10 and PM2.5 annual concentrations in Middle-earth in J.R.R. Tolkien's universe.

The rasters created correspond to the projections and coordinates of [the Arda Project: Maps of Middle-earth by J.R.R. Tolkien, using a DEM (digital elevation model) and place-name vectors](https://github.com/bburns/Arda).

Concentration kriging and rasterization of the kriged grid is performed with kriging_to_raster.py.

The kriging is done with the following files:
- poll_city.csv which corresponds to the concentrations of the main cities/cities of Middle Earth, 
- poll_vulcain.csv which corresponds to the concentrations of the main volcanoes,
- poll_grid.csv which is a grid of points with regional concentrations.
 
These three files are created in concentration_calculation_lotr.xlsx based on regional concentrations (determined by Chat GPT 4) according to region description, climate, temperature, precipitation and wind. Cities and citadels concentrations are determined by number of inhabitants, surface area and people (elves, men, orcs, dwarves...).

The rasters created by kriging_to_raster.py are in TIFF format and can be opened by GIS software (QGIS and ArcGIS). Maps of SO2 and PM10 concentrations created in QGIS can be found in the map directory.

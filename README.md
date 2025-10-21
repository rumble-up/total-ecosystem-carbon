# Total Ecosystem Carbon Pipeline for Summarizing by County

This repository contains a reproducible Python pipeline that summarizes the National Forest Carbon Monitoring System "Total Ecosystem Carbon" raster by US counties in Michigan, Wisconsin, Minnesota and writes the results to an sqlite database.

Sqlite is not the best choice for a GIS database, PostGres with PostGIS would have been better. However, the purpose of this exercise was to build something simple and quick that another person could easily run locally.  Sqlite is nice for this because it is already included in Python.


Contents
- `data/inputs/` — place the raster and county shapefile here (not included in this repo)

Quick start
1. Place the raster `NLS_TotalEcosystemCarbon2020.tif` inside `data/inputs/` 
2. [next step]


Notes & assumptions
- Units: [explain]

Next steps / improvements
- Add unit tests 



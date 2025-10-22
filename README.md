# Total Ecosystem Carbon Pipeline for Summarizing by County

This repository contains a reproducible Python pipeline that summarizes the National Forest Carbon Monitoring System (NFCMS)"Total Ecosystem Carbon" by county and writes the results to a database.  

The input datasets for this demonstration are located here:
* [Zip file of NFCMS raster carbon data](https://usfs-public.box.com/shared/static/v861gwms9fq68sitl0r3vs2v3moxeu9x.zip)
* [US Census County administrative boundaries](https://catalog.data.gov/dataset/2024-cartographic-boundary-file-kml-county-and-equivalent-for-united-states-1-500000)



## Project Structure

```
total-ecosystem-carbon/
├── data/
│   ├── inputs/               # Input data files
│   │   ├── NLS_TotalEcosystemCarbon2020.tif
│   │   └── US_census_counties/ #Shapefile of US 2024 administrative county polygons 
│   └── outputs/              # Generated output files, for now the processed database is stored here
├── *.ipynb                   # Jupyter notebooks for exploration and examples
├── carbon_stats.py          # Main processing module
└── requirements.txt         # Python package dependencies
```

## Quick Start

1. Clone the repository to your local computer:
```bash
git clone https://github.com/rumble-up/total-ecosystem-carbon.git
cd total-ecosystem-carbon
```

2. Create a Python virtual environment and activate it:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Download the raster input data:
   - [Zip file of NFCMS raster carbon data](https://usfs-public.box.com/shared/static/v861gwms9fq68sitl0r3vs2v3moxeu9x.zip) - Because the raster is large, you will need to download the zipfile separately. You only need one raster from the zip for this demo. It's located here inside the zipfile:  
  RDS-2025-0019_Data_NLS/Data/NLS/NLS_TotalEcosystemCarbon2020.tif
   - Put `NLS_TotalEcosystemCarbon2020.tif` in `data/inputs/` in your local repo directory

5. Run the pipeline using either:
   - The Python module:
     ```python
     from carbon_stats import CarbonStats

     cs = CarbonStats(
         raster_file="data/inputs/NLS_TotalEcosystemCarbon2020.tif",
         boundary_file="data/inputs/US_census_counties/cb_2024_us_county_500k.shp"
     )
     cs.read_raster()
     cs.process_boundaries(['Michigan', 'Wisconsin', 'Minnesota'])
     cs.calculate_stats()
     cs.export_to_sqlite("data/outputs/county_carbon.sqlite")
     ```
   - Or explore using the Jupyter notebook:
     - `A. Quick Start and SQL Query Examples.ipynb`

## Output Database Schema

The SQLite database contains a single table `county_carbon` with the following columns:

- `geoid`: County GEOID (unique identifier)
- `county_name`: Name of the county
- `state_name`: Name of the state
- `total_Tg_CO2e`: Total carbon within the county in Teragrams CO2 equivalent
- `average_Mg_CO2e_per_acre`: Average carbon per acre in Megagrams CO2 equivalent (metric tons CO2e)
- `county_area_acres`: County area in acres
- `geometry_wkt_EPSG_4326`: County boundary geometry in WKT format (EPSG:4326)

## Future Improvements

- **Change SQLite for PostGres with PostGIS** - SQLite is not the best choice for a GIS database, PostGres with PostGIS would have been better. However, the purpose of this exercise was to build something simple and quick that another person could easily run locally. SQLite is nice for this because it is already included in Python.  

- **Make the pipeline flexible for adding new raster data to the database** - The NCFMS dataset has multiple interesting rasters.  It would be great if a user could select a new raster, and add the data to the database. As long as the rasters are carbon data recorded in the same units, this should be possible.  The database could have two tables:
    1. `county_info` table with county specific information, for example, these columns:
        - `geoid`: County GEOID (unique identifier)
        - `county_name`: Name of the county
        - `state_name`: Name of the state
        - `county_area_acres`: County area in acres
        - `geometry_wkt_EPSG_4326`: County boundary geometry in WKT format (EPSG:4326)  
          
    2. `carbon_data` table with raster statistics within each county.  This table would have a long, melted format to facilitate adding more raster data on the fly to the same database structure.  For example, columns like these:
        - `geoid`: County GEOID (unique identifier)
        - `year`: NCFMS dataset has 2020 data and then 2050 and 2070 projections
        - `raster_type`: The type of raster summarized, for example AbovegroundBiomass, LiveBiomass, SoilCarbon
        - `total_Tg_CO2e`: Total carbon within the county in Teragrams CO2 equivalent
        - `average_Mg_CO2e_per_acre`: Average carbon per acre in Megagrams CO2 equivalent (metric tons CO2e)  
     
- **Add unit tests and input data validation** - These tests are important to systematically check that the pipeline is working as intended. 



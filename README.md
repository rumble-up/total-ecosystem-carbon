# Pipeline to Summarize Total Ecosystem Carbon by County

This repository contains a reproducible Python pipeline that totals the National Forest Carbon Monitoring System (NFCMS) "Total Ecosystem Carbon" from 2020 by county and writes the results to a simple database.  

The input datasets for this demonstration are from the following sources:
* [Zip file of NFCMS raster carbon data](https://usfs-public.box.com/shared/static/v861gwms9fq68sitl0r3vs2v3moxeu9x.zip)
* [US Census County administrative boundaries](https://catalog.data.gov/dataset/2024-cartographic-boundary-file-kml-county-and-equivalent-for-united-states-1-500000)

The area of focus is the Northern Lake States (NLS): Michigan, Minnesota, Wisconsin. Below is a visualization of the NFCMS original raster for Total Ecosystem Carbon in 2020.  
  
Each pixel in the image represents a 30m x 30m square which is over 282 million pixels of data in this raster!  
<img width="650"  alt="Original raster visualization" src="https://github.com/user-attachments/assets/df96d603-130a-442f-8d21-28b49eaa2664" />

This pipeline condenses the information to a database with a single total for each county, which is visualized below.  
The output database has 242 rows of vector data, one for each county. That's quite a big change from 282 million datapoints to 242.  
This transformation from raster data to a smaller vector dataset helps make the dataset faster, easier, and lighter to work with for information at the county level.  
<img width="650"  alt="Output totals per county visualization" src="https://github.com/user-attachments/assets/f27605a6-b01d-49b3-b0af-1d334ff840ae" />




## Project Structure

```
total-ecosystem-carbon/
├── data/
│   ├── inputs/                         # Input data files
│   │   ├── NLS_TotalEcosystemCarbon2020.tif
│   │   └── US_census_counties/         #Shapefile of US 2024 administrative county polygons 
│   └── outputs/                        # Generated output files, for now the processed database is stored here
├── A. Quick Start...ipynb              # Jupyter notebooks with examples for running the pipeline
├── B. Initial Exploration...ipynb      # My original assumptions and process behind building the pipeline
├── carbon_stats.py                     # Main processing module, where the pipeline code is
└── requirements.txt                    # Python package dependencies
```

## Output Database Schema

The final SQLite database contains a single table `county_carbon` with the following columns:

- `geoid`: County GEOID (unique identifier)
- `county_name`: Name of the county
- `state_name`: Name of the state
- `total_Tg_CO2e`: Total carbon within the county in Teragrams CO2 equivalent (million metric tons CO2e)
- `average_Mg_CO2e_per_acre`: Average carbon per acre in Megagrams CO2 equivalent (metric tons CO2e)
- `county_area_acres`: County area in acres
- `geometry_wkt_EPSG_4326`: County boundary geometry in WKT format (EPSG:4326)

Here is a screenshot of example data it contains:  
<img width="1039" height="213" alt="image" src="https://github.com/user-attachments/assets/81e7da2d-b53e-4f02-b866-dfff64f8b73a" />

## Quick Start

### Querying the database
- If you would like to jump straight to the final results, the final database is already stored in this repo. You can download it directly from the repo here: [county_carbon.sqlite](https://github.com/rumble-up/total-ecosystem-carbon/blob/main/data/outputs/county_carbon.sqlite)
- You can use your own database tools to query with SQL.  For example, to query all columns for Minnesota counties with more than 50 Tg CO2e, and order from lowest to highest total_Tg_CO2e, you could use
     ```SQL
      SELECT *
      FROM county_carbon
      WHERE state_name = 'Minnesota'
        AND total_Tg_CO2e > 50
      ORDER BY total_Tg_CO2e;
     ```


### Replicating the pipeline locally
If you wish to replicate and run the whole pipeline locally, please follow these steps:  
  
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

5. You have 3 options to run the pipeline.
   1. You can run it with the default values in your virtual environment from a command line with 
    ```bash
    $ python carbon_stats.py
    ```
   2. You can run the pipeline within other python code by importing the carbon_stats module:
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
   3. You can use the pipeline within a Jupyter notebook. Check out the notebook in this repository for an example of using the pipeline, or loading the SQLite database back into a pandas dataframe.
     - `A. Quick Start and SQL Query Examples.ipynb`
  
6. Query the database
     - You can query the database with the example in `A. Quick Start and SQL Query Examples.ipynb`
     - Or use your own database tools to query with SQL.  For example, to query all columns for Minnesota counties with more than 50 Tg CO2e, and order from lowest to highest total_Tg_CO2e, you could use
     ```SQL
      SELECT *
      FROM county_carbon
      WHERE state_name = 'Minnesota'
        AND total_Tg_CO2e > 50
      ORDER BY total_Tg_CO2e;
     ```




## Future Improvements
Here are some of the next steps to improve this pipeline.

1. **Change SQLite for PostGres with PostGIS** - SQLite is not the best choice for a GIS database, PostGres with PostGIS would have been better for working with geospatial data and queries. However, the purpose of this exercise was to build something simple and quick that another person could easily run locally. SQLite is nice for this because it is already included in Python and is easy to share with others.

2. **Improve speed by using a different raster processing library** - I learned through this project that `raster_stats.zonal_statistics` is fairly slow in processing large rasters.  If processing speed is important, then I would look at other alternatives for improving the speed of the calculations, such as `rioxarray`. 
  
2. **Make the pipeline flexible for adding new raster data to the database** - The NCFMS dataset has multiple interesting rasters.  It would be great if a user could select a new raster, and add the data to the database. As long as the rasters are carbon data recorded in the same units, this should be possible.  The database could have two tables:
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
     
3. **Add unit tests and input data validation** - These tests are important to systematically check that the pipeline is working as intended. 



import geopandas as gpd
import pandas as pd
from rasterstats import zonal_stats
import rasterio
import os
import sqlite3

class CarbonStats:
    # Constants
    SQ_M_IN_ACRE = 4046.86
    SQ_M_IN_SQ_MILE = 2589988.11
    # each pixel is 30m x 30m = 900 sq meters
    PIXEL_AREA_ADJUST = 900 / SQ_M_IN_ACRE

    def __init__(self, raster_file, boundary_file, raster_nodata=65535, export_crs="EPSG:4326"):
        self.raster_file = raster_file
        self.boundary_file = boundary_file
        self.raster_nodata = raster_nodata
        self.export_crs = export_crs
        self.raster_crs = None
        self.gdf = None

    def read_raster(self):
        """Read raster file and get CRS"""
        with rasterio.open(self.raster_file) as src:
            self.raster_crs = src.crs.to_string()
        return self.raster_crs

    def process_boundaries(self, state_filter=None):
        """Load and process boundary file, optionally filtering by state names"""
        # Load polygon boundaries
        self.gdf = gpd.read_file(self.boundary_file)
        
        # Apply state filter if provided
        if state_filter:
            if isinstance(state_filter, str):
                state_filter = [state_filter]
            mask = self.gdf['STATE_NAME'].isin(state_filter)
            self.gdf = self.gdf[mask]

        # Project to match raster CRS
        if not self.raster_crs:
            self.read_raster()
        self.gdf = self.gdf.to_crs(self.raster_crs)
        
        return self.gdf

    def calculate_stats(self):
        """Calculate carbon statistics for each county"""
        if self.gdf is None:
            raise ValueError("No boundary data loaded. Call process_boundaries first.")

        # Calculate zonal statistics
        stats = zonal_stats(self.gdf, self.raster_file, stats=["sum"], nodata=self.raster_nodata)
        self.gdf["raster_sum"] = [s["sum"] for s in stats]

        # Calculate derived statistics
        self.gdf['Mg_CO2e'] = self.gdf['raster_sum'] * self.PIXEL_AREA_ADJUST
        self.gdf['Tg_CO2e'] = self.gdf['Mg_CO2e'] / 1e6  # convert from Mg to Tg
        self.gdf['county_area_sq_miles'] = self.gdf.geometry.area / self.SQ_M_IN_SQ_MILE
        self.gdf['county_area_acres'] = self.gdf.geometry.area / self.SQ_M_IN_ACRE
        self.gdf['average_Mg_CO2e_per_acre'] = self.gdf['Mg_CO2e'] / self.gdf['county_area_acres']

        return self.gdf

    def prepare_for_export(self):
        """Prepare data for SQLite export"""
        # Select and rename columns
        keep_cols = ['GEOID', 'NAME', 'STATE_NAME', 'Tg_CO2e', 
                    'average_Mg_CO2e_per_acre', 'county_area_acres', 'geometry']
        gdf_for_sql = self.gdf[keep_cols].to_crs(self.export_crs)

        # Convert to database-friendly format
        df = gdf_for_sql.drop(columns="geometry").copy()
        geom_column_name = f"geometry_wkt_{self.export_crs.replace(':', '_')}"
        df[geom_column_name] = gdf_for_sql.geometry.to_wkt()

        # Rename columns to be more database-friendly
        rename_cols = {
            'GEOID': 'geoid',
            'NAME': 'county_name',
            'STATE_NAME': 'state_name',
            'Tg_CO2e': 'total_Tg_CO2e'
        }
        df = df.rename(columns=rename_cols)

        return df

    def export_to_sqlite(self, output_path, table_name="county_carbon"):
        """Export the processed data to SQLite database"""
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Prepare data for export
        df = self.prepare_for_export()

        # Write to SQLite
        conn = sqlite3.connect(output_path)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        conn.close()
        print('Successfully exported to', output_path)
        return output_path

def main():
    # Example usage
    raster_file = "data/inputs/NLS_TotalEcosystemCarbon2020.tif"
    boundary_file = "data/inputs/US_census_counties/cb_2024_us_county_500k.shp"
    output_db = "data/outputs/county_carbon.sqlite"

    # Initialize and run the pipeline
    cs = CarbonStats(raster_file, boundary_file)
    cs.read_raster()
    cs.process_boundaries(['Michigan', 'Wisconsin', 'Minnesota'])
    cs.calculate_stats()
    cs.export_to_sqlite(output_db)

if __name__ == "__main__":
    main()
from flask import Blueprint, jsonify, request
from create_database.models import create_database, Trip, DimDate, DimRegion, DimDatasource
from etl_process.etl_process import read_file, create_trip_df, create_store_region_table, create_store_date_table, create_store_datasource_table, store_notify_df

# Create blueprint to be modular
ingestion_bp = Blueprint('ingestion_bp', __name__)

# Create route for api
@ingestion_bp.route('/ingest-data', methods=['POST'])
def data_ingestion():
    
    # Get parameters from api
    chunksize = int(request.args.get('chunk_size'))
    # Declare file_name, database
    file_name = "data_source/trips.csv"
    database_name = "database.db"
    
    try:
        # Call create_database
        create_database(database_name) 

        # Call methods to store the data in the corresponding tables
        df = read_file(file_name)
        df = create_store_region_table(df,database_name=database_name, model=DimRegion)
        df = create_store_datasource_table(df,database_name=database_name, model=DimDatasource)
        df = create_trip_df(df)
        create_store_date_table(df,database_name=database_name, model=DimDate)

        return store_notify_df(df, 'trip', chunk_size = chunksize, database_name=database_name, model=Trip)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400
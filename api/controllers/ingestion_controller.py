from flask import Blueprint
from create_database.models import create_database, Trip, DimDate, DimRegion
from etl_process.etl_process import read_file, create_trip_df, create_store_region_df, create_store_date_df, store_notify_df

ingestion_bp = Blueprint('ingestion_bp', __name__)

@ingestion_bp.route('/ingest-data', methods=['POST'])
def data_ingestion():
    file_name = "data_source/trips.csv"
    database_name = "database.db"
    
    create_database(database_name) 
    df = read_file(file_name)
    
    df = create_trip_df(df)
    
    create_store_region_df(df=df, database_name=database_name, model=DimRegion)
    create_store_date_df(df=df, database_name=database_name, model=DimDate)

    return store_notify_df(df, 'trip', chunk_size = 10, database_name=database_name, model=Trip)
    
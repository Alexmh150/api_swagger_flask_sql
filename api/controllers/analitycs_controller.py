from flask import Blueprint, jsonify, request
from create_database.models import create_database, Trip, DimDate
from datetime import datetime
from sqlalchemy import create_engine, func, text
from sqlalchemy.orm import sessionmaker
import json

analitycs_bp = Blueprint('analitycs_bp', __name__)

database_name = "database.db"
engine = create_engine(f'sqlite:///{database_name}')
Session = sessionmaker(bind=engine)

@analitycs_bp.route('//most-common-region', methods=['GET'])
def most_common_region():
    
    try:
        # Extract query parameters from the request URL
        week_number = request.args.get('week')

        # Query the database to join trips with dim_date and group by week and region
        session = Session()

        subquery_count = session.query(
            Trip.region_name,
            func.count(1).label('count'),
            func.avg(1).label('avg')
            #(func.count(1) / 7).label('avg')
        ).join(
            DimDate,
            func.substr(DimDate.date, 1, 10) == func.substr(Trip.datetime, 1, 10)
        ).filter(DimDate.week_number == week_number).group_by(Trip.region_name).subquery()

        result = session.query(subquery_count.c.region_name, subquery_count.c.count, subquery_count.c.avg).order_by(subquery_count.c.count.desc()).first()
        session.close()

        query_trips = text("""select b.* from dim_date a inner join trip b on substr(a.date,1,10) = substr(b.datetime,1,10) where a.week_number = 21 and b.region_name = '"""+result.region_name+"';")
        
        # Connect to the database and execute the query
        with engine.connect() as connection:
            result_trips = connection.execute(query_trips).fetchall()        

        trips = []
        for row in result_trips:
            trip_data = {
                "trip_id": row.trip_id,
                "region_name": row.region_name,
                "origin_coord": row.origin_coord,
                "destination_coord": row.destination_coord,
                "datetime": row.datetime,
                "datasource": row.datasource
            } 
            trips.append(trip_data)

        res = {
            "region_name": result.region_name,
            "count": result.count,
            "average": result.avg,
            "trips": trips
        }
        # Process the result to get the most common region by week
        return jsonify(res), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
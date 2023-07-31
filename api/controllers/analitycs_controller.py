from flask import Blueprint, jsonify, request
from create_database.models import Trip, DimDate, DimRegion
from sqlalchemy import create_engine, func, text
from sqlalchemy.orm import sessionmaker

# Create Blueprint to be modular
analitycs_bp = Blueprint('analitycs_bp', __name__)

# Declare database to enable session
database_name = "database.db"
engine = create_engine(f'sqlite:///{database_name}')
Session = sessionmaker(bind=engine)

# Declare route for api
@analitycs_bp.route('/most-common-region', methods=['GET'])
def most_common_region():
    
    try:
        # Extract parameters
        week_number = request.args.get('week_number')

        # Establish connection to sql
        session = Session()

        # Declare sql statement
        query = session.query(DimRegion.region_name, func.count(1).label('count'), func.avg(1).label('avg')).\
                    join(Trip, Trip.region_id == DimRegion.region_id).\
                    join(DimDate, func.substr(Trip.datetime, 1, 10) == func.substr(DimDate.date, 1, 10)).\
                    group_by(DimRegion.region_name).\
                    order_by(func.count(1).desc())
        
        # validate if week_number has value to change the sql statement
        if week_number is not None:
            query = session.query(DimRegion.region_name, func.count(1).label('count'), func.avg(1).label('avg')).\
                    join(Trip, Trip.region_id == DimRegion.region_id).\
                    join(DimDate, func.substr(Trip.datetime, 1, 10) == func.substr(DimDate.date, 1, 10)).\
                    filter(DimDate.week_number == week_number).\
                    group_by(DimRegion.region_name)
        
        results = query.all()

        # Build the response
        most_common_regions = []
        for result in results[:2]:
            common_region = {
                "region_name": result.region_name,
                "num_trips": result.count,
                "average_trips": result.avg,
                "last_trip": get_last_trip_by_region(result.region_name, week_number=week_number)
            }
            most_common_regions.append(common_region)

        session.close() 

        return jsonify(most_common_regions), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
# Declare route for api
@analitycs_bp.route('/regions/<string:datasource_name>', methods=['GET'])
def get_regions_by_datasource(datasource_name):
    try:
        session = Session()

        # Declare sql statement directly
        query = text(f"""select
                     distinct 
                    c.* from trip a
                    inner join dim_region c on a.region_id = c.region_id
                    inner join dim_datasource b on a.datasource_id = b.datasource_id
                    where b.datasource_name = '{datasource_name}'
                                     """)
        
        # Retrieve the data
        with engine.connect() as connection:
            results = connection.execute(query).all()

        # Build response
        regions = []
        for result in results:
            region = {
                "region_id":result.region_id,
                "region_name":result.region_name,
                "region_population":result.region_population
            }
            regions.append(region)
        
        session.close()

        return jsonify(regions), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Retrieve last trip data for region_name
def get_last_trip_by_region(region_name, week_number=None):

    session = Session()

    # Declare query statement
    last_trip = text(f"""select a.*, c.region_name as region_name, d.datasource_name as datasource_name
                    from trip a
                    inner join dim_region c on a.region_id = c.region_id
                    inner join dim_datasource d on a.datasource_id = d.datasource_id
                    where c.region_name = '{region_name}'
                    order by a.datetime desc limit 1""")
    
    # Change query statement if week_numbe has value
    if week_number is not None:
        last_trip = text(f"""select a.*, c.region_name as region_name, d.datasource_name as datasource_name
                    from trip a
                    inner join dim_region c on a.region_id = c.region_id
                    inner join dim_datasource d on a.datasource_id = d.datasource_id
                    inner join dim_date b on substr(a.datetime,1,10) = substr(b.date,1,10)
                    where c.region_name = '{region_name}' and b.week_number = {week_number}
                    order by a.datetime desc limit 1""")
        
    # Execute query
    with engine.connect() as connection:
        result_trip = connection.execute(last_trip).first() 
    
    # Build trip
    trip_data = {
        "trip_id": result_trip.trip_id,
        "region_name": result_trip.region_name,
        "origin_coord": result_trip.origin_coord,
        "destination_coord": result_trip.destination_coord,
        "datetime": result_trip.datetime,
        "datasource_name": result_trip.datasource_name
    } 
    
    session.close() 

    return trip_data       
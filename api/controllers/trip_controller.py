from flask import Blueprint, jsonify, request
from create_database.models import Trip, DimRegion, DimDatasource
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.common.common_functions import calculate_distance, paginate_query_result
import time

# Create blueprint to be modular
trip_bp = Blueprint('trip_bp', __name__)

# Declare database to establish session
database_name = "database.db"
engine = create_engine(f'sqlite:///{database_name}')
Session = sessionmaker(bind=engine)

# Create route with method for api
@trip_bp.route('/trips', methods=['GET'])
def get_trips():
    try:
        start_time = time.time()

        # Extract parameters from the request URL
        region_name = request.args.get('region_name')
        start_date = request.args.get('start_date')
        datasource_name = request.args.get('datasource_name')
        page_number = int(request.args.get('page_number',1))
        page_size = int(request.args.get('page_size',10))
    

        # Establish connetion
        session = Session()

        # Declare query statement
        query = session.query(Trip, DimRegion.region_name, DimDatasource.datasource_name).\
            join(DimRegion, Trip.region_id == DimRegion.region_id).\
            join(DimDatasource, Trip.datasource_id == DimDatasource.datasource_id)

        # Validate if parameters were provided to add in the query
        if region_name is not None:
            query = query.filter(DimRegion.region_name == region_name.lower())
        
        if start_date is not None:
            query = query.filter(Trip.datetime>=start_date)
        
        if datasource_name is not None:
            query = query.filter(DimDatasource.datasource_name == datasource_name.lower())

        response, query_paginated = paginate_query_result(query,page_number,page_size)
        # Retrieve data
        trips = query_paginated.all()
        session.close()

        if not trips:
            return jsonify({"message": "No trips found"}), 404

        # Build response and calculate the traveled distance
        trip_list = []
        distance = 0
        for trip, region_name, datasource_name in trips:
            distance += calculate_distance(trip.origin_coord, trip.destination_coord) 
            trip_data = {
                "trip_id": trip.trip_id,
                "region_name": region_name,
                "origin_coord": trip.origin_coord,
                "destination_coord": trip.destination_coord,
                "datetime": trip.datetime.strftime('%Y-%m-%d %H:%M:%S'),
                "datasource": datasource_name
            }
            trip_list.append(trip_data)

        end_time = time.time()
        execution_time = end_time - start_time

        response['distance_traveled'] = distance
        response['data'] = trip_list
        response['execution_time'] = execution_time

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Create route with method for api
@trip_bp.route('/trips', methods=['POST'])
def add_trip():
    try:
        # Extract body
        data = request.get_json()

        session = Session()

        # Retrive region_id, datasourse based on the body
        region_id = session.query(DimRegion.region_id).filter_by(region_name = data['region_name'].lower()).first()
        datasource_id = session.query(DimDatasource.datasource_id).filter_by(datasource_name = data['datasource_name'].lower()).first()

        # Create a new trip
        new_trip = Trip(
            region_id=region_id[0],
            origin_coord=data['origin_coord'],
            destination_coord=data['destination_coord'],
            datetime=datetime.strptime(data['datetime'], '%Y-%m-%d %H:%M:%S'),
            datasource_id=datasource_id[0]
        )

        # Add new trip
        session.add(new_trip)
        session.commit()

        # Build response
        message = f"Trip id {new_trip.trip_id} added successfully"
        session.close()
        
        return jsonify({"message": message}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Create route with method for api    
@trip_bp.route('/trips/<int:trip_id>', methods=['DELETE'])
def delete_trip(trip_id):

    try:
        # Retrieve the trip to be deleted
        session = Session()
        trip = session.query(Trip).filter_by(trip_id=trip_id).first()

        if trip is None:
            session.close()
            return jsonify({"message": "Trip not found"}), 404

        # Delete the trip
        session.delete(trip)
        session.commit()
        session.close()

        return jsonify({"message": f"Trip id {trip_id} deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Create route with method for api
@trip_bp.route('/trips/<int:trip_id>', methods=['PUT'])
def update_trip(trip_id):
    try:
        # Extract body
        data = request.get_json()
        print(data)

        # Retrieve trip
        session = Session()
        trip = session.query(Trip).filter_by(trip_id = trip_id).first()

        if trip is None:
            session.close()
            return jsonify({"message": "Trip not found"}), 404
        
        
        # Validate if the body cointains the attribute to update
        if data.get('region_name') is not None:
            # Find the region_id for the update trip
            region_id = session.query(DimRegion.region_id).filter_by(region_name = data['region_name'].lower()).first()
            trip.region_id = region_id[0]
        if data.get('datasource_name')  is not None:
             # Find the datasource for the update trip
            datasource_id = session.query(DimDatasource.datasource_id).filter_by(datasource_name = data['datasource_name'].lower()).first()
            trip.datasource_id = datasource_id[0]
        if data.get('origin_coord')  is not None:
            trip.origin_coord = data.get('origin_coord', trip.origin_coord)
        if data.get('destination_coord')  is not None:
            trip.destination_coord = data.get('destination_coord', trip.destination_coord)
        if data.get('datetime')  is not None:
            trip.datetime = data.get(datetime.strptime(data['datetime'], '%Y-%m-%d %H:%M:%S'), trip.datetime)       
    
        session.commit()
        session.close()

        return jsonify({"message": f"Trip {trip_id} updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Create route with method for api
@trip_bp.route('/trips/<int:trip_id>', methods=['GET'])
def get_single_trip(trip_id):
    try:
        # Retrieve trip
        session = Session()
        trip = session.query(Trip, DimRegion.region_name, DimDatasource.datasource_name).join(DimRegion, Trip.region_id == DimRegion.region_id).join(DimDatasource, Trip.datasource_id == DimDatasource.datasource_id).filter(Trip.trip_id==trip_id).first()
        session.close()

        # Validate if the trip exist to handle error
        if trip is None:
            return jsonify({"message": "Trip not found"}), 404

        # Build the response form dictionary
        trip_details, region_name, datasource_name =  trip
        
        trip_data = {
            "trip_id": trip_details.trip_id,
            "region_name": region_name,
            "origin_coord": trip_details.origin_coord,
            "destination_coord": trip_details.destination_coord,
            "datetime": trip_details.datetime.strftime('%Y-%m-%d %H:%M'),
            "datasource_name": datasource_name
        }

        return jsonify(trip_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
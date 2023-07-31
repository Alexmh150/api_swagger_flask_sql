from flask import Blueprint, jsonify, request
from create_database.models import create_database, Trip
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

trip_bp = Blueprint('trip_bp', __name__)

database_name = "database.db"
engine = create_engine(f'sqlite:///{database_name}')
Session = sessionmaker(bind=engine)

@trip_bp.route('/trips', methods=['GET'])
def get_trips():
    try:
        # Extract query parameters from the request URL
        region_name = request.args.get('region_name')
        start_date = request.args.get('start_date')
        datasource = request.args.get('datasource')

        # Query the database to retrieve trips based on the specified filters
        session = Session()
        query = session.query(Trip)

        if region is not None:
            print(region)
            query = query.filter_by(region_name=region_name)

        if start_date is not None:
            query = query.filter(Trip.datetime>=start_date)
        
        if datasource is not None:
            query = query.filter_by(datasource=datasource)

        trips = query.all()
        session.close()

        if not trips:
            return jsonify({"message": "No trips found"}), 404

        # Convert the SQLAlchemy objects to a list of dictionaries for serialization
        trip_list = []
        for trip in trips:
            trip_data = {
                "trip_id": trip.trip_id,
                "region_name": trip.region_name,
                "origin_coord": trip.origin_coord,
                "destination_coord": trip.destination_coord,
                "datetime": trip.datetime.strftime('%Y-%m-%d %H:%M:%S'),
                "datasource": trip.datasource
            }
            trip_list.append(trip_data)

        return jsonify(trip_list), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@trip_bp.route('/trips', methods=['POST'])
def add_trip():
    try:
        # Extract JSON data from the request body
        data = request.get_json()

        # Create a new trip instance
        new_trip = Trip(
            region_name=data['region_name'],
            origin_coord=data['origin_coord'],
            destination_coord=data['destination_coord'],
            datetime=datetime.strptime(data['datetime'], '%Y-%m-%d %H:%M:%S'),
            datasource=data['datasource']
        )

        # Add the new trip to the database
        session = Session()
        session.add(new_trip)
        session.commit()
        session.close()

        return jsonify({"message": "Trip added successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@trip_bp.route('/trips/<int:trip_id>', methods=['DELETE'])
def delete_trip(trip_id):

    try:
        # Query the database to retrieve the trip by trip_id
        session = Session()
        trip = session.query(Trip).filter_by(trip_id=trip_id).first()

        if trip is None:
            session.close()
            return jsonify({"message": "Trip not found"}), 404

        # Delete the trip from the database
        session.delete(trip)
        session.commit()
        session.close()

        return jsonify({"message": "Trip deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@trip_bp.route('/trips/<int:trip_id>', methods=['PUT'])
def update_trip(trip_id):
    try:
        # Query the database to retrieve the trip by trip_id
        session = Session()
        trip = session.query(Trip).filter_by(trip_id=trip_id).first()

        if trip is None:
            session.close()
            return jsonify({"message": "Trip not found"}), 404

        # Extract JSON data from the request body
        data = request.get_json()

        # Update the trip attributes
        trip.region_name = data.get('region_name', trip.region_name)
        trip.origin_coord = data.get('origin_coord', trip.origin_coord)
        trip.destination_coord = data.get('destination_coord', trip.destination_coord)
        trip.datetime = datetime.strptime(data['datetime'], '%Y-%m-%d %H:%M:%S')
        trip.datasource = data.get('datasource', trip.datasource)

        # Commit the changes to the database
        session.commit()
        session.close()

        return jsonify({"message": "Trip updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@trip_bp.route('/trips/<int:trip_id>', methods=['GET'])
def get_single_trip(trip_id):
    try:
        # Query the database to retrieve the trip by trip_id
        session = Session()
        trip = session.query(Trip).filter_by(trip_id=trip_id).first()
        session.close()

        if trip is None:
            return jsonify({"message": "Trip not found"}), 404

        # Convert the SQLAlchemy object to a dictionary for serialization
        trip_data = {
            "trip_id": trip.trip_id,
            "region_name": trip.region_name,
            "origin_coord": trip.origin_coord,
            "destination_coord": trip.destination_coord,
            "datetime": trip.datetime.strftime('%Y-%m-%d %H:%M'),
            "datasource": trip.datasource
        }

        return jsonify(trip_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
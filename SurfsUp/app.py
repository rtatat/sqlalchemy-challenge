# Import the dependencies.
import numpy as np 
import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")
# Declare a Base using `automap_base()`
Base = automap_base()
# Use the Base class to reflect the database tables
Base.prepare(engine, reflect = True)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return(
        f"Welcome to the Climate Analysis App<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"Note that in the following, dates need to be entered in the following format: YYYY-MM-DD"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

# This route will query precipitation levels and dates and returns a dictionary based on them
@app.route("/api/v1.0/precipitation")
def precipitation():
    # The session will begin here
    session = Session(engine)

    """Return a list of Precipitation and Date data"""
    # Obtain the precipitation data from the past year
    precip_query = session.query(Measurement.prcp, Measurement.date).all()
    
    session.close()

    # Get a JSON representation of the dictionary
    precip_query_values = []
    for prcp, date in precip_query:
        precipitation_dictionary = {}
        precipitation_dictionary["precipitation"] = prcp
        precipitation_dictionary["date"] = date
        precip_query_values.append(precipitation_dictionary)

    return jsonify(precip_query_values)

# This route will query all of the station data
@app.route("/api/v1.0/stations")
def stations():
    # Begin the session
    session = Session(engine)

    """Return a list of all active stations in Hawaii"""
    station_query = session.query(Station.station, Station.id).all()
    session.close()

    # Get a JSON representation
    station_info = []
    for station, id in station_query:
        station_info_dict = {}
        station_info_dict["station"] = station
        station_info_dict["id"] = id
        station_info.append(station_info_dict)

    return jsonify(station_info)

# This route will query the temperature observation for the most active station in a year
@app.route("/api/v1.0/tobs")
def tobs():
    # Begin session
    session = Session(engine)

    """Return a list of dates and temperatures from the most active station over the year"""
    # This will get the latest date recorded
    last_year_data = session.query(Measurement.date).\
        order_by(Measurement.date.desc()).first()
    print(last_year_data)

    query_start_date = dt.date(2017, 8, 23)-dt.timedelta(days = 365)
    print(query_start_date)

    station_activity = session.query(Measurement.station, func.count(Measurement.station)).\
        order_by(func.count(Measurement.station).desc()).\
        group_by(Measurement.station).first()
    most_active_station = station_activity[0]

    session.close()
    print(most_active_station)

    # Obtain data of tobs over the last year in the most active station
    tobs_most_active_station = session.query(Measurement.date, Measurement.tobs, Measurement.station).\
        filter(Measurement.date > query_start_date).\
        filter(Measurement.station == most_active_station)
    session.close()
    
    # Use the above query to create a list to display the data of the most active station
    most_active_station_values = []
    for date, tobs, station in tobs_most_active_station:
        mas_dict = {}
        mas_dict["date"] = date
        mas_dict["tobs"] = tobs
        mas_dict["station"] = station
        most_active_station_values.append(mas_dict)

    return jsonify(most_active_station_values)

# This route will return min, max and avg temperature values for all dates equal to or greater than the start date
@app.route("/api/v1.0/start")
def start_date(start):
    session = Session(engine)

    """Return minimum, average and maximum temperature values given the start date"""
    start_date_tobs_info = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    # This will create a list of the information obtained above
    start_date_tobs_values = []
    for min, avg, max in start_date_tobs_info:
        start_date_tobs_dict = {}
        start_date_tobs_dict["min"] = min
        start_date_tobs_dict["avg"] = avg
        start_date_tobs_dict["max"] = max
        start_date_tobs_values.append(start_date_tobs_dict)

    return jsonify(start_date_tobs_values)

# This route will return min, max and avg temperature values for all dates from the start date to the end date inclusively
@app.route("/api/v1.0/start/end")
def start_end_date(start, end):
    session = Session(engine)

    """eturn minimum, average and maximum temperature values from the start date to the end date inclusively"""
    start_end_date_tobs_info = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    session.close()

    #Creating a list based on info above
    start_end_tobs_values = []
    for min, avg, max in start_end_date_tobs_info:
        start_end_tobs_dict = {}
        start_end_tobs_dict["min"] = min
        start_end_tobs_dict["avg"] = avg
        start_end_tobs_dict["max"] = max
        start_end_tobs_values.append(start_end_tobs_dict)

    return jsonify(start_end_tobs_values)

if __name__ == "__main__":
    app.run(debug=True)
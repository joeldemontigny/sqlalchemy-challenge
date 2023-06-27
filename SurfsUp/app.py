# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
base = automap_base()
# reflect the tables
base.prepare(autoload_with=engine)

# Save references to each table
measurement = base.classes.measurement
station = base.classes.station

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

#Start at the homepage

@app.route("/")
def homepage():
    """List all the available routes"""
    return(
        f"Available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Find latest date
    recent_data = session.query(measurement.date).order_by(measurement.date.desc()).first()
    # Query last 12 months and precipitation
    
    yearago = (dt.date(2017,8,23)) - (dt.timedelta(days=365))
    results = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= yearago).all()

    # Close session
    session.close()

    # Create a dictionary from the row data and append to a list of data_prcp
    data_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        data_prcp.append(prcp_dict)

    return jsonify(data_prcp)

@app.route("/api/v1.0/stations")
def stations():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Preform a query to retrieve data for all stations
    stations = session.query(station.station, station.name, station.latitude, station.longitude, station.elevation).all()
    
    # Close Session                                                  
    session.close()
    
    # Create a dictionary from the row data and append to list station_data
    station_data = []
    for station, name, latitude, longitude, elevation in stations:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name        
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        station_data.append(station_dict)
        
    return jsonify(station_data)

@app.route("/api/v1.0/tobs")
def tobs():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Calculate the date one year from the last date in data set.
    yearago = (dt.date(2017,8,23)) - (dt.timedelta(days=365))
    
    # Query the last 12 months of temperature observation (TOBS) data for the most active station
    active_station = session.query(measurement.tobs).filter(measurement.station == 'USC00519281').\
                            filter(measurement.date >= yearago).all()
    
    # Close Session                                                  
    session.close()
    
    # Create a dictionary from the row data and append to list most_active
    most_active = []
    for date, tobs in active_station:
        active_dict = {}
        active_dict["date"] = date
        active_dict["temperature"] = tobs
        most_active.append(active_dict)
        
    return jsonify(most_active)

@app.route("/api/v1.0/<start>")
def start(start):

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Preform a query to retrieve the minimum, maximum, and average temperature for a specified start date to the end of the dataset
    query_results = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
            filter(measurement.date >= start).filter(measurement.date <= end).order_by (measurement.date).all()
    
    # Close Session                                                  
    session.close()
    
    # Create a dictionary from the row data and append to list start_date
    start_date = []
    for min, max, avg in query_results:
        start_dict = {}
        start_dict["minimum temperature"] = min
        start_dict["maxium temperature"] = max
        start_dict["average temperature"] = avg
        start_date.append(start_dict)
        
    return jsonify(start_date)

@app.route("/api/v1.0/<start>/<end>")
def range_date(start,end):
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
   # Using the most active station id from the previous query, calculate the lowest, highest, and average temperature.
    range_summary = session.query(func.min(measurement.tobs), func.max(measurement.tobs),\
                                  func.avg(measurement.tobs)).filter(measurement.date.between(start, end)).all()
    
    # Close Session                                                  
    session.close()
    
    # Create a dictionary from the row data and append to list range_date
    range_date = []
    for min, max, avg in query_results:
        range_dict = {}
        range_dict["Minimum Temperature"] = min
        range_dict["Maxium Temperature"] = max
        range_dict["Average Temperature"] = avg
        range_date.append(range_dict)
        
    return jsonify(range_date)
    
if __name__ == '__main__':
    app.run(debug=True)

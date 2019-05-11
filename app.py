import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt
import numpy as np


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite?check_same_thread=False")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Find last date and the date one year before
#################################################

date_list = engine.execute('SELECT date FROM measurement').fetchall()
max_date = max(date_list)
last_date = max_date[0]
final_date = dt.date.fromisoformat(last_date)
year_ago = final_date.year - 1
year_ago_date = final_date.replace(year = year_ago)
first_date = year_ago_date.isoformat()


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/precipitation<br/>"
        f"/api/stations<br/>"
        f"/api/temperature<br/>"
        f"/api/&lt;start&gt; [YYYY-MM-DD]<br/>"
        f"/api/&lt;start&gt;/&lt;end&gt [YYYY-MM-DD];"
    )


@app.route("/api/precipitation")
def precipitation():
    """Return the amounts of precipitation"""
    # Query for precipitation on date
    results = session.query(Measurement.date, Measurement.prcp).all()

    # Create a dictionary from the row data and append to a list of prcp data
    all_prcp = []
    for date, prcp in results:
        prcp_dict = {date:prcp}
        all_prcp.append(prcp_dict)

        return jsonify(all_prcp)


@app.route("/api/stations")
def stations():
    """Return a list of stations from the dataset"""
    # Query all stations
    results = session.query(Station.station, Station.name).all()

    # Create a dictionary from the row data and append to a list of all_stations
    all_stations = []
    for station, name in results:
        station_dict = {station:name}
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/temperature")
def temps():
    """Return a list of the most recent year of temperature data from the dataset"""
    # Query all stations
    msmt = [Measurement.date, Measurement.tobs]

    past_year = session.query(*msmt).\
        filter(Measurement.date >= year_ago_date).\
        order_by(Measurement.date).all()

    # Create a dictionary from the row data and append to a list of all_temps
    all_temps = []
    for year in past_year:
        temp_dict = {year[0]:year[1]}
        all_temps.append(temp_dict)

    return jsonify(all_temps)


@app.route("/api/<start>", defaults={"start":first_date})
def starting(start):
    """Return tavg, tmax, and tmin from the dataset starting from the provided date"""
    # Query all stations
    msmt = [Measurement.date, Measurement.tobs]

    # Filter out results before passed-in date
    from_date = session.query(*msmt).\
        filter(Measurement.date >= start).\
        order_by(Measurement.date).all()
    
    # Calculate the average temperature for the range of dates
    tobs_sum = 0
    tobs_count = 0
    for date in from_date:
        tobs_sum = tobs_sum + date[1]
        tobs_count = tobs_count + 1
    tobs_avg = round((tobs_sum / tobs_count), 1)

    # Create a dictionary from the row data and calculate min and max since start date
    start_dict = {}
    start_dict["tavg"] = tobs_avg
    start_dict["tmax"] = max(from_date)[1]
    start_dict["tmin"] = min(from_date)[1]

    return jsonify(start_dict)


@app.route("/api/<start>/<end>", defaults={'start':first_date, 'end': last_date})
def between(start,end):
    """Return tavg, tmax, and tmin from the dataset between the provided dates"""
    # Query all stations
    msmt = [Measurement.date, Measurement.tobs]

    # Filter out results outside the passed-in dates
    btw_dates = session.query(*msmt).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).\
        order_by(Measurement.date).all()
    
    # Calculate the average temperature for the range of dates
    tobs_sum = 0
    tobs_count = 0
    for date in btw_dates:
        tobs_sum = tobs_sum + date[1]
        tobs_count = tobs_count + 1
    tobs_avg = round((tobs_sum / tobs_count), 1)

    # Create a dictionary from the row data and calculate min and max since start date
    start_dict = {}
    start_dict["tavg"] = tobs_avg
    start_dict["tmax"] = max(btw_dates)[1]
    start_dict["tmin"] = min(btw_dates)[1]

    return jsonify(start_dict)




if __name__ == '__main__':
    app.run(debug=True)
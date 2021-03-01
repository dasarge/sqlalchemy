# import dependencies
import numpy as np
import datetime as dt
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# -------------------------------------------------------------
# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database and tables
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# ------------------------------------------------------
session = Session(engine)

# Design a query to find the most active stations (what stations have the most rows?)
# List the stations and the counts in descending order.

station_max = session.query(Measurement.station, func.count(Measurement.station)).group_by(
    Measurement.station).order_by(func.count(Measurement.station).desc()).all()

# create DataFrame using data
df = pd.DataFrame(station_max, columns=['station', 'count'])

max_df = df.loc[df['count'].idxmax()]


# find the last date in the database
last_date = session.query(Measurement.date).order_by(
    Measurement.date.desc()).first()

# Calculate the date 1 year ago from the last data point in the database
query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

session.close()
# ---------------------------------------------------------
# Create an app
app = Flask(__name__)

# --------------------------------------------------------------
# Flask Routes
# Define what to do when user hits the index route


@app.route("/")
def home():
    """List all available api routes."""
    return(
        f"Welcome to Hawaii Climate Page<br/> "
        f"Available Routes:<br/>"
        f"<br/>"
        f"The list of precipitation data with dates:<br/>"
        f"Precipitation <a href='/api/v1.0/precipitation' target='_blank'>/api/v1.0/precipitation</a><br/>"
        f"<br/>"
        f"The list of stations and names:<br/>"
        f"Active_Stations <a href='/api/v1.0/stations' target='_blank'>/api/v1.0/stations</a><br/>"
        f"<br/>"
        f"The most active station:{(max_df)}<br/>"
        f"<br/>"
        f"The list of temperture observations for the most active weather station from a year from the last data point:<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"Min, Max. and Avg. temperatures for given start date: (please use 'yyyy-mm-dd' format):<br/>"
        f"/api/v1.0/min_max_avg/&lt;start date&gt;<br/>"
        f"<br/>"
        f"Min. Max. and Avg. tempratures for given start and end date: (please use 'yyyy-mm-dd'/'yyyy-mm-dd' format for start and end values):<br/>"
        f"/api/v1.0/min_max_avg/&lt;start date&gt;/&lt;end date&gt;<br/>"
        f"<br/>"
        f"<a href='/api/v1.0/min_max_avg/2012-01-01/2016-12-31' target='_blank'>/api/v1.0/min_max_avg/2012-01-01/2016-12-31</a>"
    )
# ------------------------------------------------------

# create precipitation route


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create the session link
    session = Session(engine)

    """Return the dictionary for date and precipitation info"""
    # Query precipitation and date values
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Create a dictionary as date the key and prcp as the value
    precipitation = []
    for result in results:
        r = {}
        r[result[0]] = result[1]
        precipitation.append(r)

    return jsonify(precipitation)

# -----------------------------------------------

# create stations route


@app.route("/api/v1.0/stations")
def stations():
    # Create the session link
    session = Session(engine)

    """Return a JSON list of stations from the dataset."""
    # Query data to get stations list
    results = session.query(Station.station, Station.name).all()
    session.close()

    # Convert list of tuples into list of dictionaries for each station and name
    station_list = []
    for result in results:
        r = {}
        r["station"] = result[0]
        r["name"] = result[1]
        station_list.append(r)

    # jsonify the list
    return jsonify(station_list)
# -----------------------------------------------

# # create most_active_station route


# @app.route("/api/v1.0/MaxStations")
# def MaxStations():
#     # Create the session link
#     session = Session(engine)
#     return f"most active station"


# -------------------------------------------------------

# create temperatures route


@app.route("/api/v1.0/tobs")
def tobs():
    # create session link
    session = Session(engine)

    """Return a JSON list of Temperature Observations (tobs) for the previous year."""
    # query tempratures from a year from the last data point.
    # query_date  is "2016-08-23" for the last year query
    results = session.query(Measurement.tobs, Measurement.date).filter(
        Measurement.date >= query_date).all()

    session.close()

    # convert list of tuples to show date and temprature values
    tobs_list = []
    for result in results:
        r = {}
        r["date"] = result[1]
        r["temprature"] = result[0]
        tobs_list.append(r)

    # jsonify the list
    return jsonify(tobs_list)

# -------------------------------------------------------

# create route for query the most active station for the last year of data


@app.route("/api/v1.0/min_max_avg/<start>")
def start(start):
    # create session link
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date."""

    # take any date and convert to yyyy-mm-dd format for the query
    start_dt = dt.datetime.strptime(start, '%Y-%m-%d')

    # query data for the start date value
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(
        Measurement.tobs)).filter(Measurement.date >= start_dt).all()

    session.close()

    # Create a list to hold results
    t_list = []
    for result in results:
        r = {}
        r["StartDate"] = start_dt
        r["TMIN"] = result[0]
        r["TAVG"] = result[1]
        r["TMAX"] = result[2]
        t_list.append(r)

    # jsonify the result
    return jsonify(t_list)

# ------------------------------------------------------

# create route for theset start date to last date of data


@app.route("/api/v1.0/min_max_avg/<start>/<end>")
def start_end(start, end):
    # create session link
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start and end dates."""

    # take start and end dates and convert to yyyy-mm-dd format for the query
    start_dt = dt.datetime.strptime(start, '%Y-%m-%d')
    end_dt = dt.datetime.strptime(end, "%Y-%m-%d")

    # query data for the start date value
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(
        Measurement.tobs)).filter(Measurement.date >= start_dt).filter(Measurement.date <= end_dt)

    session.close()

    # Create a list to hold results
    t_list = []
    for result in results:
        r = {}
        r["StartDate"] = start_dt
        r["EndDate"] = end_dt
        r["TMIN"] = result[0]
        r["TAVG"] = result[1]
        r["TMAX"] = result[2]
        t_list.append(r)

    # jsonify the result
    return jsonify(t_list)


# ---------------------------------------------------------
# run the app
if __name__ == "__main__":
    app.run(debug=True)

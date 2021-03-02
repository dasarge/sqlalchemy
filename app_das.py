
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


# station_max = session.query(Measurement.station, func.count(Measurement.station)).group_by(
#     Measurement.station).order_by(func.count(Measurement.station).desc()).all()

# # create DataFrame using data
# df = pd.DataFrame(station_max, columns=['station', 'count'])

# max_df = df.loc[df['count'].idxmax()]


# # find the last date in the database
# last_date = session.query(Measurement.date).order_by(
#     Measurement.date.desc()).first()

# # Calculate the date 1 year ago from the last data point in the database
# #calc_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
# calc_date = dt.date(last_date) - dt.timedelta(days=365)
# session.close()
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
        f"1. - The list of precipitation data with dates:<br/>"
        f"Precipitation <a href='/api/v1.0/precipitation' target='_blank'>/api/v1.0/precipitation</a><br/>"
        f"------------------------------------------<br/>"
        f"2. - The list of stations and names:<br/>"
        f"Active_Stations <a href='/api/v1.0/stations' target='_blank'>/api/v1.0/stations</a><br/>"
        f"--------------------------------------------<br/>"
        f"3. - The most active station:{(max_df)}<br/>"
        f"<br/>"
        f"First date entered:{first_date}<br/>"
        f"<br/>"
        f"Date 1 year before last date entered:{calc_date}<br/>"
        f"<br/>"
        f"Last date entered:{last_date}<br/>"
        f"--------------------------------------------<br/>"
        f"4. - The list of temperture observations for the most active weather station from a year from the last data point:<br/>"
        f"<br/>"
        f"<a href='/api/v1.0/min_max_avg/2016-08-23/2017-08-23' target='_blank'>/api/v1.0/tobs</a><br/>"
        f"----------------------------------------------<br/>"
        f"5. - Min. Max. and Avg. tempratures for given start and end date:<br/>"
        f"<br/>"
        f"temperature by date <a href='/api/v1.0/min_max_avg/2012-01-01/2016-12-31' target='_blank'>/api/v1.0/min_max_avg</a>"
    )
# ------------------------------------------------------
# 1. - create precipitation route


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
# 2. - create stations route


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
# 3. - Design a query to find the most active stations
# List the stations and the counts in descending order.
# Find most active atation


station_max = session.query(Measurement.station, func.count(Measurement.station)).group_by(
    Measurement.station).order_by(func.count(Measurement.station).desc()).all()

# create DataFrame using data
df = pd.DataFrame(station_max, columns=['station', 'count'])

max_df = df.loc[df['count'].idxmax()]

# -------------------------------------------------------
# find the first date in the database
first_date = session.query(Measurement.date).order_by(
    Measurement.date.asc()).first()

# ----------------------------------------------------

# find the last date in the database
last_date = session.query(Measurement.date).order_by(
    Measurement.date.desc()).first()

# --------------------------------------------------------------


# Calculate the date 1 year ago from the last data point in the database
calc_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
session.close()


# -------------------------------------------------------
# 4. - create temperatures route

@app.route("/api/v1.0/tobs")
def tobs():
    # create session link
    session = Session(engine)

    """Return a JSON list of Temperature Observations (tobs) for the previous year."""
    # query tempratures from a year from the last data point.
    # calc_date  is "2016-08-23" for the last year query
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= '2016-08-23').all()

    session.close()

    t_list = []
    for result in results:
        r = {}
        r["StartDate"] = start_dt
        r["StartDate"] = start_dt
        r["TMIN"] = result[0]
        r["TAVG"] = result[1]
        r["TMAX"] = result[2]
        t_list.append(r)

    # convert list of tuples to show date and temperature values
    tobs_list = []
    for result in results:
        r = {}
        r["date"] = result[1]
        r["temperature"] = result[0]
        tobs_list.append(r)

    # jsonify the list
    return jsonify(tobs_list)

# -------------------------------------------------------
# 5. - create route for query the most active station for the last year of data


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
    app.run(debug=True, host="127.0.0.1", port=8010)

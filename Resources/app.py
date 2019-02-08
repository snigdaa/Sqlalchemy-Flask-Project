from flask import Flask, jsonify, render_template
import pandas as pd 
import numpy as np
import datetime as dt  

#set up sqlalchemy for the queries in flask
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, or_, and_

import pymysql
pymysql.install_as_MySQLdb()

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#set up the app
app = Flask(__name__)

@app.route('/')
def home():
    return(render_template('home.html'))

@app.route("/api/v1.0/precipitation")
def precipitation():
    rain = session.query(Measurement.date, func.sum(Measurement.prcp)).group_by(Measurement.date).all()
    raindf = pd.DataFrame(rain, columns = ['Date','Total Precipitation per day (in)'])
    raindf = raindf.set_index('Date')
    raindict = raindf.to_dict()
    return(jsonify(raindict))

@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Station.name).group_by(Station.name).all()
    stationdf = pd.DataFrame(stations)
    stationdict = stationdf.to_dict()
    return(jsonify(stationdict))

@app.route("/api/v1.0/tobs")
def tobs():
    lastdate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    lastformat = dt.datetime.strptime(lastdate, '%Y-%m-%d')
    oneYr = lastformat - dt.timedelta(weeks=52)
    yrBefore = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date >= oneYr).all()
    tobsYr = pd.DataFrame(yrBefore, columns = ['Date','Temp Observed'])
    tobsYr = tobsYr.set_index('Date')
    tobsYr = tobsYr.sort_values(by='Date',ascending=False)
    tobsdict = tobsYr.to_dict()
    return(jsonify(tobsdict))

@app.route("/api/v1.0/<start>")
def analyzer(start):
    temps = session.query(Measurement.date, func.min(Measurement.tobs), \
        func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
    tempsdf = pd.DataFrame(temps, columns = ['DATE', 'TMIN', 'TAVG','TMAX'])
    tempsdf = tempsdf.drop('DATE', axis=1)
    tempsdict = tempsdf.to_dict('records')
    return(jsonify(tempsdict))

@app.route("/api/v1.0/<start>/<end>")
def startend(start, end):
    temps = session.query(Measurement.date, func.min(Measurement.tobs), \
        func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(and_(Measurement.date >= start, Measurement.date <= end)).all()
    tempsdf = pd.DataFrame(temps, columns = ['DATE','TMIN', 'TAVG','TMAX'])
    tempsdf = tempsdf.drop('DATE', axis=1)
    tempsdict = tempsdf.to_dict('records')
    return(jsonify(tempsdict))

if __name__ == '__main__':
    app.run(debug=True)
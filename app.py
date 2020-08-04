import numpy as np
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
Base = automap_base()
Base.prepare(engine, reflect=True)

# Base.metadata.tables # Check tables, not much useful
# Base.classes.keys() # Get the table names

measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"Temperature start date(yyyy-mm-dd): /api/overalltempstats/yyyy-mm-dd<br/>"
        f"Temperature over most recent year: /api/TemperatureObserved<br/>"
        f"Temperature start to end dates(yyyy-mm-dd): /api/overalltempstats/yyyy-mm-dd/yyyy-mm-dd <br/>"   
        f"Precipitation: /api/precipitation<br/>"
        f"List of Stations: /api/stations"
    )


@app.route('/api/overalltempstats/<start>/<stop>')
def tempStartStop(start, stop):
    session = Session(engine)
    queryresult = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= stop).all()
    session.close()
    tempAll = []
    for min,avg,max in queryresult:
        tempDict = {}
        tempDict["Min"] = min
        tempDict["Average"] = avg
        tempDict["Max"] = max
        tempAll.append(tempDict)

    return jsonify(tempAll)



@app.route('/api/overalltempstats/<start>')
def tempStart(start):
    session = Session(engine)
    queryresult = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).all()
    session.close()
    tempAll = []
    for min,avg,max in queryresult:
        tempDict = {}
        tempDict["Min"] = min
        tempDict["Average"] = avg
        tempDict["Max"] = max
        tempAll.append(tempDict)

    return jsonify(tempAll)

@app.route('/api/TemperatureObserved')
def temp():
    session = Session(engine)
    bdQuery = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    edQuery = dt.datetime.strptime(bdQuery, '%Y-%m-%d')
    querydate = dt.date(edQuery.year -1, edQuery.month, edQuery.day)
    sel = [measurement.date,measurement.tobs]
    queryresult = session.query(*sel).filter(measurement.date >= querydate).all()
    session.close()

    tempAll = []
    for date, tobs in queryresult:
        tempDict = {}
        tempDict["Date"] = date
        tempDict["Temprature Observed"] = tobs
        tempAll.append(tempDict)

    return jsonify(tempAll)


@app.route('/api/precipitation')
def precipitation():
    session = Session(engine)
    sel = [measurement.date,measurement.prcp]
    queryresult = session.query(*sel).all()
    session.close()

    precipitation = []
    for date, prcp in queryresult:
        prcpDict = {}
        prcpDict["Date"] = date
        prcpDict["Precipitation"] = prcp
        precipitation.append(prcpDict)

    return jsonify(precipitation)

@app.route('/api/stations')
def stations():
    station = Base.classes.station
    session = Session(engine)
    sel = [station.station,station.name,station.latitude,station.longitude,station.elevation]
    queryresult = session.query(*sel).all()
    
    session.close()

    stationsj = []
    for station,name,lat,lon,el in queryresult:
        stationDict = {}
        stationDict["Station"] = station
        stationDict["Name"] = name
        stationDict["Lat"] = lat
        stationDict["Lon"] = lon
        stationDict["Elevation"] = el
        stationsj.append(stationDict)

    return jsonify(stationsj)

if __name__ == '__main__':
    app.run(debug=True)
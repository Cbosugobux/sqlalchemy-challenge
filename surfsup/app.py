# Import the dependencies.
from flask import Flask, jsonify
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.dates as mdates
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
# Create Engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measure = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

# Setup Flask App
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

# Create the Home Route and display apis as links
@app.route('/')
def home():
    return(
       "<div style='text-align: center;'>"
        "<h1>Welcome to the Hawaii Weather Analysis API</h1>"
        "</div>"
        "<div style='text-align: left; margin-left: 20px;'>"
        "<h2>Please select your desired API</h2>"
        "<ul>"
        "<li><a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a></li>"
        "<li><a href='/api/v1.0/stations'>/api/v1.0/stations</a></li>"
        "<li><a href='/api/v1.0/tobs'>/api/v1.0/tobs</a></li>"
        "<li><a href='/api/v1.0/start/end'>/api/v1.0/start/end</a></li>"
        "<small style = 'margin-left: 20px; color: red;'>After Selecting, user must enter date in address bar as MMDDYYY</small><br>"
        "<small style = 'margin-left: 20px; color: red;'>For Start and End Date Enter StartDate/EndDate in address bar</small>"
        "</ul>"
        "</div>"
    )

@app.route("/api/v1.0/precipitation")
def precip():
    # Calculate the date one year from the last date in data set.
    oneYearAgo = dt.date(2017,8,23) - dt.timedelta(days=365)


    # Perform a query to retrieve the data and precipitation scores
    queryResults = (
    session.query(measure.date, measure.prcp).filter(measure.date >= oneYearAgo).all())
    
    session.close()
    #Dictionary with the date as the key and the precipitation (prcp) as the value
    precipitation = {date: prcp for date, prcp in queryResults}
    
    #Covert to a JSON
    return jsonify(precipitation)
    
@app.route("/api/v1.0/stations")
def stations():
    # Design a query to find the most active stations (i.e. which stations have the most rows?)
    queryResults = (session.query(station.station).all())

    # Close Session
    session.close()
    
    # Convert to One Dimensional Array
    stationList = list(np.ravel(queryResults))
    
    # Convert to JSON and display
    return jsonify(stationList)

@app.route("/api/v1.0/tobs")
def temperatures():
    # Return the previous years temperatures
    # Calculate the date one year from the last date in data set.
    oneYearAgo = dt.date(2017,8,23) - dt.timedelta(days=365)


    # Perform a query to retrieve the data and precipitation scores
    queryResults = session.query(measure.tobs).\
        filter(measure.station == 'USC00519281').\
        filter(measure.date >= oneYearAgo).all()
    
    # Close the Session
    session.close()
    
    tempList = list(np.ravel(queryResults))
    
    # Return the list of temps as a JSON
    return jsonify(tempList)
    
# Start and End Route    
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def dateStats(start=None, end = None):

    # Select statement
    selection = [func.min(measure.tobs), func.max(measure.tobs), func.avg(measure.tobs)]
    
    if not end:
        
        startDate = dt.datetime.strptime(start, "%m%d%Y")
    
        queryResults = session.query(*selection).filter(measure.date >= startDate).all()
        
        session.close()
        
        tempList = list(np.ravel(queryResults))
    
         # Return the list of temps as a JSON
        return jsonify(tempList)
    
    else:
        startDate = dt.datetime.strptime(start, "%m%d%Y")
        endDate = dt.datetime.strptime(end,"%m%d%Y")
    
        queryResults = session.query(*selection).filter(measure.date >= startDate)\
            .filter(measure.date > startDate)\
            .filter(measure.date <= endDate).all()
        
        session.close()
        
        tempList = list(np.ravel(queryResults))
    
    # Return the list of temps as a JSON
    return jsonify(tempList)
    
    
## App Launcher
if __name__ == '__main__':
    app.run()
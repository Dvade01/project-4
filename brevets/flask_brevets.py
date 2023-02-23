"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)
"""

import flask
from flask import request
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations
import config

import logging

###
# Globals
###
app = flask.Flask(__name__)
CONFIG = config.configuration()

###
# Pages
###


@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    return flask.render_template('404.html'), 404


###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############
@app.route("/_calc_times")
def _calc_times():
    # Log request
    app.logger.debug("Got a JSON request")

    # Retrieve request parameters
    km = request.args.get('km', 999, type=float)
    brev_km_dist = request.args.get('brev_km_dist', default=None, type=int)
    if brev_km_dist is None:
        # If 'brev_km_dist' is not provided or is not a valid integer, raise an HTTPException with a 400 Bad Request status code
        raise BadRequest("Missing or invalid 'brev_km_dist' parameter")
    brev_start = request.args.get('brev_start_date', default=None, type=str)
    if brev_start is None:
        # If 'brev_start_date' is not provided or is not a valid string, raise an HTTPException with a 400 Bad Request status code
        raise BadRequest("Missing or invalid 'brev_start_date' parameter")

    # Convert start date to Arrow object for calculations
    start_time = arrow.get(brev_start)

    # Log parameters for debugging purposes
    app.logger.debug("km={}".format(km))
    app.logger.debug("brev_dist={}".format(brev_km_dist))
    app.logger.debug("brev_start={}".format(brev_start))

    # Calculate open and close times based on input parameters
    open_time = acp_times.open_time(km, brev_km_dist, start_time) # calculate open time
    open_time_str = open_time.format('YYYY-MM-DDTHH:mm') # Removed isoformat for readability

    close_time = acp_times.close_time(km, brev_km_dist, start_time) # calculate close time
    close_time_str = close_time.format('YYYY-MM-DDTHH:mm') # Removed isoformat for readability

    result = {"open": open_time_str, "close": close_time_str}
    return flask.jsonify(result=result)


#############

app.debug = CONFIG.DEBUG
if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    print("Opening for global access on port {}".format(CONFIG.PORT))
    app.run(port=CONFIG.PORT, host="0.0.0.0")
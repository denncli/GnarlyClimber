import flask
import GnarlyClimber
from flask import request

@GnarlyClimber.app.route('/routes/', methods=["GET"])
def show_routes():
    '''
    location = flask.request.form['location']
    maxDistanceMiles = flask.request.form['maxDistanceMiles']
    minDifficulty = flask.request.form['minDifficulty']
    maxDifficulty = flask.request.form['maxDifficulty']
    '''
    location = request.args.get('location')
    maxDistanceMiles = request.args.get('maxDistanceMiles')
    minDifficulty = request.args.get('minDifficulty')
    maxDifficulty = request.args.get('maxDifficulty')

    """Display / route."""
    context = {
        "location" : location,
        "maxDistanceMiles" : maxDistanceMiles,
        "maxResults" : GnarlyClimber.app.config['NUM_RESULTS'],
        "minDifficulty" : minDifficulty,
        "maxDifficulty" : maxDifficulty
    }
    return flask.render_template("routes.html", **context)

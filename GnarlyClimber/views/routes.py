import flask
import GnarlyClimber


@GnarlyClimber.app.route('/routes/string:location>/<int:maxDistanceMiles>' \
        '/<int:maxResults>/<string:minDifficulty>/<string:maxDifficulty>/', methods=["GET"])
def show_routes(location, maxDistanceMiles, minDifficulty, maxDifficulty):
    """Display / route."""
    context = {
        "location" : location,
        "maxDistanceMiles" : maxDistanceMiles,
        "maxResults" : GnarlyClimber.app.config['NUM_RESULTS'],
        "minDifficulty" : minDifficulty,
        "maxDifficulty" : maxDifficulty
    }
    return flask.render_template("routes.html", **context)

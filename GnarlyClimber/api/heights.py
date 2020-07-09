import flask
import GnarlyClimber
import mtn_project_height_scraper

#TODO: support search by city
#TODO: consider putting cached case into this file
@GnarlyClimber.app.route('/api/height/<float:lat>/<float:lon>/<int:maxDistanceMiles>' \
        '/<int:maxResults>/<string:minDifficulty>/<string:maxDifficulty>/', methods=["GET"])
def get_post(lat, lon, maxDistanceMiles, maxResults, minDifficulty, maxDifficulty):
    height_sorted_routes = \
            mtn_project_height_scraper.get_height_sorted_routes(lat, lon, maxDistanceMiles=maxDistanceMiles,
            maxResults=maxResults, minDifficulty=minDifficulty, maxDifficulty=maxDifficulty)
    context = {
        "height_sorted_routes": height_sorted_routes
    }
    return flask.jsonify(**context)
import flask
import GnarlyClimber
import GnarlyClimber.api.mtn_project_height_scraper #TODO: import as, it causes import to fail
from requests.exceptions import HTTPError

#TODO: support search by city, consider doing conversion to lat lon on front end 
#TODO: consider putting cached case into this file
@GnarlyClimber.app.route('/api/height/<string:lat>/<string:lon>/<int:maxDistanceMiles>' \
        '/<int:maxResults>/<string:minDifficulty>/<string:maxDifficulty>/', methods=["GET"])
def get_heights(lat, lon, maxDistanceMiles, maxResults, minDifficulty, maxDifficulty):
    #pass in lat and lon as strings because flask api call does not support negative floats
    lat = float(lat)
    lon = float(lon)
    try:
        height_sorted_routes = \
                GnarlyClimber.api.mtn_project_height_scraper.get_height_sorted_routes(
                lat, lon, maxDistanceMiles=maxDistanceMiles, maxResults=maxResults,
                minDifficulty=minDifficulty, maxDifficulty=maxDifficulty)
        success = True
    except:
        height_sorted_routes = []
        success = False
    
    height_sorted_routes = GnarlyClimber.api.mtn_project_height_scraper.convert_list_of_routes_to_json(
            height_sorted_routes)
        
    context = {
        "height_sorted_routes": height_sorted_routes,
        "success" : success
    }
    return flask.jsonify(**context)
import flask
import GnarlyClimber
from requests.exceptions import HTTPError

def parse_coordinates(coordinates):
    coordinates = coordinates.replace(" ", "")
    coordinates = coordinates.replace("\t", "")
    coordinates = coordinates.split(",")
    lat = coordinates[0]
    lon = coordinates[1]
    return float(lat), float(lon)


#TODO: support search by city, consider doing conversion to lat lon on front end 
#TODO: consider putting cached case into this file
@GnarlyClimber.app.route('/api/routes/<string:location>/<int:maxDistanceMiles>' \
        '/<string:maxResults>/<string:minDifficulty>/<string:maxDifficulty>/', methods=["GET"])
def get_routes(location, maxDistanceMiles, maxResults, minDifficulty, maxDifficulty):
    lat, lon = parse_coordinates(location)
    try:
        height_sorted_routes = \
                GnarlyClimber.api.mtn_project_height_scraper.get_height_sorted_routes(
                lat, lon, maxDistanceMiles=maxDistanceMiles, maxResults=maxResults,
                minDifficulty=minDifficulty, maxDifficulty=maxDifficulty)
        success = True
    except Exception as e:
        height_sorted_routes = []
        success = False
        GnarlyClimber.app.logger.error(e)
    
    height_sorted_routes = GnarlyClimber.api.mtn_project_height_scraper.convert_list_of_routes_to_json(
            height_sorted_routes)
        
    context = {
        "height_sorted_routes": height_sorted_routes,
        "success" : success
    }
    return flask.jsonify(**context)

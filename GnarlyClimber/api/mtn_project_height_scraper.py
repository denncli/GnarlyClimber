from lxml import html
from requests import get
from requests.exceptions import HTTPError
import json
from bs4 import BeautifulSoup
from functools import total_ordering
import GnarlyClimber
import time

#TODO: store private key in credential store
MTN_PROJECT_PRIVATE_KEY = '200829148-b236255ec26c32a8f7d7c01b3f363bcc'

class RateLimiter:
    def __init__(self, minimumTimeBetweenExecution):
        self.minimumTimeBetweenExecution = minimumTimeBetweenExecution
        self.prevExecutionTime = None

    def stall_until_minimum_time_reached(self):
        if self.prevExecutionTime:
            cur_time = time.time()
            elapsed_time = cur_time - self.prevExecutionTime
            if elapsed_time < self.minimumTimeBetweenExecution:
                time_to_stall = self.minimumTimeBetweenExecution - elapsed_time
                time.sleep(time_to_stall)
        self.prevExecutionTime = time.time()


@total_ordering
class Route:
    def __init__(self, mtn_project_json_info, height_in):
        self.json_info = mtn_project_json_info
        self.height = height_in
    
    def get_height(self):
        return self.height
    
    def get_json_representation(self):
        json_dict = {'mtn_project_info': self.json_info, 'height': self.height}
        return json_dict
    
    def __lt__(self, other):
        return self.get_height() < other.get_height()
    
    def __eq__(self, other):
        return self.get_height() == other.get_height()
    
    def __str__(self):
        return "HEIGHT: {}ft".format(self.height) + ' ' + str(self.json_info['url'])

def convert_list_of_routes_to_json(route_list):
    json_list = []
    for route in route_list:
        json_list.append(route.get_json_representation())
    return json_list

#TODO: cache api results    
def get_routes_json_by_lat_lon(lat, lon, key=MTN_PROJECT_PRIVATE_KEY,
        maxDistanceMiles='', maxResults='', minDifficulty='', maxDifficulty=''):
    parameters = {"lat": lat, "lon": lon, "maxDistance": maxDistanceMiles, "maxResults": maxResults, 
            "minDiff": minDifficulty, "maxDiff": maxDifficulty, "key": key}
    api_url = 'https://www.mountainproject.com/data/get-routes-for-lat-lon'

    if GnarlyClimber.app.config['LIMIT_MTN_PROJECT_API_HIT_RATE']:
        GnarlyClimber.api.MTN_PROJECT_API_RATE_LIMITER.stall_until_minimum_time_reached()

    response = get(api_url, parameters)
    response.raise_for_status()
    return response.json()['routes']

def get_route_height_from_webpage(url):
    if GnarlyClimber.app.config['LIMIT_MTN_PROJECT_SCRAPE_RATE']:
        GnarlyClimber.api.MTN_PROJECT_SCRAPE_RATE_LIMITER.stall_until_minimum_time_reached()

    response = get(url)
    response.raise_for_status()
    raw_html = response.content
    parser = BeautifulSoup(raw_html, 'html.parser')
    description_details_table = parser.find("table", "description-details")
    text_line_with_height = str(description_details_table.findChild().contents[3])
    words_in_text_line_with_height =  text_line_with_height.split()
    index_of_ft_word = -1
    for i, word in enumerate(words_in_text_line_with_height):
        if word == 'ft':
            index_of_ft_word = i
    if index_of_ft_word <= 0:
        raise RuntimeError('Length of route not specified')
    else:
        height_in_ft = words_in_text_line_with_height[index_of_ft_word - 1]
        return int(height_in_ft)

def get_route_height_from_db(route_id):
    connection = GnarlyClimber.model.get_db()
    query_response = connection.execute(
        "SELECT height FROM route_heights "
        f"WHERE route_id=\'{route_id}\'"
    ).fetchall()
    if(not query_response):
        GnarlyClimber.app.logger.info(str(route_id) + " not found in db")
        return None
    else:
        GnarlyClimber.app.logger.info(str(route_id) + " found in db")
        return query_response[0]['height']

def update_db_with_route_height(route_id, height):
    connection = GnarlyClimber.model.get_db()
    connection.execute(
        f"INSERT INTO route_heights (route_id, height) VALUES (\'{route_id}\', \'{height}\')"
    )

def get_route_height(route_json):
    route_id = route_json['id']
    height = get_route_height_from_db(route_id)
    if height: 
        return height #height cached in db
    try:
        height = get_route_height_from_webpage(route_json['url']) #TODO: spawn a thread
        update_db_with_route_height(route_json['id'], height)
    except RuntimeError:
        #-1 in database denotes height not listed
        update_db_with_route_height(route_json['id'], -1)
        raise RuntimeError

    return height

#sort in descending order
def get_height_sorted_routes(lat, lon, key=MTN_PROJECT_PRIVATE_KEY,
                maxDistanceMiles='', maxResults='', minDifficulty='', maxDifficulty=''):
        try:
            routes = get_routes_json_by_lat_lon(
                    lat, lon, key, maxDistanceMiles, maxResults, minDifficulty, maxDifficulty)
        except HTTPError as e:
            GnarlyClimber.app.logger.error('Mountain project api returned an error status for this request!')
            GnarlyClimber.app.logger.error(e)
            raise HTTPError

        height_sorted_routes = []
        for route in routes:
            try:
                height = get_route_height(route)
                if height != -1:
                    routeWithHeight = Route(route, height)
                    height_sorted_routes.append(routeWithHeight)
            except (RuntimeError, HTTPError):
                #TODO: Increment counter of unfound heights. If it is large then there is an issue
                #height not found on page. likely unlisted
                pass

        height_sorted_routes.sort(reverse=True)
        return height_sorted_routes

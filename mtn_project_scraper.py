from lxml import html
from requests import get
from requests.exceptions import HTTPError
import json
from bs4 import BeautifulSoup
from functools import total_ordering

#TODO: store private key in credential store
MTN_PROJECT_PRIVATE_KEY = '200829148-b236255ec26c32a8f7d7c01b3f363bcc'

@total_ordering
class Route:
    def __init__(self, mtn_project_json_info, height_in):
        self.json_info = mtn_project_json_info
        self.height = height_in
    
    def get_height(self):
        return self.height
    
    def __lt__(self, other):
        return self.get_height() < other.get_height()
    
    def __eq__(self, other):
        return self.get_height() == other.get_height()
    
    def __str__(self):
        return "HEIGHT: {}ft".format(self.height) + ' ' + str(self.json_info['url'])

    
def get_routes_by_lat_lon(lat, lon, key=MTN_PROJECT_PRIVATE_KEY,
        maxDistanceMiles='', maxResults='', minDifficulty='', maxDifficulty=''):
    parameters = {"lat": lat, "lon": lon, "maxDistance": maxDistanceMiles,
            "minDiff": minDifficulty, "maxDiff": maxDifficulty, "key": key}
    api_url = 'https://www.mountainproject.com/data/get-routes-for-lat-lon'
    response = get(api_url, parameters)
    response.raise_for_status()
    return response.json()['routes']

def get_route_height(url):
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

#sort in descending order
def get_height_sorted_routes(lat, lon, key=MTN_PROJECT_PRIVATE_KEY,
                maxDistanceMiles='', maxResults='', minDifficulty='', maxDifficulty=''):
        try:
            routes = get_routes_by_lat_lon(
                    lat, lon, key, maxDistanceMiles, maxResults, minDifficulty, maxDifficulty)
        except HTTPError as e:
            #TODO: handle this exception for client without exiting
            print('Mountain project api returned an error status for this request!')
            print(e)
            exit(1)

        height_sorted_routes = []
        for route in routes:
            route_url = route['url']
            try:
                height = get_route_height(route_url)
                routeWithHeight = Route(route, height)
                height_sorted_routes.append(routeWithHeight)
            except (RuntimeError, HTTPError):
                #TODO: Increment counter of unfound heights. If it is large then there is an issue
                #height not found on page. likely unlisted
                pass

        height_sorted_routes.sort(reverse=True)
        for route in height_sorted_routes:
            print(route)


#print(get_routes_by_lat_lon(lat=39,lon=-77.2))
#get_route_height('https://www.mountainproject.com/route/106051051/slanty-crack')
#get_route_height('https://www.mountainproject.com/route/116715747/the-father')
#get_route_height('https://www.mountainproject.com/route/116715799/roto')
get_height_sorted_routes(39, -77.2, minDifficulty='V0', maxDifficulty='V17', maxDistanceMiles=100)

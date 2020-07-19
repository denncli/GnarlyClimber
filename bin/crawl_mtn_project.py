from requests import get

def crawl_mtn_project_boulders(south_lat, north_lat, west_lon, east_lon):
    south_lat = int(south_lat) + 1
    north_lat = int(north_lat) + 1
    west_lon = int(west_lon) + 1
    east_lon = int(east_lon) + 1
    #increment by 1 degree (~66miles). Get everything within 200mi radius
    for lat in range(south_lat, north_lat + 1):
        for lon in range(west_lon, east_lon + 1):
            api_url = 'http://localhost:8000/api/height/{}/{}/{}/{}/{}/{}/'.format(
                lat, lon, 200, 500, 'V0', 'V17' 
            )
            response = get(api_url)
            response.raise_for_status()


def crawl_united_states():
    US_NORTHERNMOST_LATITUDE = 49.0
    US_SOUTHERNMOST_LATITUDE = 24.0
    US_EASTERNMOST_LONGITUDE = -66.0
    US_WESTERNMOST_POINT = -125.0

    #split in fifths to avoid overloading MP servers
    us_total_latitude_fifth = (US_EASTERNMOST_LONGITUDE - US_WESTERNMOST_POINT) / 5
    crawl_mtn_project_boulders(US_SOUTHERNMOST_LATITUDE, US_NORTHERNMOST_LATITUDE, 
            US_WESTERNMOST_POINT + 2 * us_total_latitude_fifth, US_WESTERNMOST_POINT + 3 * us_total_latitude_fifth)

crawl_united_states()

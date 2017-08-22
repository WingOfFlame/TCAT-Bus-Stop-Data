from bs4 import BeautifulSoup
import requests
import json

from pathlib import Path



BASE_URL = "https://realtimetcatbus.availtec.com/InfoPoint/Minimal"
STOPS_BY_ROUTE = "/Stops/ForRoute?routeId="
TIMES_BY_STOP = "/Departures/ForStop?stopId="

def parse_route_colors():
    colors = {}

    with open('color.html', 'r') as f:
        page = BeautifulSoup(f.read(), 'html.parser')

        colors_raw = page.find_all('div', class_='route-abbr')
        for c in colors_raw:
            code = (c.get('style').split(';')[0]).split(':')[1].strip()
            route = c.text.split(' ')[1].strip()
            colors[route]=code

    return colors

def fetch_routes():
    r = requests.get(BASE_URL)
    routes = []

    if r.status_code != 200:
        return routes

    page = BeautifulSoup(r.text, 'html.parser')
    routes_raw = page.find_all('a')[0:-1]

    print("%d routes found" % (len(routes_raw)))
    for route in routes_raw:
        route_dict = {'id': route.get('routeid'), 'name': route.text, 'color':COLORS_DICT[route.get('routeid')]} #'href': route.get('href'),
        routes.append(route_dict)

    return routes

def fetch_stops_by_route(routeid):
    r = requests.get(BASE_URL + STOPS_BY_ROUTE + routeid)
    stops = {}

    if r.status_code != 200:
        return stops

    page = BeautifulSoup(r.text, 'html.parser')
    stops_raw = page.find_all('a')[0:-1][1::2]  # only cares every second line

    print("%d stops found for route %s" %(len(stops_raw), routeid))
    for stop in stops_raw:
        stops[stop.get('stopid')] = stop.text

    return stops

def fetch_stops():
    route_stop_dict={}
    stops_dict={}

    for r in ROUTES:
        stops = fetch_stops_by_route(r['id'])
        route_stop_dict[r['id']]=list(stops.keys())
        stops_dict.update(stops)

    stops=[]
    for key in sorted(stops_dict.keys()):
        stops.append({'id':key, 'name': stops_dict[key]})

    print("%d stops found"%(len(stops)))
    return route_stop_dict, stops


''' Getting local/manual data '''
# color code for routes
my_file = Path("./color.json")
if not my_file.is_file():
    COLORS_DICT = parse_route_colors()
    with open('color.json', 'w') as fp:
        json.dump(COLORS_DICT, fp)
else:
    with open('color.json', 'r') as fp:
        COLORS_DICT = json.load(fp)



''' Getting info online'''
ROUTES = fetch_routes()     # all routes
ROUTE_STOP_DICT, STOPS = fetch_stops()  # stops of each routes and consolidated stop lists

with open('route.json', 'w') as fp:
    json.dump(ROUTES, fp)

with open('route-stop.json', 'w') as fp:
    json.dump(ROUTE_STOP_DICT, fp)

with open('stop.json', 'w') as fp:
    json.dump(STOPS, fp)



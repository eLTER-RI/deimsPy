import codecs
import csv
import json
import re
import sys
import urllib.request

import geopandas
import geopy.distance


def getListOfSites(network=None,verified_only=False):
    """Get all site records on DEIMS-SDR and return a list of IDs.

    'network' must be the ID of a network. If provided, only sites from
    that network are returned. Defaults to None.

    'verified_only' must be a boolean. If True, only verified members of
    the network are returned. Ignored if 'network' not supplied.
    Defaults to False.
    """
    csv.field_size_limit(sys.maxsize)

    # set API URL based on input
    if network is not None:
        if verified_only:
            url = f"https://deims.org/api/sites?format=csv&network={network}&verified={str(verified_only).lower()}"
        else:
            url = f"https://deims.org/api/sites?format=csv&network={network}"
    else:
        url = "https://deims.org/api/sites?format=csv"

    # connect to DEIMS REST-API
    csv_stream = urllib.request.urlopen(url)
    csvfile = csv.reader(codecs.iterdecode(csv_stream, 'utf-8'), delimiter=';')
    next(csvfile) # ignore first row

    # load all site records into one object
    list_of_sites = []
    for line in csvfile:
        list_of_sites.append(line[2])

    # returns list of UUIDs
    return list_of_sites


def getSiteById(site_id):
    """Get complete record of site with ID site_id and return as a
    dictionary.

    'site_id' is the only, mandatory argument and must be a valid DEIMS
    ID.
    """
    # make sure we have a well-formed deims_id suffix
    deims_id_suffix = normaliseDeimsID(site_id)

    # construct URL
    site_json_url = "https://deims.org/api/sites/" + deims_id_suffix

    # open URL and parse as json
    with urllib.request.urlopen(site_json_url) as f:
        parsed_site_json = json.loads(f.read().decode("utf-8"))

    # optional processing steps
    # ...

    # returns entire site records as dict
    return parsed_site_json


def normaliseDeimsID(deims_id):
    """Extract standardised ID from input string. Returns ID as string
    of the form '00000000-0000-0000-0000-000000000000' or raises
    RuntimeError if no ID found.
    """
    # extract ID from lowercased string via regex
    # returns the first match only
    normalised_deims_id = re.search(r"([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})",deims_id.lower())
    if normalised_deims_id:
        return normalised_deims_id.group(1)
    else:
        raise RuntimeError("no ID found")


def getSitesWithinRadius(lat, lon, distance):
    """Get all site records on DEIMS-SDR that are within a given radius
    of a point. Returns a list of sites consisting of the DEIMS.iD
    and the distance to the input coordinates in meters.
    """
    gdf = geopandas.GeoDataFrame(
            df, geometry=geopandas.points_from_xy(x=[lon], y=[lat], crs="EPSG:4326").to_crs(3857)
        )

    bounding_box = gdf.geometry.buffer(distance).to_crs(4326).bounds

    bounding_box_string = str(bounding_box['miny'][0]) + ',' + str(bounding_box['minx'][0]) +  ',' + str(bounding_box['maxy'][0]) +  ',' + str(bounding_box['maxx'][0])
    query_string = 'https://deims.org/geoserver/deims/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=deims%3Adeims_all_sites&outputFormat=application%2Fjson&srsName=EPSG:3857&bbox=' + bounding_box_string + ',urn:ogc:def:crs:EPSG:4326'

    # open URL and parse as json
    with urllib.request.urlopen(query_string) as f:
        parsed_results_json = json.loads(f.read().decode("utf-8"))

    if parsed_results_json['totalFeatures']>0:
        results = [];
        for site in parsed_results_json['features']:
            current_distance = geopy.distance.geodesic((lat,lon),(site['properties']['field_coordinates_lat'],site['properties']['field_coordinates_lon']))
            if (current_distance < distance):
                results.append([normaliseDeimsID(site['properties']['deimsid']), round(current_distance.meters)])
            else:
                continue
        return sorted(results, key=lambda x: x[1])
    else:
        return None

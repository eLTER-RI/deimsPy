"""A module for interacting with the DEIMS-SDR API.
The main functions exported are:
    - getListOfSites
    - getSiteById
    - getSitesWithinRadius
    - getSiteBoundaries
    - getSiteCoordinates

See the respective functions' help or the README for more information.
"""


import codecs
import csv
import json
import re
import sys
import urllib.request

import geopandas
import geopy.distance
import pandas


def getListOfSites(network=None,verified_only=False):
    """Get all site records on DEIMS-SDR and return a list of DEIMS.IDs.
    'network' must be the ID of a network. If provided, only sites from
    that network are returned. Defaults to None.
    'verified_only' must be a boolean. If True, only verified members of
    the network are returned. Ignored if 'network' not supplied.
    Defaults to False.
    """
    csv.field_size_limit(2 ** 31 - 1)

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
    """Get complete record of a site and return as a dictionary.
    'site_id' is the only, mandatory argument and must be a valid
    DEIMS.ID.
    """
    # make sure we have a well-formed DEIMS.ID suffix
    deims_id_suffix = _normaliseDeimsID(site_id)

    # construct URL
    site_json_url = "https://deims.org/api/sites/" + deims_id_suffix

    # open URL and parse as json
    with urllib.request.urlopen(site_json_url) as f:
        parsed_site_json = json.loads(f.read().decode("utf-8"))

    # optional processing steps
    # ...

    # returns entire site records as dict
    return parsed_site_json


def _normaliseDeimsID(deims_id):
    """Extract standardised DEIMS.ID suffix from input string.
    'deims_id' is the only, mandatory argument and must be a valid
    DEIMS.ID.
    Returns a string of the form '00000000-0000-0000-0000-000000000000'
    or raises a RuntimeError if no DEIMS.ID suffix is found.
    """
    # extract ID from lowercased string via regex
    # returns the first match only
    normalised_deims_id = re.search(r"([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})",deims_id.lower())
    if normalised_deims_id:
        return normalised_deims_id.group(1)
    else:
        raise RuntimeError("no ID found")


def getSitesWithinRadius(lat, lon, distance):
    """Get all sites within a given distance of a point.
    'lat' and 'lon' should be coordinates in degrees describing a point
    to search from.
    'distance' should be the number of metres from the point to search.
    Returns a list of (DEIMS.ID, distance to input coordinates in
    meters) tuples or None if no sites are found.
    """
    # construct GeoDataFrame from input coordinates
    gdf = geopandas.GeoDataFrame(
            geometry=geopandas.points_from_xy(x=[lon], y=[lat], crs="EPSG:4326").to_crs(3857)
        )
    
    # construct query URL from bounding box centred on input point
    bounding_box = gdf.geometry.buffer(distance).to_crs(4326).bounds
    bounding_box_string = str(bounding_box['miny'][0]) + ',' + str(bounding_box['minx'][0]) +  ',' + str(bounding_box['maxy'][0]) +  ',' + str(bounding_box['maxx'][0])
    query_string = 'https://deims.org/geoserver/deims/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=deims%3Adeims_all_sites&outputFormat=application%2Fjson&srsName=EPSG:3857&bbox=' + bounding_box_string + ',urn:ogc:def:crs:EPSG:4326'

    # open URL and parse as json
    with urllib.request.urlopen(query_string) as f:
        parsed_results_json = json.loads(f.read().decode("utf-8"))

    if parsed_results_json['totalFeatures']>0:
        # sites were returned but need distance checking still
        results = [];
        for site in parsed_results_json['features']:
            current_distance = geopy.distance.geodesic((lat,lon),(site['properties']['field_coordinates_lat'],site['properties']['field_coordinates_lon']))
            if (current_distance < distance):
                results.append([_normaliseDeimsID(site['properties']['deimsid']), round(current_distance.meters)])
            else:
                continue
        return sorted(results, key=lambda x: x[1])
    else:
        # no sites returned
        return None


def getSiteBoundaries(site_ids, filename=None):
    """Get all available boundaries for one or more sites.
    'site_ids' can either be a string featuring the DEIMS.ID or a
    list of ids as returned by other functions in this package.
    If 'filename' is provided, output will be saved as a shapefile.
    Otherwise, it is returned as a GeoDataFrame.
    """

    # ensure input is a list
    if isinstance(site_ids, str):
        site_ids = [site_ids]

    # initialise GeoDataFrame
    list_of_boundaries = geopandas.GeoDataFrame(columns=['name', 'deimsid', 'field_elev', 'geometry'], geometry='geometry').set_crs(4326)
    
    # get boundaries
    for site_id in site_ids:
        current_boundary = geopandas.read_file("https://deims.org/geoserver/deims/ows?service=WFS&version=2.0.0&request=GetFeature&typeName=deims:deims_sites_boundaries&srsName=EPSG:4326&CQL_FILTER=deimsid=%27https://deims.org/" + _normaliseDeimsID(site_id) + "%27&outputFormat=SHAPE-ZIP").to_crs(4326)
        list_of_boundaries = pandas.concat([list_of_boundaries, current_boundary])

    # save file
    if (filename):
        list_of_boundaries.to_file(filename + ".shp")
    else:
        return list_of_boundaries


def getSiteCoordinates(site_ids, filename=None):
    """Get all available coordinates for one or more sites.
    'site_ids' can either be a string featuring the DEIMS.ID or a
    list of ids as returned by other functions in this package.
    If 'filename' is provided, output will be saved as a shapefile.
    Otherwise, it is returned as a GeoDataFrame.
    """

    # ensure input is a list
    if isinstance(site_ids, str):
        site_ids = [site_ids]

    # initialise GeoDataFrame
    list_of_coordinates = geopandas.GeoDataFrame(columns=['name', 'deimsid', 'field_elev', 'geometry'], geometry='geometry').set_crs(4326)
    
    # get coordinates
    for site_id in site_ids:
        current_coordinates = geopandas.read_file("https://deims.org/geoserver/deims/ows?service=WFS&version=2.0.0&request=GetFeature&typeName=deims:deims_qa_sites&srsName=EPSG:4326&CQL_FILTER=deimsid=%27https://deims.org/" + _normaliseDeimsID(site_id) + "%27&outputFormat=SHAPE-ZIP").to_crs(4326)
        list_of_coordinates = pandas.concat([list_of_coordinates, current_coordinates])

    # save file
    if (filename):
        list_of_coordinates.to_file(filename + ".shp")
    else:
        return list_of_coordinates

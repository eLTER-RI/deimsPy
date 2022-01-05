import csv
import urllib.request
import codecs
import sys
import json
import re


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

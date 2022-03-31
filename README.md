# deimsPy

This repository represents the latest version of a collection of python functions with the intention of easing access to DEIMS-SDR data (www.deims.org).
This python package is openly available and free to use. Should you use DEIMS-SDR data for any studies or analyses, please cite the service accordingly.
For further information about DEIMS-SDR, please refer to its About page (www.deims.org/about).

## Installation

Via pip (see the package on [PyPI](https://pypi.org/project/deims/)): `pip install deims`.
Manually: download `deims.py` to working directory.

You can then `import deims` as normal.

## Usage

Get the list of all verified site of a network, e.g. ECN
- deims.getListOfSites(network="a197664f-569e-4df6-933a-86de676dbfc5",verified_only=True)

Get the list of all network sites (verified and not verified), e.g. LTER Austria
- deims.getListOfSites("d45c2690-dbef-4dbc-a742-26ea846edf28")

Get the list of all sites
- deims.getListOfSites()

Get a particular site record by its DEIMS.ID (multiple formats of the DEIMS.ID are accepted)
- deims.getSiteById(site_id="deims.org/8eda49e9-1f4e-4f3e-b58e-e0bb25dc32a6")
- deims.getSiteById("1b94503d-285c-4028-a3db-bc78e31dea07")

Get all sites on DEIMS within 30km of latitude 47.84, longitude 14.44
- deims.getSitesWithinRadius(lat=47.84,lon=14.44,distance=30000)

Get all sites on DEIMS within 1500m of latitude 57.08, longitude -3.667
- deims.getSitesWithinRadius(57.08,-3.667,1500)

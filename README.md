# deimsPy

This repository represents the latest version of a collection of python functions with the intention of easing access to DEIMS-SDR data (www.deims.org).
This python package is openly available and free to use. Should you use DEIMS-SDR data for any studies or analyses, please cite the service accordingly.
For further information about DEIMS-SDR, please refer to its About page (www.deims.org/about).

## Usage

Get the list of all verified site of a network, e.g. ECN<br>
- getListOfSites(network="a197664f-569e-4df6-933a-86de676dbfc5",verified_only=True)

Get the list of all network sites (verified and not verified), e.g. LTER Austria<br>
- getListOfSites(network="d45c2690-dbef-4dbc-a742-26ea846edf28")

Get a particular site record by its DEIMS.iD (multiple formats of the deims.iD are accepted)<br>
- getSiteById("deims.org/8eda49e9-1f4e-4f3e-b58e-e0bb25dc32a6")<br>
- getSiteById("8eda49e9-1f4e-4f3e-b58e-e0bb25dc32a6")

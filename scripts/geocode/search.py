import logging
import os
from typing import *

import requests
from marshmallow.utils import EXCLUDE

from schemas import *

AUCKLAND_BOUNDS = [-37.364473, -35.698392, 173.896328, 175.903215]


def search_osm(
    params: Dict[str, Any],
    bounds: List[float] = None,
    bounded: bool = True,
) -> List[Place]:
    logging.info(f"Searching OSM: '{params}', bounds={bounds}")
    all_params = params | {
        "countrycodes": "nz",
        "addressdetails": 1,
        "format": "jsonv2",
    }
    if bounds is not None:
        all_params["viewbox"] = ",".join([str(x) for x in bounds])

    r = requests.get("https://nominatim.openstreetmap.org/search.php", all_params)
    results = Place.Schema().load(r.json(), many=True, partial=True, unknown=EXCLUDE)
    if bounded and bounds is not None:
        x1, x2, y1, y2 = bounds
        return list(filter(lambda p: x1 <= p.lat <= x2 and y1 <= p.lon <= y2, results))
    return results


def search_google(
    params: Dict[str, Any],
    bounds: List[float] = None,
    bounded: bool = True,
):
    logging.info(f"Searching Google Maps: '{params}', bounds={bounds}")
    all_params = params | {
        "components": "country:NZ|administrative_area:Auckland",
        "key": os.environ["GCLOUD_API_KEY"],
    }
    if bounds is not None:
        all_params["bounds"] = f"{bounds[0]},{bounds[3]}|{bounds[1]},{bounds[2]}"

    r = requests.get("https://maps.googleapis.com/maps/api/geocode/json", all_params)
    response = r.json()
    if response["status"] not in ["OK", "ZERO_RESULTS"]:
        logging.error(response)

    results = response["results"]
    if bounded and bounds is not None:
        x1, x2, y1, y2 = bounds
        return list(
            filter(
                lambda r: x1 <= float(r["geometry"]["location"]["lat"]) <= x2
                and y1 <= float(r["geometry"]["location"]["lng"]) <= y2,
                results,
            )
        )
    return results

import logging
from os.path import splitext
import re
from argparse import ArgumentParser
from glob import glob
from itertools import chain
from typing import *

from pathlib import Path
import requests_cache

from file_io import *
from schemas import *
from search import *


def main(paths: List[str], output_dir: str):
    streets = load_streets(paths)
    suburb_names = set(chain.from_iterable([s.parsed_suburbs for s in streets]))
    suburbs = {n: geocode_suburb(n) for n in suburb_names}
    results: List[Any] = []
    unmatched_streets: List[Street] = []

    num_streets = float(len(streets))
    count = 1

    for street in streets:
        progress = round(100 * count / num_streets, 2)
        logging.info(f"[{progress}%] Locating street {count}/{int(num_streets)}")
        if street.parsed_street == "IGNORE":
            continue
        elif re.search(r"[A-Za-z]", street.parsed_street) is None:
            results.append(GeocodedStreet.from_coords(street).to_array())
        else:
            geocoded_street = geocode_street(street, suburbs)
            if geocoded_street is None:
                unmatched_streets.append(street)
            else:
                results.append(geocoded_street.to_array())
        count += 1

    missing = len(unmatched_streets)
    logging.info(
        f"{missing}/{int(num_streets)} ({round(100*missing/num_streets, 2)}%) results are missing. Saving..."
    )

    output_name = "-".join(Path(p).stem for p in paths)
    save_json(f"{output_dir}/{output_name}.json", results)
    save_json(f"{output_dir}/{output_name}_unmatched.json", unmatched_streets)
    logging.info("Done.")


def geocode_suburb(name: str) -> Suburb:
    results = search_osm({"q": f"{name}, Auckland"}, AUCKLAND_BOUNDS)
    for place in results:
        if place.type == "suburb" and "city" in place.address:
            return Suburb.new(place.address["suburb"], place)
    for place in results:
        if place.type == "administrative" and "city" in place.address:
            return Suburb.new(place.display_name.split(",")[0], place)
    for place in results:
        if place.type == "island":
            return Suburb.new(place.display_name.split(",")[0], place)
    for place in results:
        if "suburb" in place.address:
            return geocode_suburb(place.address["suburb"])
    assert False, f"Suburb not found: {name}"


# TODO: geocoding regions like suburbs
# TODO: better parsed streets. parse all streets, loop in order?
# TODO: if we don't find anything, just attach it to the suburb perhaps


def geocode_street(street: Street, suburbs: Dict[str, Suburb]) -> GeocodedStreet:
    for sub in street.parsed_suburbs:
        place = geocode_street_suburb(street, suburbs.get(sub))
        if place is not None:
            return place
    logging.warning(f"Street not found: {street}")


def geocode_street_suburb(street: Street, suburb: Suburb) -> GeocodedStreet:
    results = search_osm(
        {
            "street": street.parsed_street,
            "city": suburb.district,
            "state": "Auckland",
        },
        bounds=suburb.bounds,
    )
    if len(results) > 0:
        return GeocodedStreet.from_osm(street, results[0])

    district = suburb.district
    if district is None:
        district = suburb.suburb
    district_results = search_osm({"q": f"{suburb.district}, Auckland"}, bounds=AUCKLAND_BOUNDS)
    results = search_google(
        {"address": f"{street.parsed_street}, {suburb.suburb}, Auckland"},
        bounds=district_results[0].boundingbox,
    )
    if len(results) > 0:
        return GeocodedStreet.from_google(street, results[0])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = ArgumentParser()
    parser.add_argument(
        "-s",
        "--streets",
        help="Glob for street JSON files",
        default="data/streets/auckland_city.json",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        help="Directory to save results in",
        default="scripts/geocode/results",
    )
    parser.add_argument(
        "-c",
        "--cache",
        help="Use requests cache",
        default=True,
    )

    args = parser.parse_args()
    if args.cache is True:
        requests_cache.install_cache("data/requests_cache")
    main(glob(args.streets), args.output_dir)

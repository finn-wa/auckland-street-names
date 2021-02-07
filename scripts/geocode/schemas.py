import re
from dataclasses import field
from typing import *

from marshmallow import Schema
from marshmallow_dataclass import dataclass


class SchemaType:
    """Base class for marshmallow dataclasses. Adds Schema field."""

    Schema: ClassVar[Type[Schema]] = Schema


@dataclass
class Street(SchemaType):
    PARSED_STREET_PATTERN = re.compile(r"(?<=[Nn]ow )([a-z\s]*?)([A-Z]+[a-z]+.?)+", re.MULTILINE)

    street: str
    info: str
    suburb: str
    parsed_street: str = field(default=None)
    parsed_suburbs: List[str] = field(default_factory=list)

    @staticmethod
    def clean(s: str) -> str:
        s = re.sub(r"\s+", " ", s)
        s = re.sub(r",|\.", " ", s)
        return s.strip()

    def __post_init__(self):
        self.street = self.clean(self.street)
        if len(self.parsed_suburbs) == 0:
            if ";" in self.suburb:
                suburbs = self.clean(self.suburb).split(";")
            else:
                suburbs = self.clean(self.suburb).split("/")
            self.parsed_suburbs = [self.clean(s) for s in suburbs]
        if self.parsed_street is None:
            match = self.PARSED_STREET_PATTERN.search(self.info)
            if match:
                self.parsed_street = self.clean(match.group(0).removeprefix(match.group(1)))
            else:
                self.parsed_street = self.street


@dataclass
class Place(SchemaType):
    place_id: int
    type: str
    boundingbox: List[float]
    lat: float
    lon: float
    display_name: str
    address: Dict[str, str]


@dataclass
class Suburb(SchemaType):
    suburb: str
    bounds: List[float]
    district: str = field(default=None)

    @staticmethod
    def new(name: str, place: Place):
        if "city" in place.address:
            district = place.address["city"]
        else:
            district = None
        return Suburb(suburb=name, bounds=place.boundingbox, district=district)


@dataclass
class GeocodedStreet(SchemaType):
    street: str
    info: str
    lat: float
    lon: float
    address: str

    @staticmethod
    def from_osm(street: Street, place: Place):
        return GeocodedStreet(
            street=street.street,
            info=street.info,
            lat=place.lat,
            lon=place.lon,
            address=place.display_name,
        )

    @staticmethod
    def from_google(street: Street, place: Dict[str, Any]):
        return GeocodedStreet(
            street=street.street,
            info=street.info,
            lat=place["geometry"]["location"]["lat"],
            lon=place["geometry"]["location"]["lng"],
            address=place["formatted_address"],
        )

    @staticmethod
    def from_coords(street: Street):
        lat, lon = re.sub(r"\s", "", street.parsed_street).split(",")
        return GeocodedStreet(
            street=street.street,
            info=street.info,
            lat=float(lat),
            lon=float(lon),
            address=f"{street.street}, {street.suburb}, Auckland",
        )

    def to_array(self) -> List[Any]:
        return [round(self.lat, 7), round(self.lon, 7), self.street, self.info]

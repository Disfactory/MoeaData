import shelve

from . import data
from .normalizer import Normalizer
from .tokenlizer import Tokenlizer


class SectCodeConverter:
    normalizer: Normalizer
    tokenlizer: Tokenlizer
    towncode_to_countycode: shelve.Shelf[str]
    countyname_to_countycode: shelve.Shelf[str]

    def __init__(self):
        self.normalizer = Normalizer()

        self.countyname_to_countycode = data.load_county_data()
        self.townname_to_towncode = data.load_town_data()
        self.towncode_to_countycode = data.load_towncode_to_countycode()

        city_list = list(self.countyname_to_countycode.keys())
        town_list = list(self.townname_to_towncode.keys())

        self.tokenliizer = Tokenlizer(city_list, town_list)

    def convert(self, address: str) -> str:
        address = self.normalizer.execute(address)
        address_tokens = self.tokenliizer.execute(address)
        print(address_tokens)

        county_code = self.countyname_to_countycode.get(address_tokens.county, "")
        town_code = self.townname_to_towncode.get(address_tokens.town, "")

        if county_code == "" and town_code:
            county_code = self.towncode_to_countycode.get(town_code, "")

        if county_code == "" or town_code == "":
            raise ValueError(
                f"{address} City code {address_tokens.county} or town code {address_tokens.town} is not found"
            )

        sectname_to_sectcode = data.load_sectname_to_sectcode(county_code, town_code)
        sect_code = sectname_to_sectcode.get(address_tokens.sect, {}).get(
            "sectcode", ""
        )

        print(f"{county_code} {town_code} {sect_code} {address_tokens.land}")
        return ""

import shelve

from . import data
from .normalizer import Normalizer
from .tokenlizer import Tokenlizer


class SectCode:
    county_code: str
    town_code: str
    sect_code: str
    land_numbers: list[str]

    def __init__(self, county_code, town_code, sect_code, land_numbers):
        self.county_code = county_code
        self.town_code = town_code
        self.sect_code = sect_code
        self.land_numbers = land_numbers


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

    def convert(self, address: str) -> SectCode:
        address = self.normalizer.execute(address)
        address_tokens = self.tokenliizer.execute(address)

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

        land_numbers = []
        land_tokens = address_tokens.land.value.split("、")

        for token in land_tokens:
            if token == "":
                continue

            # Special case for 956至960
            if "至" in token:
                start, end = token.split("至")
                land_numbers.extend([i for i in range(int(start), int(end) + 1)])
                continue

            digits = token.split("-")
            if len(digits) == 2:
                land_numbers.append(f"{int(digits[0]):04d}{int(digits[1]):04d}")
            elif len(digits) == 1:
                land_numbers.append(f"{int(digits[0]):04d}0000")
            else:
                print(f"Invalid land number {token}")

        return SectCode(county_code, town_code, sect_code, land_numbers)

import re


class Token:
    value: str
    unit: str

    def __init__(self, value: str = "", unit: str = ""):
        self.value = value
        self.unit = unit

    def __repr__(self):
        return f"{self.value}{self.unit}"


class AddressToken:
    county: str
    town: str
    sect: str
    land: Token

    def __init__(self):
        self.county = ""
        self.town = ""
        self.sect = ""
        self.land = Token()

    def __repr__(self):
        return ",".join(
            [self.county, self.town, self.sect, self.land.value, self.land.unit]
        ).strip()


class Tokenlizer:
    token_regex: re.Pattern

    def __init__(self, county_list: list[str], town_list: list[str]):
        self.county_token_regex = re.compile(
            f"""(?P<value>{"|".join(county_list)})""",
            re.X,
        )

        self.town_token_regex = re.compile(
            f"""(?P<value>{"|".join(town_list)})""",
            re.X,
        )

        self.sect_token_regex = re.compile(
            f"""(?P<value>.+)(?P<unit>地段|小段|區段|鎮段|段)""",
            re.X,
        )

        self.land_token_regex = re.compile(
            f"""(?P<value>.+?)(?P<unit>地號|號)""",
            re.X,
        )

    def execute(self, text) -> AddressToken:
        address_token = AddressToken()

        def replace_county_token(m: re.Match):
            if m.groups():
                address_token.county = m.group("value")
            return ""

        def replace_town_token(m: re.Match):
            if m.groups():
                address_token.town = m.group("value")

            return ""

        def replace_sect_token(m: re.Match):
            if m.groups():
                address_token.sect = m.group("value") + m.group("unit")
            return ""

        def replace_land_token(m: re.Match):
            if m.groups() and address_token.land.value == "":
                address_token.land.value = m.group("value")
                address_token.land.unit = m.group("unit")
            return ""

        sub_address = self.county_token_regex.sub(replace_county_token, text)
        sub_address = self.town_token_regex.sub(replace_town_token, sub_address)
        sub_address = self.sect_token_regex.sub(replace_sect_token, sub_address)
        sub_address = self.land_token_regex.sub(replace_land_token, sub_address)

        return address_token

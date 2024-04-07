import os
import shelve
import xml.etree.ElementTree as ET
from typing import KeysView, ValuesView

import requests

ROOT_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(ROOT_DIR, "data")

COUNTY_CODE_API = "https://api.nlsc.gov.tw/other/ListCounty"
COUNTY_DB_PATH = os.path.join(DATA_DIR, "county")

TOWN_CODE_API = "https://api.nlsc.gov.tw/other/ListTown/{county}"
TOWN_DB_PATH = os.path.join(DATA_DIR, "town")
TOWN_CODE_TO_COUNTY_CODE_DB_PATH = os.path.join(DATA_DIR, "towncode_to_countycode")

LAND_SECTION_API = "https://api.nlsc.gov.tw/other/ListLandSection/{county}/{town}"


def download_county_data(file_path: str):
    resp = requests.get(COUNTY_CODE_API)
    root = ET.fromstring(resp.text)

    result = shelve.open(file_path, writeback=True)
    for countyItem in root:
        countyJson = {}
        for item in countyItem:
            countyJson[item.tag] = item.text

        result[countyJson["countyname"]] = countyJson["countycode"]

    result.close()


def load_county_data() -> shelve.Shelf[str]:
    return shelve.open(COUNTY_DB_PATH, writeback=False)


def download_town_data(
    county_code_list: KeysView[str] | ValuesView[str], file_path: str
):
    townname_to_towncode = shelve.open(file_path, writeback=True)
    towncode_to_county_code = shelve.open(
        TOWN_CODE_TO_COUNTY_CODE_DB_PATH, writeback=True
    )
    for code in county_code_list:
        url = TOWN_CODE_API.format(county=code)
        resp = requests.get(url)

        root = ET.fromstring(resp.text)
        for townItem in root:
            townJson = {}
            for item in townItem:
                townJson[item.tag] = item.text

            townname_to_towncode[townJson["townname"]] = townJson["towncode"]
            towncode_to_county_code[townJson["towncode"]] = code

    townname_to_towncode.close()
    towncode_to_county_code.close()


def load_town_data() -> shelve.Shelf[str]:
    return shelve.open(TOWN_DB_PATH, writeback=False)


def load_towncode_to_countycode() -> shelve.Shelf[str]:
    return shelve.open(TOWN_CODE_TO_COUNTY_CODE_DB_PATH, writeback=False)


def load_sectname_to_sectcode(county_code: str, town_code: str) -> shelve.Shelf[dict]:
    return shelve.open(
        generate_land_section_file_path(county_code, town_code), writeback=False
    )


def download_sect_land_data(county_code: str, town_code: str, file_path: str):
    url = LAND_SECTION_API.format(county=county_code, town=town_code)
    resp = requests.get(url)

    root = ET.fromstring(resp.text)
    result = shelve.open(file_path, writeback=True)

    for landSectionItem in root:
        landSectionJson = {}
        for item in landSectionItem:
            landSectionJson[item.tag] = item.text

        result[landSectionJson["sectstr"]] = landSectionJson

    result.close()


def generate_land_section_file_path(county_code: str, town_code: str) -> str:
    return os.path.join(DATA_DIR, f"{county_code}_{town_code}")


def check_db_exists(db_path: str) -> bool:
    db_data_path = db_path + ".dat"
    if os.path.exists(db_data_path):
        return True

    return False


def init():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not check_db_exists(COUNTY_DB_PATH):
        download_county_data(COUNTY_DB_PATH)

    county_code_list = load_county_data().values()

    if not check_db_exists(TOWN_DB_PATH):
        download_town_data(county_code_list, TOWN_DB_PATH)

    town_data = load_town_data()

    for town_code in town_data.values():
        county_code = town_code[:1]
        file_path = generate_land_section_file_path(county_code, town_code)
        if not check_db_exists(file_path):
            download_sect_land_data(
                county_code,
                town_code,
                file_path,
            )


def get_tokenlize_regex():
    town_list = load_town_data()
    town_name_list = town_list.keys()
    # Remove the last word "鄉鎮市區" from the town name
    town_name_list = list(map(lambda x: x[:-1], town_name_list))

    token_regex = f"""
        (?:
            (?P<value>{"|".join(town_name_list)}|.+?)
        )
        (?:
            (?P<unit>地號|地段|小段|區段|鎮段|鎮區|市區|縣|市|鄉|鎮|市|村|里|區|段|號)
        )
    """
    return token_regex


if __name__ == "__main__":
    init()
    token_regex = get_tokenlize_regex()
    print(token_regex)

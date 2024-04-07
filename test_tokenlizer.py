from sect import data, normalizer, tokenlizer

if __name__ == "__main__":
    n = normalizer.Normalizer()

    city_list = list(data.load_county_data().keys())
    town_list = list(data.load_town_data().keys())
    parser = tokenlizer.Tokenlizer(city_list, town_list)

    # address = "雲林縣口湖鄉梧北段二五四之四十三、二五四之四十六地號"
    # address = "朴子市母寮段竹村小段581地號"
    address = "烏日區北里段277地號"
    address = n.execute(address)
    print(address)
    address = parser.execute(address)
    print(address)

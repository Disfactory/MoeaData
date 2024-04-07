import json

import pandas as pd

from sect.sectcode import SectCodeConverter

sheet_name_list = [
    "11201",
    "11202",
    "11203",
    "11205",
    "11206",
    "11207",
    "11208",
    "11209",
    "11210",
    "11211",
    "11212",
]

ROW_NAME: dict[str, str] = {
    "id": "ID",
    "number": "編號",
    "city": "市縣",
    "sectname": "地號",
    # "sectcode": "地號代碼",
    "usage_zone": "使用分區",
    "use": "使用地",
    "status": "市縣政府查處情形",
}


class LandUseViolation:
    id: str
    year: str
    month: str
    number: str
    city: str
    sectname: str
    sectcode: str
    usage_zone: str
    use: str
    status: list[str]

    def __init__(
        self,
        id: str,
        year: str,
        month: str,
        number: str,
        city: str,
        sectname: str,
        sectcode: str,
        usage_zone: str,
        use: str,
        status: list[str],
    ):
        self.id = id
        self.year = year
        self.month = month
        self.number = number
        self.city = city
        self.sectname = sectname
        self.sectcode = sectcode
        self.usage_zone = usage_zone
        self.use = use
        self.status = status

    def diff(self, other: "LandUseViolation") -> "LandUseViolation":
        if self.id != other.id:
            raise ValueError(
                f"Cannot diff two different LandUseViolation {self.id} and {other.id}"
            )

        id = self.id
        new_number = self.number if self.number != other.number else ""
        new_year = self.year if self.year != other.year else ""
        new_month = self.month if self.month != other.month else ""
        new_city = self.city if self.city != other.city else ""
        new_sectname = self.sectname if self.sectname != other.sectname else ""
        new_sectcode = self.sectcode if self.sectcode != other.sectcode else ""
        new_usage_zone = self.usage_zone if self.usage_zone != other.usage_zone else ""
        new_use = self.use if self.use != other.use else ""
        new_status = list(set(self.status) - set(other.status))

        return LandUseViolation(
            id,
            new_year,
            new_month,
            new_number,
            new_city,
            new_sectname,
            new_sectcode,
            new_usage_zone,
            new_use,
            new_status,
        )

    def to_dict(self) -> dict[str, str | list[str]]:
        return {
            "id": self.id,
            "year": self.year,
            "month": self.month,
            "number": self.number,
            "city": self.city,
            "sectname": self.sectname,
            "sectcode": self.sectcode,
            "usage_zone": self.usage_zone,
            "use": self.use,
            "status": self.status,
        }


# If the year is 11201, the id format will be 112010001, 112010002, 112010003, ...
class IDGenerator:
    year: str
    index: int

    def __init__(self, year: str):
        self.year = year
        self.index = 1

    def generate_id(self) -> str:
        id = f"{self.year}{self.index:04d}"
        self.index += 1
        return id


def open_xlsx(file_path: str, sheet_name_list: list) -> dict[str, pd.DataFrame]:
    xlsx = pd.read_excel(file_path, sheet_name=sheet_name_list)
    return xlsx


def save_xlsx(xlsx: pd.DataFrame, file_path: str, sheet_name_list: list):
    with pd.ExcelWriter(file_path) as writer:
        for name in sheet_name_list:
            xlsx[name].to_excel(writer, sheet_name=name)


def row_to_model(row: pd.Series) -> LandUseViolation:
    id = str(row[ROW_NAME["id"]])
    number = str(row[ROW_NAME["number"]])
    city = str(row[ROW_NAME["city"]])
    sectname = str(row[ROW_NAME["sectname"]])
    usage_zone = str(row[ROW_NAME["usage_zone"]])
    use = str(row[ROW_NAME["use"]])
    status_str = str(row[ROW_NAME["status"]])
    status = status_str.split() if status_str != "" else []

    return LandUseViolation(
        id, "", "", number, city, sectname, "", usage_zone, use, status
    )


def parse_sheet(df: pd.DataFrame) -> list[LandUseViolation]:
    result: list[LandUseViolation] = []
    for _, row in df.iterrows():
        violation = row_to_model(row)
        result.append(violation)

    return result


class Parser:
    violation_dict: dict[str, LandUseViolation]
    update_list: list[LandUseViolation]
    converter: SectCodeConverter

    def __init__(self):
        self.violation_dict = {}
        self.update_list = []
        self.converter = SectCodeConverter()

    def parse_all_sheets(self, xlsx: dict[str, pd.DataFrame]):
        for sheet_name in sheet_name_list:
            df = xlsx[sheet_name]
            violation_list = parse_sheet(df)
            id_generator = IDGenerator(sheet_name)
            year = sheet_name[:3]
            month = sheet_name[3:]

            for violation in violation_list:
                violation.year = year
                violation.month = month

                if violation.sectname in self.violation_dict:
                    violation.id = self.violation_dict[violation.sectname].id
                    diff = self.violation_dict[violation.sectname].diff(violation)
                    self.update_list.append(diff)
                else:
                    violation.id = id_generator.generate_id()
                    print(self.converter.convert(violation.sectname))
                    self.violation_dict[violation.sectname] = violation
                    self.update_list.append(violation)

    def save(self, file_path: str):
        # Save violation_dict to json
        violation_json_list = [
            violation.to_dict() for _, violation in self.violation_dict.items()
        ]
        update_json_list = [violation.to_dict() for violation in self.update_list]

        with open(file_path, "w") as f:
            json.dump(
                {
                    "violations": violation_json_list,
                    "updates": update_json_list,
                },
                f,
                ensure_ascii=False,
                indent=4,
            )


if __name__ == "__main__":
    parser = Parser()
    xlsx = open_xlsx("112.xlsx", sheet_name_list)
    parser.parse_all_sheets(xlsx)
    parser.save("112.json")

# if __name__ == "__main__":
# converter = SectCodeConverter()
# address = "竹北市三崁店段三崁店小段120-6地號"
# address = "烏日區北里段277地號"
# converter.convert(address)

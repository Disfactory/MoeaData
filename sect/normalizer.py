import re

# the strs matched but not in here will be removed
TO_REPLACE_MAP = {
    "之": "-",
    "–": "-",
    "—": "-",
    "台": "臺",
    "１": "1",
    "２": "2",
    "３": "3",
    "４": "4",
    "５": "5",
    "６": "6",
    "７": "7",
    "８": "8",
    "９": "9",
    "０": "0",
    "一": "1",
    "二": "2",
    "三": "3",
    "四": "4",
    "五": "5",
    "六": "6",
    "七": "7",
    "八": "8",
    "九": "9",
}

CHINESE_NUMERALS_SET = set("一二三四五六七八九")


class Normalizer:
    global_replace_re: re.Pattern
    no_hyphen_replace_re: re.Pattern
    no_num_replace_re: re.Pattern

    def __init__(self):
        self.global_replace_re = re.compile(
            """
                [ 　台]
                |
                [０-９]    
            """,
            re.X,
        )

        self.no_hyphen_replace_re = re.compile(
            """
            [之–—]
        """,
            re.X,
        )

        self.no_num_replace_re = re.compile(
            """
            (?:
                [一二三四五六七八九]?
                [一二三四五六七八九]?
                十?
                [一二三四五六七八九]
            )
            (?=-|號|地號|、|$)
        """,
            re.X,
        )

    def execute(self, address: str) -> str:

        if isinstance(address, bytes):
            address = address.decode("utf-8")

        def replace(m):

            found = m.group()

            if found in TO_REPLACE_MAP:
                return TO_REPLACE_MAP[found]

            return ""

        def replace_num(m):

            found = m.group()

            if found in TO_REPLACE_MAP:
                return TO_REPLACE_MAP[found]

            if found[0] in CHINESE_NUMERALS_SET:
                len_found = len(found)
                if len_found == 2:
                    return "1" + TO_REPLACE_MAP[found[1]]
                if len_found == 3:
                    return TO_REPLACE_MAP[found[0]] + TO_REPLACE_MAP[found[2]]

            return ""

        address = self.global_replace_re.sub(replace, address)
        address = self.no_hyphen_replace_re.sub(replace, address)

        while True:
            replaced = self.no_num_replace_re.sub(replace_num, address)
            if address == replaced:
                break
            address = replaced

        return address


if __name__ == "__main__":
    address = "雲林縣口湖鄉梧北段二五四之四十三、二五四之四十六地號"

    normalizer = Normalizer()
    tokens = normalizer.no_num_replace_re.findall(address)
    print(normalizer.execute(address))

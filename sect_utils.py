import re
from collections import namedtuple


class Address(object):
    TOKEN_RE = re.compile(
        """
        (?:
            (?P<value>松山|大安|中正|萬華|大同|中山|文山|南港|內湖|士林|北投|信義|中|東|南|西|北|西屯|南屯|北屯|豐原|東勢|大甲|清水|沙鹿|梧棲|后里|神岡|潭子|大雅|新社|石岡|外埔|大安|烏日|大肚|龍井|霧峰|太平|大里|和平|中正|七堵|暖暖|仁愛|中山|安樂|信義|東|南|北|安南|安平|中西|新營|鹽水|柳營|白河|後壁|東山|麻豆|下營|六甲|官田|大內|佳里|西港|七股|將軍|北門|學甲|新
化|善化|新市|安定|山上|左鎮|仁德|歸仁|關廟|龍崎|玉井|楠西|南化|永康|鹽埕|鼓山|左營|楠梓|三民|新興|前金|苓雅|前鎮|旗津|小港|鳳山|林園|大寮|大樹|大社|仁武|鳥松|岡山|橋頭|燕巢|田寮|阿蓮|路竹|湖內|茄萣|永安|彌陀|梓官|旗山|美濃|六龜|甲仙|杉林|內門|茂林|桃源|那瑪夏|新莊|林口|五股|蘆洲|三重|泰山|新店|石碇|深坑|坪林|烏來|板橋|三峽|鶯歌|樹林|中和|土城|瑞芳|平溪|雙溪|貢
寮|金山|萬里|淡水|汐止|三芝|石門|八里|永和|宜蘭|頭城|礁溪|壯圍|員山|羅東|五結|冬山|蘇澳|三星|大同|南澳|桃園|大溪|中壢|楊梅|蘆竹|大園|龜山|八德|龍潭|平鎮|新屋|觀音|復興|嘉義|竹東|關西|新埔|竹北|湖口|橫山|新豐|芎林|寶山|北埔|峨眉|尖石|五峰|苗栗|苑裡|通霄|公館|銅鑼|三義|西湖|頭屋|竹南|頭份|造橋|後龍|三灣|南庄|大湖|卓蘭|獅潭|泰安|南投|埔里|草屯|竹山|集集|名間|鹿谷|中寮|魚池|國姓|水里|信義|仁愛|彰化|鹿港|和美|北斗|員林|溪湖|田中|二林|線西|伸港|福興|秀水|花壇|芬園|大村|埔鹽|埔心|永靖|社頭|二水|田尾|埤頭|芳苑|大城|竹塘|溪州|新竹|斗六|斗南|虎尾|西螺|土庫|北港|古坑|大埤|莿桐|林內|二崙|崙背|麥寮|東勢|褒忠|臺西|元長|四湖|口湖|水林|朴子|布袋|大林|民雄|溪口|新港|六腳|東石|義竹|鹿草|太保|水上|中埔|竹崎|梅山|番路|大埔|阿里山|屏東|
潮州|東港|恆春|萬丹|長治|麟洛|九如|里港|鹽埔|高樹|萬巒|內埔|竹田|新埤|枋寮|新園|崁頂|林邊|南州|佳冬|琉球|車城|滿州|枋山|三地門|霧臺|瑪家|泰武|來義|春日|獅子|牡丹|花蓮|光復|玉里|新城|吉安|壽豐|鳳林|豐濱|瑞穗|富里|秀林|萬榮|卓溪|臺東|成功|關山|卑南|大武|太麻里|東河|長濱|鹿野|池上|綠島|延平|海端|達仁|金峰|蘭嶼|金湖|金沙|金城|金寧|烈嶼|烏坵|馬公|湖西|白沙|西嶼|望安
|七美|南竿|北竿|莒光|東引|.+?)
        )
        (?:
            (?P<unit>地號|地段|小段|區段|鎮段|鎮區|市區|縣|市|鄉|鎮|市|村|里|區|段|號)
        )
    """,
        re.X,
    )

    VALUE = 0
    UNIT = 1

    GLOBAL_REPLACE_RE = re.compile(
        """
        [ 　台]
        |
        [０-９]    
    """,
        re.X,
    )

    NO_HYPHEN_REPLACE_RE = re.compile(
        """
        [之–—]
    """,
        re.X,
    )

    NO_NUM_REPLACE_RE = re.compile(
        """
        (?:
            [一二三四五六七八九]?
            [一二三四五六七八九]?
            十?
            [一二三四五六七八九]
        )
        (?=-|號|地號|$)
    """,
        re.X,
    )

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

    @staticmethod
    def normalize(s):

        if isinstance(s, bytes):
            s = s.decode("utf-8")

        def replace(m):

            found = m.group()

            if found in Address.TO_REPLACE_MAP:
                return Address.TO_REPLACE_MAP[found]

            return ""

        def replace_num(m):

            found = m.group()

            if found in Address.TO_REPLACE_MAP:
                return Address.TO_REPLACE_MAP[found]

            if found[0] in Address.CHINESE_NUMERALS_SET:
                # for '十一' to '九十九'
                len_found = len(found)
                if len_found == 2:
                    return "1" + Address.TO_REPLACE_MAP[found[1]]
                if len_found == 3:
                    return (
                        Address.TO_REPLACE_MAP[found[0]]
                        + Address.TO_REPLACE_MAP[found[2]]
                    )

            return ""

        s = Address.GLOBAL_REPLACE_RE.sub(replace, s)

        s = Address.NO_HYPHEN_REPLACE_RE.sub(replace, s)

        while True:
            replaced = Address.NO_NUM_REPLACE_RE.sub(replace_num, s)
            if s == replaced:
                break
            s = replaced

        return s

    @staticmethod
    def tokenize(addr_str, normalize=True):
        if normalize:
            addr_str = Address.normalize(addr_str)
        return Address.TOKEN_RE.findall(addr_str)

    def __init__(self, addr_str, normalize=True):
        self.tokens = Address.tokenize(addr_str, normalize)

    def __len__(self):
        return len(self.tokens)

    @staticmethod
    def flat(tokens, sarg=None, *sargs):
        return "".join("".join(token) for token in tokens[slice(sarg, *sargs)])

    def pick_to_flat(self, *idxs):
        return "".join("".join(self.tokens[idx]) for idx in idxs)

    def __repr__(self):
        return f"Address({Address.flat(self.tokens)})"


LandType = namedtuple("LandType", ["name", "units", "digit"])
_types = (
    ("county", ["縣", "市"]),
    ("town", ["鄉", "鎮", "區", "市區", "鎮區"]),
    ("village", ["村", "里"]),
    ("section", ["段", "地段", "區段", "鎮段"]),
    ("small_section", ["小段"]),
    ("number", ["號", "地號"]),
)
_land_types = [LandType(item[0], item[1], i) for i, item in enumerate(_types)]


class LandAddress(Address):

    TOKEN_RE = re.compile(
        """
        (?:
            (?P<value>..+?)
        )
        (?:
            (?P<unit>[縣市鄉鎮市區村里])
        )
    """,
        re.X,
    )

    S_TOKEN_RE = re.compile(
        """
        (?:
            (?P<value>.+?)
        )
        (?:
            (?P<unit>地段|段|小段|地號|號)
        )
    """,
        re.X,
    )

    SEP_SIGN = ","

    def __init__(self, addr_str, normalize=False):
        super(LandAddress, self).__init__(addr_str, normalize)
        for land_type in _land_types:
            setattr(self, land_type.name, self.get_match(self.tokens, land_type.units))

    def __repr__(self):
        return f"LandAddress({self.flat(self.tokens)})"

    def pick_to_flat(self, *digits):
        return "".join("".join(getattr(self, _land_types[d].name)) for d in digits)

    @staticmethod
    def get_digit(unit) -> int:
        for land_type in _land_types:
            if unit in land_type.units:
                return land_type.digit
        return 0

    @staticmethod
    def singularize_address(tokens):

        def flag(ts):
            flags = []
            for i, t in enumerate(ts):
                try:
                    cut_here = (
                        LandAddress.get_digit(t[1])
                        - LandAddress.get_digit(ts[i + 1][1])
                        > 0
                    )
                    flags.append(cut_here)
                except IndexError:
                    flags.append(True)

            return [ts[i] + (f,) for i, f in enumerate(flags)]

        def pre_flat(ts):
            results = []
            fr = 0
            for i, t in enumerate(ts):
                to = i + 1
                if t[2]:
                    results.append((fr, to))
                    fr = to
            return results

        flagged_tokens = flag(tokens)
        to_flat = pre_flat(flagged_tokens)

        return [Address.flat(tokens, fr, to) for fr, to in to_flat]

    @staticmethod
    def get_match(tokens, units):

        def get_first_match(lst):
            return next(iter(lst or []), ("", ""))

        def get_all_matches(ts, us):
            return [
                (t[Address.VALUE], t[Address.UNIT]) for t in ts if t[Address.UNIT] in us
            ]

        all_matches = get_all_matches(tokens, units)

        return get_first_match(all_matches)


# # address = "朴子市母寮段竹村小段581地號"
# address = "大里區大里段1064地號"
# tokens = Address.tokenize(address, normalize=False)
#
# print(tokens)
#
# land_address = LandAddress.singularize_address(tokens)
# print(land_address)

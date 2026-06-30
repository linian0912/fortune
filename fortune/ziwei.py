# -*- coding: utf-8 -*-
"""紫微斗数排盘模块。"""

from datetime import date
from .core import (
    TIAN_GAN, DI_ZHI, JIA_ZI, NA_YIN,
    TIAN_GAN_WX, TIAN_GAN_YY,
    get_gan_index, get_zhi_index,
)
from .lunar import solar_to_lunar, compute_day_gan_zhi

# 十二宫名称（按命宫起顺排）
GONG_NAMES = [
    "命宫", "兄弟", "夫妻", "子女", "财帛", "疾厄",
    "迁移", "交友", "官禄", "田宅", "福德", "父母",
]

# 十二宫地支顺序（从寅开始顺时针）
GONG_ZHI_ORDER = ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"]

# 五行局对应
WX_JU_MAP = {"金": 4, "木": 3, "水": 2, "火": 6, "土": 5}

# 紫微星位置表：key=(五行局数, 农历日)，value=紫微星所在宫位(寅=0)
# 水二局
ZIWEI_TABLE = {
    2: {
        1:0, 2:11, 3:0, 4:1, 5:2, 6:3, 7:4, 8:5, 9:6, 10:7,
        11:8, 12:9, 13:10, 14:11, 15:0, 16:1, 17:2, 18:3, 19:4, 20:5,
        21:6, 22:7, 23:8, 24:9, 25:10, 26:11, 27:0, 28:1, 29:2, 30:3,
    },
    3: {
        1:0, 2:10, 3:0, 4:2, 5:4, 6:6, 7:8, 8:10, 9:0, 10:2,
        11:4, 12:6, 13:8, 14:10, 15:0, 16:2, 17:4, 18:6, 19:8, 20:10,
        21:0, 22:2, 23:4, 24:6, 25:8, 26:10, 27:0, 28:2, 29:4, 30:6,
    },
    4: {
        1:0, 2:9, 3:0, 4:3, 5:6, 6:9, 7:0, 8:3, 9:6, 10:9,
        11:0, 12:3, 13:6, 14:9, 15:0, 16:3, 17:6, 18:9, 19:0, 20:3,
        21:6, 22:9, 23:0, 24:3, 25:6, 26:9, 27:0, 28:3, 29:6, 30:9,
    },
    5: {
        1:0, 2:8, 3:0, 4:4, 5:8, 6:0, 7:4, 8:8, 9:0, 10:4,
        11:8, 12:0, 13:4, 14:8, 15:0, 16:4, 17:8, 18:0, 19:4, 20:8,
        21:0, 22:4, 23:8, 24:0, 25:4, 26:8, 27:0, 28:4, 29:8, 30:0,
    },
    6: {
        1:0, 2:7, 3:0, 4:5, 5:10, 6:3, 7:0, 8:5, 9:10, 10:3,
        11:0, 12:5, 13:10, 14:3, 15:0, 16:5, 17:10, 18:3, 19:0, 20:5,
        21:10, 22:3, 23:0, 24:5, 25:10, 26:3, 27:0, 28:5, 29:10, 30:3,
    },
}

# 天府星位置：紫微在寅(0)→天府在辰(2)，紫微在卯(1)→天府在卯(1)，...
# 天府位置 = (0 + (12 - 紫微位置) + 4) % 12 = (16 - 紫微位置) % 12
# Actually the formula: 天府 = (紫微 + 4) with 对宫关系
# 紫微在寅(0)→天府在辰(2), 紫微在卯(1)→天府在巳(3), 紫微在辰(2)→天府在午(4)
# Wait, let me use the standard formula:
# 天府位置 = (4 - 紫微位置) % 12 + 紫微位置? No...
# Standard: 紫微在寅，天府在辰; 紫微在卯，天府在卯; 紫微在辰，天府在寅
# This is: 天府 = (12 - 紫微 + 4) % 12? 
# Let me just precompute the table
TIANFU_TABLE = {
    0: 2, 1: 1, 2: 0, 3: 11, 4: 10, 5: 9,
    6: 8, 7: 7, 8: 6, 9: 5, 10: 4, 11: 3,
}


def compute_ming_gong(month, hour_zhi):
    """安命宫。返回命宫地支索引(寅=0)。"""
    hour_idx = DI_ZHI.index(hour_zhi)
    # 从寅宫起正月，顺数到生月；再从该宫起子时，逆数到生时
    ming_idx = (2 + (month - 1) - hour_idx) % 12
    return ming_idx


def compute_shen_gong(month, hour_zhi):
    """安身宫。返回身宫地支索引(寅=0)。"""
    hour_idx = DI_ZHI.index(hour_zhi)
    # 从寅宫起正月，顺数到生月；再从该宫起子时，顺数到生时
    shen_idx = (2 + (month - 1) + hour_idx) % 12
    return shen_idx


def compute_wx_ju(ming_gan_zhi):
    """定五行局。根据命宫干支纳音定局数。"""
    idx = JIA_ZI.index(ming_gan_zhi)
    na_yin_wx_str = NA_YIN[idx % 30]
    # 纳音五行映射
    for wx in ["金", "木", "水", "火", "土"]:
        if wx in na_yin_wx_str:
            return WX_JU_MAP[wx], na_yin_wx_str
    return 5, "未知"


def compute_ziwei_pos(wx_ju, lunar_day):
    """安紫微星。返回紫微星所在宫位(寅=0)。"""
    return ZIWEI_TABLE.get(wx_ju, {}).get(lunar_day, 0)


def compute_tianfu_pos(ziwei_pos):
    """安天府星。返回天府星所在宫位(寅=0)。"""
    return TIANFU_TABLE.get(ziwei_pos, 2)


def place_ziwei_stars(ziwei_pos):
    """安紫微系星曜：紫微、天机、(太阳)、武曲、天同、(廉贞)"""
    # 紫微系从紫微逆行安：紫微,天机,空,太阳,武曲,天同,空,空,空,空,廉贞
    stars = {}
    stars["紫微"] = ziwei_pos
    stars["天机"] = (ziwei_pos - 1) % 12
    # 跳过一位
    stars["太阳"] = (ziwei_pos - 3) % 12
    stars["武曲"] = (ziwei_pos - 4) % 12
    stars["天同"] = (ziwei_pos - 5) % 12
    stars["廉贞"] = (ziwei_pos - 9) % 12  # Actually 廉贞 is at -8 or -9
    # Let me fix: 紫微系：紫微(-0),天机(-1),空,太阳(-3),武曲(-4),天同(-5),空,廉贞(-8)
    stars["廉贞"] = (ziwei_pos - 8) % 12
    return stars


def place_tianfu_stars(tianfu_pos):
    """安天府系星曜：天府、太阴、贪狼、巨门、天相、天梁、七杀、破军"""
    # 天府系从天府顺行：天府,太阴,贪狼,巨门,天相,天梁,七杀,空,空,破军
    stars = {}
    stars["天府"] = tianfu_pos
    stars["太阴"] = (tianfu_pos + 1) % 12
    stars["贪狼"] = (tianfu_pos + 2) % 12
    stars["巨门"] = (tianfu_pos + 3) % 12
    stars["天相"] = (tianfu_pos + 4) % 12
    stars["天梁"] = (tianfu_pos + 5) % 12
    stars["七杀"] = (tianfu_pos + 6) % 12
    stars["破军"] = (tianfu_pos + 10) % 12
    return stars


def place_aux_stars(year_gan, year_zhi, month, hour_zhi, lunar_day):
    """安辅星。"""
    stars = {}
    zhi_idx = DI_ZHI.index(year_zhi)
    gan_idx = get_gan_index(year_gan)
    hour_idx = DI_ZHI.index(hour_zhi)

    # 文昌：从戌宫起，逆数到生时
    stars["文昌"] = (10 - hour_idx) % 12  # 戌=10

    # 文曲：从辰宫起，顺数到生时
    stars["文曲"] = (2 + hour_idx) % 12  # 辰=2

    # 左辅：辰上起正月，顺数到生月
    stars["左辅"] = (2 + month - 1) % 12  # 辰=2

    # 右弼：戌上起正月，逆数到生月
    stars["右弼"] = (10 - (month - 1)) % 12  # 戌=10

    # 天魁/天钺：按年干
    kui_map = {0: 1, 1: 0, 2: 10, 3: 10, 4: 1, 5: 0, 6: 7, 7: 7, 8: 4, 9: 4}
    yue_map = {0: 7, 1: 6, 2: 4, 3: 4, 4: 7, 5: 6, 6: 1, 7: 1, 8: 10, 9: 10}
    stars["天魁"] = kui_map.get(gan_idx, 1)
    stars["天钺"] = yue_map.get(gan_idx, 7)

    # 禄存：按年干
    lucun_map = {0: 0, 1: 3, 2: 5, 3: 6, 4: 5, 5: 6, 6: 8, 7: 9, 8: 10, 9: 0}
    stars["禄存"] = lucun_map.get(gan_idx, 0)

    # 擎羊：禄存前一宫
    stars["擎羊"] = (stars["禄存"] + 1) % 12

    # 陀罗：禄存后一宫
    stars["陀罗"] = (stars["禄存"] - 1) % 12

    # 火星/铃星：按年支和时辰
    huo_start = {"寅午戌": 1, "申子辰": 0, "巳酉丑": 3, "亥卯未": 9}
    ling_start = {"寅午戌": 3, "申子辰": 9, "巳酉丑": 1, "亥卯未": 0}
    for key in huo_start:
        if year_zhi in key:
            stars["火星"] = (huo_start[key] + hour_idx) % 12
            stars["铃星"] = (ling_start[key] + hour_idx) % 12
            break

    # 天马：按年支
    tianma_map = {"寅午戌": 8, "申子辰": 0, "巳酉丑": 10, "亥卯未": 5}
    for key in tianma_map:
        if year_zhi in key:
            stars["天马"] = tianma_map[key]
            break

    return stars


def compute_si_hua(year_gan):
    """安四化：化禄、化权、化科、化忌。"""
    gan_idx = get_gan_index(year_gan)
    # 四化表：按年干
    # 甲廉破武阳, 乙机梁紫阴, 丙同机昌廉, 丁阴同机巨,
    # 戊贪阴右机, 己武贪梁曲, 庚阳武阴同, 辛巨阳曲昌,
    # 壬梁紫左武, 癸破巨阴贪
    sihua_table = {
        0: ("廉贞", "破军", "武曲", "太阳"),   # 甲
        1: ("天机", "天梁", "紫微", "太阴"),   # 乙
        2: ("天同", "天机", "文昌", "廉贞"),   # 丙
        3: ("太阴", "天同", "天机", "巨门"),   # 丁
        4: ("贪狼", "太阴", "右弼", "天机"),   # 戊
        5: ("武曲", "贪狼", "天梁", "文曲"),   # 己
        6: ("太阳", "武曲", "太阴", "天同"),   # 庚
        7: ("巨门", "太阳", "文曲", "文昌"),   # 辛
        8: ("天梁", "紫微", "左辅", "武曲"),   # 壬
        9: ("破军", "巨门", "太阴", "贪狼"),   # 癸
    }
    lu, quan, ke, ji = sihua_table.get(gan_idx, ("", "", "", ""))
    return {"化禄": lu, "化权": quan, "化科": ke, "化忌": ji}


class Ziwei:
    """紫微斗数命盘。"""

    def __init__(self, year, month, day, hour, gender='male', lunar=False):
        self.gender = gender
        if lunar:
            from .lunar import lunar_to_solar
            result = lunar_to_solar(year, month, day)
            if result:
                year, month, day = result
        self.birth = date(year, month, day)
        self.birth_hour = hour

        self.lunar_date = solar_to_lunar(year, month, day)
        lunar_y, lunar_m, lunar_d, lunar_leap = self.lunar_date

                # 年柱以立春为界
        from .bazi import compute_year_gan_zhi
        self.year_gan_zhi = compute_year_gan_zhi(year, month, day)
        self.year_gan = self.year_gan_zhi[0]
        self.year_zhi = self.year_gan_zhi[1]

        from .lunar import get_shi_chen_from_hour
        self.hour_zhi = get_shi_chen_from_hour(hour)

        # 命宫 & 身宫
        self.ming_gong_idx = compute_ming_gong(lunar_m, self.hour_zhi)
        self.shen_gong_idx = compute_shen_gong(lunar_m, self.hour_zhi)

        # 命宫干支
        ming_zhi = GONG_ZHI_ORDER[self.ming_gong_idx]
        # 命宫天干：用五虎遁，从寅宫起
        gan_idx = get_gan_index(self.year_gan)
        start_map = {0: 2, 1: 4, 2: 6, 3: 8, 4: 0}
        ming_gan_idx = (start_map[gan_idx % 5] + self.ming_gong_idx) % 10
        self.ming_gan_zhi = TIAN_GAN[ming_gan_idx] + ming_zhi

        # 五行局
        self.wx_ju, self.wx_ju_name = compute_wx_ju(self.ming_gan_zhi)

        # 紫微 & 天府
        self.ziwei_pos = compute_ziwei_pos(self.wx_ju, lunar_d)
        self.tianfu_pos = compute_tianfu_pos(self.ziwei_pos)

        # 星曜
        self.stars = {}
        self.stars.update(place_ziwei_stars(self.ziwei_pos))
        self.stars.update(place_tianfu_stars(self.tianfu_pos))
        self.stars.update(place_aux_stars(
            self.year_gan, self.year_zhi, lunar_m, self.hour_zhi, lunar_d
        ))

        # 四化
        self.si_hua = compute_si_hua(self.year_gan)

        # 十二宫
        self.gongs = self._build_gongs(lunar_m)

        # 身宫所在
        self.shen_gong_name = GONG_NAMES[(self.shen_gong_idx - self.ming_gong_idx) % 12]

    def _build_gongs(self, birth_month):
        """构建十二宫数据。每个宫包含：宫名、宫位地支、星曜列表。"""
        gong_list = []
        for i in range(12):
            gong_idx = (self.ming_gong_idx + i) % 12
            zhi = GONG_ZHI_ORDER[gong_idx]
            name = GONG_NAMES[i]
            # 干支
            gan_idx = get_gan_index(self.year_gan)
            start_map = {0: 2, 1: 4, 2: 6, 3: 8, 4: 0}
            gong_gan_idx = (start_map[gan_idx % 5] + gong_idx) % 10
            gz = TIAN_GAN[gong_gan_idx] + zhi

            # 该宫的星曜
            star_list = []
            for star_name, pos in self.stars.items():
                if pos == gong_idx:
                    prefix = ""
                    if star_name == self.si_hua.get("化禄"):
                        prefix = "禄"
                    elif star_name == self.si_hua.get("化权"):
                        prefix = "权"
                    elif star_name == self.si_hua.get("化科"):
                        prefix = "科"
                    elif star_name == self.si_hua.get("化忌"):
                        prefix = "忌"
                    star_list.append((star_name, prefix))

            is_shen = (gong_idx == self.shen_gong_idx)
            is_ming = (i == 0)
            gong_list.append({
                "name": name,
                "zhi": zhi,
                "gz": gz,
                "stars": star_list,
                "is_ming": is_ming,
                "is_shen": is_shen,
            })
        return gong_list

    def display(self):
        lunar_y, lunar_m, lunar_d, lunar_leap = self.lunar_date
        leap_str = "(闰)" if lunar_leap else ""

        lines = []
        lines.append("=" * 60)
        lines.append("                        紫微斗数命盘")
        lines.append("=" * 60)
        lines.append(f"公历: {self.birth.year}年{self.birth.month}月{self.birth.day}日 {self.birth_hour}时")
        lines.append(f"农历: {lunar_y}年{leap_str}{lunar_m}月{lunar_d}日  {self.hour_zhi}时")
        lines.append(f"性别: {'男' if self.gender == 'male' else '女'}")
        lines.append(f"命宫: {self.ming_gan_zhi}  五行局: {self.wx_ju_name}({self.wx_ju}局)")
        lines.append(f"身宫: {self.shen_gong_name}")
        lines.append("")

        # 四化
        sihua_str = "  ".join([f"{k}:{v}" for k, v in self.si_hua.items() if v])
        lines.append(f"【四化】 {sihua_str}")
        lines.append("")

        # 十二宫表格 - 4行 x 3列 布局
        # 实际布局：
        # 巳(5)  午(6)  未(7)  申(8)
        # 辰(4)                  酉(9)
        # 卯(3)                  戌(10)
        # 寅(2)  丑(1)  子(0)  亥(11)
        # But our ordering: 命宫, 兄弟, ..., 父母 clockwise from 寅
        # Mapped to: 寅=命宫, 卯=兄弟, ...丑=父母

        # 按地支排列的宫
        gong_by_zhi = {}
        for g in self.gongs:
            gong_by_zhi[g["zhi"]] = g

        lines.append("【十二宫命盘】")
        lines.append("")
        # Top row: 巳 午 未 申
        top = ["巳", "午", "未", "申"]
        mid_left = "辰"
        mid_right = "酉"
        bot = ["丑", "子", "亥", "戌"]
        right_side = ["卯", "寅"]

        for zhi_list in [top, bot]:
            row = []
            for zhi in zhi_list:
                g = gong_by_zhi.get(zhi)
                if g:
                    row.append(self._gong_box(g))
            lines.append("  ".join(row))

        # Middle row with gap
        left_g = gong_by_zhi.get("辰")
        right_g = gong_by_zhi.get("酉")
        left_box = self._gong_box(left_g).split("\n") if left_g else [""] * 6
        right_box = self._gong_box(right_g).split("\n") if right_g else [""] * 6
        for i in range(len(left_box)):
            lines.append(f"{left_box[i]}                    {right_box[i]}")

        # Bottom
        for zhi in right_side:
            g = gong_by_zhi.get(zhi)
            if g:
                left = self._gong_box(gong_by_zhi.get("卯") if zhi == "卯" else gong_by_zhi.get("寅"))
                if zhi == "卯":
                    g2 = gong_by_zhi.get("寅")
                    lines.append(f"{self._gong_box(g)}  {self._gong_box(g2)}")

        lines.append("")
        lines.append("=" * 60)
        return "\n".join(lines)

    def _gong_box(self, gong):
        name = gong["name"]
        zhi = gong["zhi"]
        gz = gong["gz"]
        tag = ""
        if gong["is_ming"]:
            tag = "【命】"
        if gong["is_shen"]:
            tag += "【身】"

        # Select main stars (紫微系+天府系)
        main_names = {"紫微", "天机", "太阳", "武曲", "天同", "廉贞",
                       "天府", "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军"}
        main_stars = [(n, p) for n, p in gong["stars"] if n in main_names]
        aux_stars = [(n, p) for n, p in gong["stars"] if n not in main_names]

        lines = [
            f"┌{'─'*12}┐",
            f"│{name}({zhi}){gz:^4}│",
        ]
        for s_name, prefix in main_stars[:3]:
            disp = f"{prefix}{s_name}" if prefix else s_name
            lines.append(f"│{disp:　^8}│")
        for _ in range(3 - len(main_stars[:3])):
            lines.append(f"│{'':　^8}│")
        for s_name, prefix in aux_stars[:2]:
            disp = f"{prefix}{s_name}" if prefix else s_name
            lines.append(f"│{disp:　^8}│")
        for _ in range(2 - len(aux_stars[:2])):
            lines.append(f"│{'':　^8}│")
        if tag:
            lines.append(f"│{tag:^10}│")
        else:
            lines.append(f"│{'':　^8}│")
        lines.append(f"└{'─'*12}┘")
        return "\n".join(lines)

    def display_simple(self):
        """简化版输出：按地支顺序列出所有宫位和星曜。"""
        lunar_y, lunar_m, lunar_d, lunar_leap = self.lunar_date
        lines = []
        lines.append("=" * 60)
        lines.append("                    紫微斗数命盘（简化版）")
        lines.append("=" * 60)
        lines.append(f"农历: {lunar_y}年{lunar_m}月{lunar_d}日 {self.hour_zhi}时")
        lines.append(f"命宫: {self.ming_gan_zhi}  五行局: {self.wx_ju_name}({self.wx_ju}局)")
        lines.append("")

        gong_by_zhi = {}
        for g in self.gongs:
            gong_by_zhi[g["zhi"]] = g

        order = ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"]
        for zhi in order:
            g = gong_by_zhi.get(zhi)
            if not g:
                continue
            tag = ""
            if g["is_ming"]:
                tag = " 【命宫】"
            if g["is_shen"]:
                tag += "【身宫】"
            star_strs = []
            for s_name, prefix in g["stars"]:
                disp = f"{prefix}{s_name}" if prefix else s_name
                star_strs.append(disp)
            lines.append(f"  {zhi}宫[{g['name']:^4}]({g['gz']}){tag}")
            lines.append(f"      {', '.join(star_strs) if star_strs else '(无主星)'}")
            lines.append("")
        lines.append("=" * 60)
        return "\n".join(lines)
    def analyze(self):
        from .ziwei_analysis import full_ziwei_analysis, format_ziwei_analysis
        return full_ziwei_analysis(self)

    def display_with_analysis(self):
        from .ziwei_analysis import format_ziwei_analysis, full_ziwei_analysis
        base = self.display_simple()
        analysis = full_ziwei_analysis(self)
        return base + "\n" + format_ziwei_analysis(analysis)


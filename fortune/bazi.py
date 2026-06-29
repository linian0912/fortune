# -*- coding: utf-8 -*-
"""四柱八字排盘模块：年柱、月柱、日柱、时柱、十神、大运、流年。"""

from datetime import date
from .core import (
    TIAN_GAN, DI_ZHI, JIA_ZI, NA_YIN,
    TIAN_GAN_WX, TIAN_GAN_YY,
    DI_ZHI_WX, DI_ZHI_CANG_GAN,
    get_gan_index, get_zhi_index, YUE_ZHI, SHENG_XIAO,
)
from .lunar import (
    solar_to_lunar, get_jie_qi_date,
    compute_day_gan_zhi, compute_hour_gan_zhi,
)


def compute_year_gan_zhi(year, month, day):
    """计算年柱（以立春为界）。"""
    # 立春在2月4日左右，之前属于上一年
    lc_m, lc_d = get_jie_qi_date(year, 2)
    if month < lc_m or (month == lc_m and day < lc_d):
        year -= 1
    idx = (year - 4) % 60
    return JIA_ZI[idx]


def compute_month_zhi(year, month, day):
    jie_list = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 0]
    for j, jie_idx in enumerate(jie_list):
        jm, jd = get_jie_qi_date(year, jie_idx)
        next_j = (j + 1) % 12
        next_jie_idx = jie_list[next_j]
        next_year = year + 1 if next_j == 0 else year
        nm, nd = get_jie_qi_date(next_year, next_jie_idx)
        if (month > jm or (month == jm and day >= jd)) and \
           (month < nm or (month == nm and day < nd)):
            return YUE_ZHI[j]
    return YUE_ZHI[11]


def compute_month_gan(year_gan, month_zhi):
    gan_idx = get_gan_index(year_gan)
    start_map = {0: 2, 1: 4, 2: 6, 3: 8, 4: 0}
    start = start_map[gan_idx % 5]
    zhi_idx = DI_ZHI.index(month_zhi)
    return TIAN_GAN[(start + zhi_idx) % 10]


def compute_shi_shen(day_gan, pillar_gan):
    me_wx = TIAN_GAN_WX[day_gan]
    other_wx = TIAN_GAN_WX[pillar_gan]
    me_yy = TIAN_GAN_YY[day_gan]
    other_yy = TIAN_GAN_YY[pillar_gan]
    relation_map = {
        ("木","水"):"生我",("木","火"):"我生",("木","金"):"克我",("木","土"):"我克",
        ("火","木"):"生我",("火","土"):"我生",("火","水"):"克我",("火","金"):"我克",
        ("土","火"):"生我",("土","金"):"我生",("土","木"):"克我",("土","水"):"我克",
        ("金","土"):"生我",("金","水"):"我生",("金","火"):"克我",("金","木"):"我克",
        ("水","金"):"生我",("水","木"):"我生",("水","土"):"克我",("水","火"):"我克",
    }
    relation = relation_map.get((me_wx, other_wx), "同我")
    same_yy = (me_yy == other_yy)
    ten_god_map = {
        "同我": "比肩" if same_yy else "劫财",
        "我生": "食神" if same_yy else "伤官",
        "我克": "偏财" if same_yy else "正财",
        "克我": "七杀" if same_yy else "正官",
        "生我": "偏印" if same_yy else "正印",
    }
    return ten_god_map[relation]


def compute_da_yun(month_jia_zi_idx, gender, year_gan_yy):
    is_yang = (year_gan_yy == 1)
    is_male = (gender == 'male')
    forward = (is_yang and is_male) or (not is_yang and not is_male)
    da_yun = []
    for i in range(1, 11):
        idx = (month_jia_zi_idx + i) % 60 if forward else (month_jia_zi_idx - i) % 60
        da_yun.append((JIA_ZI[idx], i * 10))
    return da_yun


def get_wu_xing_summary(year_gan, month_gan, day_gan, hour_gan,
                         year_zhi, month_zhi, day_zhi, hour_zhi):
    wx_count = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
    for gan in [year_gan, month_gan, day_gan, hour_gan]:
        wx_count[TIAN_GAN_WX[gan]] += 1
    for zhi in [year_zhi, month_zhi, day_zhi, hour_zhi]:
        wx_count[DI_ZHI_WX[zhi]] += 1
    return wx_count


class Bazi:
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

        self.year_gan_zhi = compute_year_gan_zhi(year, month, day)
        self.year_gan = self.year_gan_zhi[0]
        self.year_zhi = self.year_gan_zhi[1]

        self.month_zhi = compute_month_zhi(year, month, day)
        self.month_gan = compute_month_gan(self.year_gan, self.month_zhi)
        self.month_gan_zhi = self.month_gan + self.month_zhi

        self.day_gan_zhi = compute_day_gan_zhi(year, month, day)
        self.day_gan = self.day_gan_zhi[0]
        self.day_zhi = self.day_gan_zhi[1]

        self.hour_gan_zhi = compute_hour_gan_zhi(self.day_gan, hour)
        self.hour_gan = self.hour_gan_zhi[0]
        self.hour_zhi = self.hour_gan_zhi[1]

        self.shi_shen = {
            "年": compute_shi_shen(self.day_gan, self.year_gan),
            "月": compute_shi_shen(self.day_gan, self.month_gan),
            "日": "日主",
            "时": compute_shi_shen(self.day_gan, self.hour_gan),
        }

        self.wu_xing = get_wu_xing_summary(
            self.year_gan, self.month_gan, self.day_gan, self.hour_gan,
            self.year_zhi, self.month_zhi, self.day_zhi, self.hour_zhi,
        )

        year_idx = JIA_ZI.index(self.year_gan_zhi)
        month_idx = JIA_ZI.index(self.month_gan_zhi)
        day_idx = JIA_ZI.index(self.day_gan_zhi)
        hour_idx = JIA_ZI.index(self.hour_gan_zhi)
        self.na_yin = {
            "年": NA_YIN[year_idx % 30],
            "月": NA_YIN[month_idx % 30],
            "日": NA_YIN[day_idx % 30],
            "时": NA_YIN[hour_idx % 30],
        }

        year_gan_yy = TIAN_GAN_YY[self.year_gan]
        self.da_yun = compute_da_yun(month_idx, gender, year_gan_yy)

        self.day_wx = TIAN_GAN_WX[self.day_gan]
        self.sheng_xiao = SHENG_XIAO[DI_ZHI.index(self.year_zhi)]

    def display(self):
        lunar_y, lunar_m, lunar_d, lunar_leap = self.lunar_date
        leap_str = "(闰)" if lunar_leap else ""
        wx_bars = []
        for wx, count in self.wu_xing.items():
            bar = "█" * count + "░" * (8 - count)
            wx_bars.append(f"  {wx}: {bar} ({count})")

        cang_gan_lines = []
        for label, zhi in [("年", self.year_zhi), ("月", self.month_zhi),
                            ("日", self.day_zhi), ("时", self.hour_zhi)]:
            cang_gan_lines.append(
                f"  {label}支{zhi}藏: {' '.join(DI_ZHI_CANG_GAN[zhi])}"
            )

        dayun_lines = []
        for i, (gz, age) in enumerate(self.da_yun[:8]):
            dayun_lines.append(f"  {gz}({age}岁)")
        dayun_rows = []
        for i in range(0, len(dayun_lines), 4):
            dayun_rows.append("  ".join(dayun_lines[i:i+4]))

        lines = [
            "=" * 50,
            "                    四柱八字命盘",
            "=" * 50,
            f"公历: {self.birth.year}年{self.birth.month}月{self.birth.day}日 {self.birth_hour}时",
            f"农历: {lunar_y}年{leap_str}{lunar_m}月{lunar_d}日",
            f"生肖: {self.sheng_xiao}    性别: {'男' if self.gender == 'male' else '女'}",
            f"日主: {self.day_gan}({self.day_wx})",
            "",
            "  ┌──────┬──────┬──────┬──────┐",
            "  │  年柱  │  月柱  │  日柱  │  时柱  │",
            "  ├──────┼──────┼──────┼──────┤",
            f"  │ {self.year_gan_zhi:^4} │ {self.month_gan_zhi:^4} │ {self.day_gan_zhi:^4} │ {self.hour_gan_zhi:^4} │",
            "  ├──────┼──────┼──────┼──────┤",
            f"  │  {self.shi_shen['年']:^4} │  {self.shi_shen['月']:^4} │  {self.shi_shen['日']:^4} │  {self.shi_shen['时']:^4} │",
            "  ├──────┼──────┼──────┼──────┤",
            f"  │{self.na_yin['年']:^6}│{self.na_yin['月']:^6}│{self.na_yin['日']:^6}│{self.na_yin['时']:^6}│",
            "  └──────┴──────┴──────┴──────┘",
            "",
            "【五行分布】",
        ] + wx_bars + [
            f"  日主{self.day_wx}: {'旺' if self.wu_xing[self.day_wx] >= 3 else '弱'}",
            "",
            "【地支藏干】",
        ] + cang_gan_lines + [
            "",
            "【大运排盘】",
        ] + dayun_rows + [
            "",
            "=" * 50,
        ]
        return "\n".join(lines)

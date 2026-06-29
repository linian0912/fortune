# -*- coding: utf-8 -*-
"""农历转换与节气计算模块。"""

from datetime import date, timedelta
from .core import (
    TIAN_GAN, DI_ZHI, JIA_ZI, JIE_QI, YUE_ZHI,
    get_shi_chen_from_hour, get_gan_index, NA_YIN,
)

# 农历数据 1900-2100（公历日期编码）
LUNAR_INFO = [
    0x04bd8, 0x04ae0, 0x0a570, 0x054d5, 0x0d260, 0x0d950, 0x16554, 0x056a0, 0x09ad0, 0x055d2,
    0x04ae0, 0x0a5b6, 0x0a4d0, 0x0d250, 0x1d255, 0x0b540, 0x0d6a0, 0x0ada2, 0x095b0, 0x14977,
    0x04970, 0x0a4b0, 0x0b4b5, 0x06a50, 0x06d40, 0x1ab54, 0x02b60, 0x09570, 0x052f2, 0x04970,
    0x06566, 0x0d4a0, 0x0ea50, 0x06e95, 0x05ad0, 0x02b60, 0x186e3, 0x092e0, 0x1c8d7, 0x0c950,
    0x0d4a0, 0x1d8a6, 0x0b550, 0x056a0, 0x1a5b4, 0x025d0, 0x092d0, 0x0d2b2, 0x0a950, 0x0b557,
    0x06ca0, 0x0b550, 0x15355, 0x04da0, 0x0a5b0, 0x14573, 0x052b0, 0x0a9a8, 0x0e950, 0x06aa0,
    0x0aea6, 0x0ab50, 0x04b60, 0x0aae4, 0x0a570, 0x05260, 0x0f263, 0x0d950, 0x05b57, 0x056a0,
    0x096d0, 0x04dd5, 0x04ad0, 0x0a4d0, 0x0d4d4, 0x0d250, 0x0d558, 0x0b540, 0x0b6a0, 0x195a6,
    0x095b0, 0x049b0, 0x0a974, 0x0a4b0, 0x0b27a, 0x06a50, 0x06d40, 0x0af46, 0x0ab60, 0x09570,
    0x04af5, 0x04970, 0x064b0, 0x074a3, 0x0ea50, 0x06b58, 0x05ac0, 0x0ab60, 0x096d5, 0x092e0,
    0x0c960, 0x0d954, 0x0d4a0, 0x0da50, 0x07552, 0x056a0, 0x0abb7, 0x025d0, 0x092d0, 0x0cab5,
    0x0a950, 0x0b4a0, 0x0baa4, 0x0ad50, 0x055d9, 0x04ba0, 0x0a5b0, 0x15176, 0x052b0, 0x0a930,
    0x07954, 0x06aa0, 0x0ad50, 0x05b52, 0x04b60, 0x0a6e6, 0x0a4e0, 0x0d260, 0x0ea65, 0x0d530,
    0x05aa0, 0x076a3, 0x096d0, 0x04afb, 0x04ad0, 0x0a4d0, 0x1d0b6, 0x0d250, 0x0d520, 0x0dd45,
    0x0b5a0, 0x056d0, 0x055b2, 0x049b0, 0x0a577, 0x0a4b0, 0x0aa50, 0x1b255, 0x06d20, 0x0ada0,
    0x14b63, 0x09370, 0x049f8, 0x04970, 0x064b0, 0x168a6, 0x0ea50, 0x06aa0, 0x1a6c4, 0x0aae0,
    0x092e0, 0x0d2e3, 0x0c960, 0x0d557, 0x0d4a0, 0x0da50, 0x05d55, 0x056a0, 0x0a6d0, 0x055d4,
    0x052d0, 0x0a9b8, 0x0a950, 0x0b4a0, 0x0b6a6, 0x0ad50, 0x055a0, 0x0aba4, 0x0a5b0, 0x052b0,
    0x0b273, 0x06930, 0x07337, 0x06aa0, 0x0ad50, 0x14b55, 0x04b60, 0x0a570, 0x054e4, 0x0d160,
    0x0e968, 0x0d520, 0x0daa0, 0x16aa6, 0x056d0, 0x04ae0, 0x0a9d4, 0x0a4d0, 0x0d150, 0x0f252,
    0x0d520,
]

def _lunar_year_days(y):
    i, s = 0x8000, 348
    while i > 8:
        s += 1 if LUNAR_INFO[y - 1900] & i else 0
        i >>= 1
    return s + _lunar_leap_days(y)

def _lunar_leap_month(y):
    return LUNAR_INFO[y - 1900] & 0xf

def _lunar_leap_days(y):
    if _lunar_leap_month(y):
        return 30 if LUNAR_INFO[y - 1900] & 0x10000 else 29
    return 0

def _lunar_month_days(y, m):
    return 30 if LUNAR_INFO[y - 1900] & (0x10000 >> m) else 29

def solar_to_lunar(year, month, day):
    """公历转农历。返回 (lunar_year, lunar_month, lunar_day, is_leap)。"""
    base = date(1900, 1, 31)
    solar = date(year, month, day)
    offset = (solar - base).days
    y = 1900
    while y < 2101:
        ydays = _lunar_year_days(y)
        if offset < ydays:
            break
        offset -= ydays
        y += 1
    leap = _lunar_leap_month(y)
    is_leap = False
    m = 1
    while m <= 12:
        mdays = _lunar_month_days(y, m)
        if offset < mdays:
            break
        offset -= mdays
        m += 1
        if m == leap + 1:
            if offset < _lunar_leap_days(y):
                is_leap = True
                break
            offset -= _lunar_leap_days(y)
    return y, m, offset + 1, is_leap

def lunar_to_solar(year, month, day, is_leap=False):
    """农历转公历。返回 (year, month, day)。"""
    offset = 0
    for y in range(1900, year):
        offset += _lunar_year_days(y)
    leap = _lunar_leap_month(year)
    for m in range(1, month):
        offset += _lunar_month_days(year, m)
        if m == leap:
            offset += _lunar_leap_days(year)
    if month == leap and is_leap:
        pass
    elif is_leap and month != leap:
        return None
    offset += day - 1
    base = date(1900, 1, 31)
    solar = base + timedelta(days=offset)
    return solar.year, solar.month, solar.day

def get_jie_qi_date(year, jie_qi_index):
    """返回指定年份节气的公历近似日期 (month, day)。"""
    base_month, base_day = JIE_QI[jie_qi_index]
    shift = (year - 2000) // 72
    d = base_day + shift
    return base_month, max(1, d)

def get_yue_zhi_index(solar_month, solar_day, year):
    """根据公历月和日返回月支索引（寅=0...丑=11）。

    月支以节气划分：立春起为寅月，惊蛰起为卯月，以此类推。
    """
    # 检查每个节气
    for i, (m, d) in enumerate(JIE_QI):
        actual_m, actual_d = get_jie_qi_date(year, i)
        if solar_month < actual_m or (solar_month == actual_m and solar_day < actual_d):
            # 在上一个节气之后
            prev_idx = (i - 2) % 24  # 前一个"节"（非"气"）
            # 节在索引 2,4,6,8,10,12,14,16,18,20,22,0（立春=2）
            jie_list = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 0]
            for j, jie_idx in enumerate(jie_list):
                if i <= jie_idx:
                    return (j - 1) % 12
                if j == 11:
                    return 11
            return 11
    return 11  # 立春之前 = 丑月(11)

def compute_day_gan_zhi(year, month, day):
    """计算公历日期的日干支。

    基于已知参考点：1900-01-01 = 甲戌日（六十甲子序号10）。
    """
    d = date(year, month, day)
    ref = date(1900, 1, 1)
    delta = (d - ref).days
    idx = (10 + delta) % 60
    return JIA_ZI[idx]

def compute_hour_gan_zhi(day_gan, hour):
    """计算时柱干支。

    时支由小时确定，时干由日干决定（五鼠遁法）。
    """
    shi_zhi = get_shi_chen_from_hour(hour)
    zhi_idx = DI_ZHI.index(shi_zhi)
    gan_idx = get_gan_index(day_gan)
    # 甲己日起甲子，乙庚日起丙子，丙辛日起戊子，丁壬日起庚子，戊癸日起壬子
    start_gan = [(gan_idx % 5) * 2][0]  # 甲=0→0, 乙=1→2, 丙=2→4, 丁=3→6, 戊=4→8
    # 简化：甲己→甲子(0), 乙庚→丙子(2), 丙辛→戊子(4), 丁壬→庚子(6), 戊癸→壬子(8)
    start_map = {0: 0, 1: 2, 2: 4, 3: 6, 4: 8}
    start = start_map[gan_idx % 5]
    shi_gan_idx = (start + zhi_idx) % 10
    return TIAN_GAN[shi_gan_idx] + shi_zhi

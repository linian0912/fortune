# -*- coding: utf-8 -*-
"""四柱八字排盘模块：年柱、月柱、日柱、时柱、十神、大运、流年。"""

from datetime import date
from .core import (
    TIAN_GAN, DI_ZHI, JIA_ZI, NA_YIN,
    TIAN_GAN_WX, TIAN_GAN_YY,
    DI_ZHI_WX, DI_ZHI_CANG_GAN,
    get_gan_index, get_zhi_index, YUE_ZHI, SHENG_XIAO,
    get_shi_chen_from_hour,
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
    """五行分布统计（含藏干加权）。
    天干权重 1.0，地支本气权重 1.0，地支中气权重 0.5，地支余气权重 0.3。
    """
    wx_count = {"金": 0.0, "木": 0.0, "水": 0.0, "火": 0.0, "土": 0.0}
    # 天干，权重 1.0
    for gan in [year_gan, month_gan, day_gan, hour_gan]:
        wx_count[TIAN_GAN_WX[gan]] += 1.0
    # 地支藏干加权：本气 1.0，中气 0.5，余气 0.3
    for zhi in [year_zhi, month_zhi, day_zhi, hour_zhi]:
        cang = DI_ZHI_CANG_GAN.get(zhi, [])
        for i, gan in enumerate(cang):
            wx = TIAN_GAN_WX[gan]
            if i == 0:
                wx_count[wx] += 1.0   # 本气
            elif i == 1:
                wx_count[wx] += 0.5   # 中气
            else:
                wx_count[wx] += 0.3   # 余气
    return wx_count


class Bazi:
    def __init__(self, year, month, day, hour, gender='male', lunar=False, longitude=None, minute=0):
        self.gender = gender
        if lunar:
            from .lunar import lunar_to_solar
            result = lunar_to_solar(year, month, day)
            if result:
                year, month, day = result
        self.birth = date(year, month, day)
        self.birth_clock_hour = hour
        self.birth_minute = minute
        self.longitude = longitude
        # 真太阳时校正
        solar_hour = hour + minute / 60.0
        if longitude is not None:
            solar_hour += (longitude - 120.0) * 4.0 / 60.0
        self.birth_hour = int(round(solar_hour)) % 24
        self.solar_hour_raw = solar_hour
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

        self.hour_gan_zhi = compute_hour_gan_zhi(self.day_gan, self.birth_hour)
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

        # 胎元：月干顺推一位，月支顺推三位
        tai_gan_idx = (get_gan_index(self.month_gan) + 1) % 10
        tai_zhi_idx = (get_zhi_index(self.month_zhi) + 3) % 12
        self.tai_yuan = TIAN_GAN[tai_gan_idx] + DI_ZHI[tai_zhi_idx]

        # 命宫：从月支起子时，逆数到生时
        hour_zhi = get_shi_chen_from_hour(hour)
        hour_zhi_idx = DI_ZHI.index(hour_zhi)
        month_zhi_idx = DI_ZHI.index(self.month_zhi)
        ming_zhi_idx = (month_zhi_idx - hour_zhi_idx) % 12
        ming_zhi = DI_ZHI[ming_zhi_idx]
        # 命宫天干用五虎遁法（年干定月干同样规则）
        year_gan_idx = get_gan_index(self.year_gan)
        start_map = {0: 2, 1: 4, 2: 6, 3: 8, 4: 0}  # 甲己→丙寅
        ming_start = start_map[year_gan_idx % 5]
        ming_gan_idx = (ming_start + ming_zhi_idx) % 10
        self.ming_gong = TIAN_GAN[ming_gan_idx] + ming_zhi

        # 身宫：从月支起子时，顺数到生时
        shen_zhi_idx = (month_zhi_idx + hour_zhi_idx) % 12
        shen_zhi = DI_ZHI[shen_zhi_idx]
        shen_gan_idx = (ming_start + shen_zhi_idx) % 10
        self.shen_gong = TIAN_GAN[shen_gan_idx] + shen_zhi

        self.day_wx = TIAN_GAN_WX[self.day_gan]
        self.sheng_xiao = SHENG_XIAO[DI_ZHI.index(self.year_zhi)]

        # 神煞
        from .core import (compute_shen_sha, compute_month_shen_sha, get_xun_kong, get_shier_changsheng,
                            SHEN_SHA_NAMES, TIAN_YI_GUI_REN, WEN_CHANG, TAO_HUA_MAP,
                            YI_MA_MAP, HUA_GAI_MAP, YANG_REN, JIANG_XING_MAP,
                            LU_SHEN_MAP, JIN_YU_MAP, XUE_TANG_MAP,
                            HONG_LUAN_MAP, TIAN_XI_MAP, GU_CHEN_MAP, GUA_SU_MAP,
                            JIE_SHA_MAP, ZAI_SHA_MAP, TAI_JI_MAP, FU_XING_MAP, JIN_KUI_MAP,
                            TIAN_CHU_MAP, GUO_YIN_MAP, KUI_GANG, WANG_SHEN_MAP, FEI_REN_MAP,
                            SANG_MEN_MAP, DIAO_KE_MAP, BAI_HU_MAP, XUE_REN_MAP,
                            GOU_JIAO_MAP, SAN_QI, SHI_E_DA_BAI, TIAN_LUO_DI_WANG, YUAN_CHEN_MAP,
                            TIAN_GUAN_MAP, RI_DE, RI_GUI, JIN_SHEN_HOURS, BA_ZHUAN, JIU_CHOU,
                            YIN_CUO_YANG_CHA, LIU_E_MAP, PI_MA_MAP, SI_FEI_MAP, PO_SUI)
        pillars_zhi = [self.year_zhi, self.month_zhi, self.day_zhi, self.hour_zhi]
        self.shen_sha = compute_shen_sha(self.day_gan, self.year_zhi, self.day_zhi, pillars_zhi)
        # 合并月支神煞
        month_ss = compute_month_shen_sha(self.month_zhi, pillars_zhi)
        for k, v in month_ss.items():
            if k not in self.shen_sha:
                self.shen_sha[k] = v
            else:
                self.shen_sha[k].extend(v)
        # 空亡（以日柱所在旬为准）
        day_idx = JIA_ZI.index(self.day_gan_zhi)
        self.xun_kong = get_xun_kong(day_idx)
        # 日主十二长生
        self.chang_sheng = {
            "年": get_shier_changsheng(self.day_gan, self.year_zhi),
            "月": get_shier_changsheng(self.day_gan, self.month_zhi),
            "日": get_shier_changsheng(self.day_gan, self.day_zhi),
            "时": get_shier_changsheng(self.day_gan, self.hour_zhi),
        }
        # 地支十神：每个藏干对日主的十神
        self.di_zhi_shi_shen = {}
        for label, zhi in [("年", self.year_zhi), ("月", self.month_zhi),
                            ("日", self.day_zhi), ("时", self.hour_zhi)]:
            cang = DI_ZHI_CANG_GAN.get(zhi, [])
            self.di_zhi_shi_shen[label] = [compute_shi_shen(self.day_gan, g) for g in cang]
        # 每柱的神煞（完整版）
        self.pillar_shen_sha = {"年": [], "月": [], "日": [], "时": []}
        pillar_label_zhi = [("年", self.year_zhi), ("月", self.month_zhi),
                            ("日", self.day_zhi), ("时", self.hour_zhi)]
        # Build lookup: {shensha_name: target_zhi_or_list}
        shensha_checks = []
        # 日干查
        tian_yi_list = TIAN_YI_GUI_REN.get(self.day_gan, [])
        shensha_checks.append(("天乙贵人", tian_yi_list))
        wc = WEN_CHANG.get(self.day_gan)
        if wc: shensha_checks.append(("文昌", [wc]))
        yr = YANG_REN.get(self.day_gan)
        if yr: shensha_checks.append(("羊刃", [yr]))
        fr = FEI_REN_MAP.get(self.day_gan)
        if fr: shensha_checks.append(("飞刃", [fr]))
        ls = LU_SHEN_MAP.get(self.day_gan)
        if ls: shensha_checks.append(("禄神", [ls]))
        jy = JIN_YU_MAP.get(self.day_gan)
        if jy: shensha_checks.append(("金舆", [jy]))
        xt = XUE_TANG_MAP.get(self.day_gan)
        if xt: shensha_checks.append(("学堂", [xt]))
        tj_list = TAI_JI_MAP.get(self.day_gan, [])
        if tj_list: shensha_checks.append(("太极贵人", tj_list))
        fx = FU_XING_MAP.get(self.day_gan)
        if fx: shensha_checks.append(("福星贵人", [fx]))
        tc = TIAN_CHU_MAP.get(self.day_gan)
        if tc: shensha_checks.append(("天厨贵人", [tc]))
        gy = GUO_YIN_MAP.get(self.day_gan)
        if gy: shensha_checks.append(("国印贵人", [gy]))
        # 三奇贵人：检查年干+月干+日干
        year_gan = self.year_gan_zhi[0]
        month_gan = self.month_gan_zhi[0]
        gan_trio = {year_gan, month_gan, self.day_gan}
        if gan_trio in SAN_QI:
            shensha_checks.append(("三奇贵人", [self.day_zhi]))
        # 魁罡：日柱
        if self.day_gan_zhi in KUI_GANG:
            shensha_checks.append(("魁罡", [self.day_zhi]))
        # 天官贵人
        tg = TIAN_GUAN_MAP.get(self.day_gan)
        if tg: shensha_checks.append(("天官贵人", [tg]))
        # 十恶大败
        if self.day_gan_zhi in SHI_E_DA_BAI:
            shensha_checks.append(("十恶大败", [self.day_zhi]))
        # 日德
        if self.day_gan_zhi in RI_DE:
            shensha_checks.append(("日德", [self.day_zhi]))
        # 日贵
        if self.day_gan_zhi in RI_GUI:
            shensha_checks.append(("日贵", [self.day_zhi]))
        # 八专
        if self.day_gan_zhi in BA_ZHUAN:
            shensha_checks.append(("八专", [self.day_zhi]))
        # 九丑
        if self.day_gan_zhi in JIU_CHOU:
            shensha_checks.append(("九丑", [self.day_zhi]))
        # 阴错阳差
        if self.day_gan_zhi in YIN_CUO_YANG_CHA:
            shensha_checks.append(("阴错阳差", [self.day_zhi]))
        # 金神：时柱查
        if self.hour_gan_zhi in JIN_SHEN_HOURS:
            shensha_checks.append(("金神", [self.hour_zhi]))
        # 四废：月支+日柱
        si_fei_set = SI_FEI_MAP.get(self.month_zhi, set())
        if self.day_gan_zhi in si_fei_set:
            shensha_checks.append(("四废", [self.day_zhi]))
        # 破碎：日支查
        ps = PO_SUI.get(self.day_zhi)
        if ps:
            shensha_checks.append(("破碎", [ps]))
        # 年支查
        for name, m in [("桃花",TAO_HUA_MAP),("驿马",YI_MA_MAP),("华盖",HUA_GAI_MAP),
                         ("将星",JIANG_XING_MAP),("红鸾",HONG_LUAN_MAP),("天喜",TIAN_XI_MAP),
                         ("孤辰",GU_CHEN_MAP),("寡宿",GUA_SU_MAP),("劫煞",JIE_SHA_MAP),
                         ("灾煞",ZAI_SHA_MAP),("金匮",JIN_KUI_MAP),
                         ("亡神",WANG_SHEN_MAP),("元辰",YUAN_CHEN_MAP),
                         ("丧门",SANG_MEN_MAP),("吊客",DIAO_KE_MAP),("白虎",BAI_HU_MAP)]:
            s = m.get(self.year_zhi)
            if s: shensha_checks.append((name, [s]))
        # 勾绞（特殊：两个值）
        gj = GOU_JIAO_MAP.get(self.year_zhi, {})
        if gj:
            if '勾' in gj: shensha_checks.append(("勾绞", [gj['勾']]))
        le = LIU_E_MAP.get(self.year_zhi)
        if le: shensha_checks.append(("六厄", [le]))
        pm = PI_MA_MAP.get(self.year_zhi)
        if pm: shensha_checks.append(("披麻", [pm]))
        # 月支查：血刃
        xr = XUE_REN_MAP.get(self.month_zhi)
        if xr: shensha_checks.append(("血刃", [xr]))
        # 天罗地网
        for z in TIAN_LUO_DI_WANG:
            shensha_checks.append(("天罗地网", [z]))
        # Check each pillar
        for label, zhi in pillar_label_zhi:
            for ss_name, target_list in shensha_checks:
                if zhi in target_list:
                    self.pillar_shen_sha[label].append(ss_name)

    def display(self):
        lunar_y, lunar_m, lunar_d, lunar_leap = self.lunar_date
        leap_str = "(闰)" if lunar_leap else ""
        wx_bars = []
        # 五行分布：显示加权分数（保留1位小数）
        max_val = max(self.wu_xing.values()) if self.wu_xing else 1
        for wx, count in self.wu_xing.items():
            cnt_int = int(count)
            cnt_str = f"{count:.1f}" if count != int(count) else str(cnt_int)
            bar_len = max(1, int(count / max(max_val, 1) * 10))
            bar = "█" * bar_len + "░" * (10 - bar_len)
            wx_bars.append(f"  {wx}: {bar} {cnt_str}")

        dayun_lines = []
        for i, (gz, age) in enumerate(self.da_yun[:8]):
            dayun_lines.append(f"  {gz}({age}岁)")
        dayun_rows = []
        for i in range(0, len(dayun_lines), 4):
            dayun_rows.append("  ".join(dayun_lines[i:i+4]))

        # 构建每柱的藏干带五行
        def _cang_str(zhi):
            cang = DI_ZHI_CANG_GAN.get(zhi, [])
            return ', '.join([f'{g}({TIAN_GAN_WX[g]})' for g in cang])

        def _zhi_wx_str(zhi):
            return f'{zhi}({DI_ZHI_WX[zhi]})'

        def _ss_list(label):
            return ', '.join(self.di_zhi_shi_shen.get(label, []))

        def _sha_list(label):
            sa = self.pillar_shen_sha.get(label, [])
            return ', '.join(sa) if sa else '—'

        col_w = 22  # column width
        sep = "  │  "

        def _cell(content, width=col_w):
            return f"{content:^{width}}"

        def _row(label, y_data, m_data, d_data, h_data):
            return f"  {_cell(label, 6)}{sep}{_cell(y_data)}{sep}{_cell(m_data)}{sep}{_cell(d_data)}{sep}{_cell(h_data)}"

        def _divider():
            return f"  {'─'*6}─┼─{'─'*col_w}─┼─{'─'*col_w}─┼─{'─'*col_w}─┼─{'─'*col_w}"

        lines = [
            "=" * 60,
            "                        四柱八字命盘",
            "=" * 60,
            f"公历: {self.birth.year}年{self.birth.month}月{self.birth.day}日 {self.birth_hour}时",
            f"农历: {lunar_y}年{leap_str}{lunar_m}月{lunar_d}日",
            f"生肖: {self.sheng_xiao}    性别: {'男' if self.gender == 'male' else '女'}    日主: {self.day_gan}({self.day_wx})",
            f"空亡: {'、'.join(self.xun_kong)}    胎元: {self.tai_yuan}    命宫: {self.ming_gong}    身宫: {self.shen_gong}",
            "",
            _row("", "年柱", "月柱", "日柱", "时柱"),
            _divider(),
            _row("干支", self.year_gan_zhi, self.month_gan_zhi, self.day_gan_zhi, self.hour_gan_zhi),
            _row("纳音", self.na_yin['年'], self.na_yin['月'], self.na_yin['日'], self.na_yin['时']),
            _divider(),
            _row("十神", self.shi_shen['年'], self.shi_shen['月'], self.shi_shen['日'], self.shi_shen['时']),
            _row("天干",
                 f"{self.year_gan}({TIAN_GAN_WX[self.year_gan]})",
                 f"{self.month_gan}({TIAN_GAN_WX[self.month_gan]})",
                 f"{self.day_gan}({TIAN_GAN_WX[self.day_gan]})",
                 f"{self.hour_gan}({TIAN_GAN_WX[self.hour_gan]})"),
            _row("地支",
                 _zhi_wx_str(self.year_zhi),
                 _zhi_wx_str(self.month_zhi),
                 _zhi_wx_str(self.day_zhi),
                 _zhi_wx_str(self.hour_zhi)),
            _row("藏干",
                 _cang_str(self.year_zhi),
                 _cang_str(self.month_zhi),
                 _cang_str(self.day_zhi),
                 _cang_str(self.hour_zhi)),
            _row("地支十神",
                 _ss_list("年"),
                 _ss_list("月"),
                 _ss_list("日"),
                 _ss_list("时")),
            _row("长生",
                 self.chang_sheng["年"],
                 self.chang_sheng["月"],
                 self.chang_sheng["日"],
                 self.chang_sheng["时"]),
            _row("神煞",
                 _sha_list("年"),
                 _sha_list("月"),
                 _sha_list("日"),
                 _sha_list("时")),
            "",
            "",
            "【五行分布】",
        ] + wx_bars + [
            f"  日主{self.day_wx}: {self._get_strength_label()}",
            "",
            "【大运排盘】",
        ] + dayun_rows + [
            "",
            "=" * 50,
        ]
        # 喜用神和忌神
        from .bazi_analysis import derive_yong_shen, analyze_xi_yong_shen
        yong_shen, ji_shen, xian_shen = derive_yong_shen(self.day_gan, self.day_wx, 
            "旺" if self.wu_xing[self.day_wx] >= 3 else "弱")
        lines.append("")
        lines.append("【喜用神·忌神】")
        if yong_shen:
            lines.append(f"  用神: {', '.join(yong_shen)}")
        else:
            lines.append("  用神: 需结合具体格局判断")
        if ji_shen:
            lines.append(f"  忌神: {', '.join(ji_shen)}")
        else:
            lines.append("  忌神: 需结合具体格局判断")
        if xian_shen:
            lines.append(f"  闲神: {', '.join(xian_shen)}")
        # 五行缺失提示
        missing = [wx for wx, cnt in self.wu_xing.items() if cnt == 0]
        over = [wx for wx, cnt in self.wu_xing.items() if cnt >= 3.5]
        if missing:
            lines.append(f"\n【五行提示】缺失：{'、'.join(missing)}")
        if over:
            lines.append(f"  过旺：{'、'.join(over)}")

        lines.append("")
        lines.append("=" * 50)
        return "\n".join(lines)
    def _get_strength_label(self):
        """使用 analyze_day_master_strength 判断日主旺衰。"""
        from .bazi_analysis import analyze_day_master_strength
        level, _ = analyze_day_master_strength(
            self.day_gan, self.day_zhi, self.month_zhi,
            self.year_gan, self.month_gan, self.hour_gan,
            self.year_zhi, self.hour_zhi,
        )
        return level

    def analyze(self):
        from .bazi_analysis import full_bazi_analysis, format_bazi_analysis
        return full_bazi_analysis(self)

    def display_with_analysis(self):
        from .bazi_analysis import format_bazi_analysis, full_bazi_analysis
        base = self.display()
        analysis = full_bazi_analysis(self)
        return base + "\n" + format_bazi_analysis(analysis)


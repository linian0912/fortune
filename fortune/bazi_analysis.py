# -*- coding: utf-8 -*-
"""八字命理分析模块：用神忌神、格局判断、五行解读、大运分析。"""

from .core import (
    TIAN_GAN, DI_ZHI, TIAN_GAN_WX, TIAN_GAN_YY,
    DI_ZHI_WX, DI_ZHI_CANG_GAN, WX_RELATION, SHENG_XIAO,
    get_gan_index, get_zhi_index,
)

WX_ORDER = ["金", "木", "水", "火", "土"]
WX_SHENG = {"金": "水", "水": "木", "木": "火", "火": "土", "土": "金"}  # 我生
WX_KE = {"金": "木", "木": "土", "土": "水", "水": "火", "火": "金"}      # 我克
WX_SHENG_WO = {v: k for k, v in WX_SHENG.items()}  # 生我
WX_KE_WO = {v: k for k, v in WX_KE.items()}        # 克我


def _count_wx_in_zhi(zhi):
    """统计地支中各五行藏干数量。"""
    wx_count = {}
    for gan in DI_ZHI_CANG_GAN.get(zhi, []):
        wx = TIAN_GAN_WX[gan]
        wx_count[wx] = wx_count.get(wx, 0) + 1
    return wx_count


def analyze_day_master_strength(day_gan, day_zhi, month_zhi, year_gan, month_gan, hour_gan, year_zhi, hour_zhi):
    """判断日主旺衰，返回级别和理由。"""
    day_wx = TIAN_GAN_WX[day_gan]
    month_wx = DI_ZHI_WX[month_zhi]

    score = 0
    reasons = []

    # 1. 月令当令（最重要）
    if month_wx == day_wx:
        score += 3
        reasons.append(f"月令{month_zhi}为{day_wx}，日主当令")
    elif WX_SHENG_WO.get(day_wx) == month_wx:
        score += 2
        reasons.append(f"月令{month_zhi}为{day_wx}之印星，得月令生扶")
    elif WX_KE.get(day_wx) == month_wx:
        score -= 2
        reasons.append(f"月令{month_zhi}为{day_wx}之财星，月令耗身")
    elif WX_SHENG.get(day_wx) == month_wx:
        score -= 1
        reasons.append(f"月令{month_zhi}为{day_wx}之食伤，月令泄身")

    # 2. 天干助力
    for gan in [year_gan, month_gan, hour_gan]:
        wx = TIAN_GAN_WX[gan]
        if wx == day_wx:
            score += 1
            reasons.append(f"天干{gan}({wx})为比劫助身")
        elif WX_SHENG_WO.get(day_wx) == wx:
            score += 1
            reasons.append(f"天干{gan}({wx})为正偏印生身")

    # 3. 地支通根
    for label, zhi in [("年", year_zhi), ("月", month_zhi), ("日", day_zhi), ("时", hour_zhi)]:
        zhi_wx = DI_ZHI_WX[zhi]
        if zhi_wx == day_wx:
            score += 1
            reasons.append(f"{label}支{zhi}为{day_wx}，日主有根")
        elif WX_SHENG_WO.get(day_wx) == zhi_wx:
            score += 0.5
        cang = _count_wx_in_zhi(zhi)
        if day_wx in cang:
            score += cang[day_wx] * 0.3
            reasons.append(f"{label}支藏{day_wx}，通根")

    # 4. 判断
    if score >= 4:
        level = "旺"
    elif score >= 2:
        level = "偏旺"
    elif score >= 0:
        level = "中和"
    elif score >= -2:
        level = "偏弱"
    else:
        level = "弱"

    return level, reasons


def derive_yong_shen(day_gan, day_wx, strength_level):
    """根据日主旺衰推导用神和忌神。"""
    yong_shen = []
    ji_shen = []
    xian_shen = []

    if strength_level in ("旺", "偏旺"):
        # 身旺取克泄耗为用：官杀、食伤、财
        ke_wx = WX_KE_WO.get(day_wx)  # 克我的 = 官杀
        xie_wx = WX_SHENG.get(day_wx)  # 我生的 = 食伤
        hao_wx = WX_KE.get(day_wx)     # 我克的 = 财

        if ke_wx:
            yong_shen.append(f"{ke_wx}(官杀·克身)")
        if xie_wx:
            yong_shen.append(f"{xie_wx}(食伤·泄身)")
        if hao_wx:
            yong_shen.append(f"{hao_wx}(财星·耗身)")

        ji_shen.append(f"{day_wx}(比劫·助旺)加剧身旺")
        sheng_wo = WX_SHENG_WO.get(day_wx)
        if sheng_wo:
            ji_shen.append(f"{sheng_wo}(印星·生身)加剧身旺")

        # 闲神
        all_wx = set(WX_ORDER)
        used = {ke_wx, xie_wx, hao_wx, day_wx, sheng_wo}
        for w in all_wx - used - {None}:
            xian_shen.append(w)
    else:
        # 身弱取生扶为用：印星、比劫
        sheng_wo = WX_SHENG_WO.get(day_wx)
        if sheng_wo:
            yong_shen.append(f"{sheng_wo}(印星·生身)")
        yong_shen.append(f"{day_wx}(比劫·助身)")

        ke_wx = WX_KE_WO.get(day_wx)
        if ke_wx:
            ji_shen.append(f"{ke_wx}(官杀·克身)")
        xie_wx = WX_SHENG.get(day_wx)
        if xie_wx:
            ji_shen.append(f"{xie_wx}(食伤·泄身)")
        hao_wx = WX_KE.get(day_wx)
        if hao_wx:
            ji_shen.append(f"{hao_wx}(财星·耗身)")

    return yong_shen, ji_shen, xian_shen


def analyze_ge_ju(month_zhi, month_gan, day_gan, shi_shen):
    """判断八字格局（正格为主）。"""
    month_shi_shen = shi_shen.get("月", "")
    # 月令十神即为格局
    ge_ju = []
    if month_shi_shen and month_shi_shen not in ("日主",):
        ge_ju.append(f"{month_shi_shen}格")

    # 特殊格局判断
    # 从格粗略判断
    # （这里做简化，完整判断需要更复杂逻辑）
    return ge_ju


def analyze_wu_xing_balance(wu_xing_count, day_wx, strength_level):
    """五行平衡分析。"""
    analysis = []
    total = sum(wu_xing_count.values())

    for wx in WX_ORDER:
        count = wu_xing_count.get(wx, 0)
        pct = count / max(total, 1) * 100

        if count >= 5:
            analysis.append(f"{wx}极旺（{count}个），需用{WX_KE.get(wx, '?')}来克或{WX_SHENG.get(wx, '?')}来泄")
        elif count >= 3:
            analysis.append(f"{wx}偏旺（{count}个）")
        elif count == 0:
            analysis.append(f"{wx}缺失（0个），命局缺{wx}")
        elif count <= 1:
            analysis.append(f"{wx}偏弱（{count}个）")

    return analysis


def analyze_da_yun(day_wx, yong_gan_wx, da_yun, current_age=None):
    """大运吉凶分析。"""
    analysis = []
    for i, (gz, age) in enumerate(da_yun[:8]):
        g, z = gz[0], gz[1]
        g_wx = TIAN_GAN_WX[g]
        z_wx = DI_ZHI_WX[z]

        # 判断此大运天干地支对日主是喜是忌
        gan_comment = ""
        if g_wx == day_wx:
            gan_comment = "比劫运"
        elif WX_SHENG_WO.get(day_wx) == g_wx:
            gan_comment = "印运"
        elif WX_KE_WO.get(day_wx) == g_wx:
            gan_comment = "官杀运"
        elif WX_SHENG.get(day_wx) == g_wx:
            gan_comment = "食伤运"
        elif WX_KE.get(day_wx) == g_wx:
            gan_comment = "财运"

        analysis.append({
            "gz": gz, "age": age,
            "gan_wx": g_wx, "zhi_wx": z_wx,
            "gan_comment": gan_comment,
            "zhi": z,
        })
    return analysis



# ============================================================
# 喜用神深度解读
# ============================================================

XI_YONG_SHEN_ADVICE = {
    "金": {
        "direction": "西方、西北方",
        "color": "白色、金色、银色",
        "career": "金融、法律、机械、工程、金属行业、汽车、珠宝",
        "lifestyle": "佩戴金属饰品，居家宜用白色调，多接触金属器皿",
        "season": "秋季最旺",
    },
    "木": {
        "direction": "东方、东南方",
        "color": "绿色、青色",
        "career": "教育、文化、出版、园林、医药、环保、设计",
        "lifestyle": "养绿植，穿绿色衣物，多接触大自然和森林",
        "season": "春季最旺",
    },
    "水": {
        "direction": "北方",
        "color": "黑色、蓝色",
        "career": "贸易、物流、旅游、传媒、通讯、水产、航海",
        "lifestyle": "多饮水，养鱼，靠近水源居住，穿深色衣物",
        "season": "冬季最旺",
    },
    "火": {
        "direction": "南方",
        "color": "红色、紫色、橙色",
        "career": "餐饮、能源、演艺、互联网、电子、美容、化工",
        "lifestyle": "多接触阳光，穿暖色调，使用红色饰品",
        "season": "夏季最旺",
    },
    "土": {
        "direction": "中部、西南方",
        "color": "黄色、棕色、咖啡色",
        "career": "房地产、建筑、农业、矿产、陶瓷、仓储",
        "lifestyle": "多用陶瓷器皿，穿暖黄棕色系，居家宜稳重风格",
        "season": "四季末（辰戌丑未月）最旺",
    },
}

WX_KE_WO_WX = {v: k for k, v in WX_KE.items()}
WX_SHENG_WX = WX_SHENG
WX_KE_WX = WX_KE


def analyze_xi_yong_shen(yong_shen, wu_xing_count, strength_level):
    """深度分析喜用神，给出具体的生活建议（增强版）。"""
    result = {
        "first_yong_shen": None,
        "advice": {},
        "supplement": [],
        "avoid": [],
        "all_yong_detail": [],
    }

    if not yong_shen:
        return result

    # 从用神列表中提取五行
    yong_wx_list = []
    for ys in yong_shen:
        wx = ys.split("(")[0] if "(" in ys else ys
        yong_wx_list.append(wx)

    # 第一用神：优先取缺失或最弱的五行
    first = None
    for wx in yong_wx_list:
        cnt = wu_xing_count.get(wx, 0)
        if cnt == 0:
            first = wx
            break
    if not first:
        first = min(yong_wx_list, key=lambda w: wu_xing_count.get(w, 10), default=None)
    if not first and yong_wx_list:
        first = yong_wx_list[0]

    result["first_yong_shen"] = first

    if first and first in XI_YONG_SHEN_ADVICE_DETAIL:
        advice = XI_YONG_SHEN_ADVICE_DETAIL[first]
        result["advice"] = advice

        result["supplement"].append(f"有利方位：{advice['direction']}")
        result["supplement"].append(f"幸运颜色：{advice['color']}")
        result["supplement"].append(f"适合行业：{advice['career']}")
        result["supplement"].append(f"生活建议：{advice['lifestyle']}")
        result["supplement"].append(f"旺运季节：{advice['season']}")
        result["supplement"].append(f"性格特质：{advice['personality']}")
        result["supplement"].append(f"合作伙伴：{advice['partner']}")
        result["supplement"].append(f"财富风格：{advice['wealth_style']}")
        result["supplement"].append(f"健康提醒：{advice['health_tip']}")

        ke_first = WX_KE_WO_WX.get(first)
        if ke_first and ke_first in XI_YONG_SHEN_ADVICE_DETAIL:
            result["avoid"].append(f"忌{ke_first}过旺，少用{XI_YONG_SHEN_ADVICE_DETAIL[ke_first]['color']}")
        sheng_ke = WX_SHENG_WX.get(ke_first or "", "")
        if sheng_ke and sheng_ke != first:
            result["avoid"].append(f"忌{sheng_ke}过旺（生助克{first}之五行）")

    for wx in yong_wx_list:
        if wx in XI_YONG_SHEN_ADVICE_DETAIL:
            result["all_yong_detail"].append({
                "wx": wx,
                "advice": XI_YONG_SHEN_ADVICE_DETAIL[wx],
            })

    return result



# ============================================================
# 忌神深度分析
# ============================================================

JI_SHEN_WARNING = {
    "比劫": {
        "description": "比劫为忌时，命主易固执己见、竞争心过强，人际关系紧张",
        "career": "事业中易遇强力竞争者，合作伙伴关系需谨慎处理",
        "wealth": "财来财去不易聚财，与他人合作易生纠纷",
        "marriage": "婚姻中有竞争意识，配偶关系需注意平衡",
        "health": "体质虽强但易透支过度，注意劳逸结合",
        "advice": [
            "学会分享与合作，避免独断专行",
            "财务上宜独立，避免合伙投资",
            "多听取他人意见，培养包容心",
        ],
    },
    "印星": {
        "description": "印星为忌时，命主易过于依赖他人、缺乏主见，懒散依赖",
        "career": "工作中缺乏主动性，过于依赖上级或贵人，自主能力偏弱",
        "wealth": "理财观念薄弱，容易因轻信他人而破财",
        "marriage": "对配偶依赖过重，婚姻中缺乏独立性",
        "health": "体质偏弱易疲劳，注意加强锻炼",
        "advice": [
            "培养独立自主意识，减少依赖心理",
            "主动学习新技能，提升竞争力",
            "适度锻炼增强体质和意志力",
        ],
    },
    "官杀": {
        "description": "官杀为忌时，压力过大、易受约束，健康受损",
        "career": "职场压力大，易受上司压制，感到喘不过气",
        "wealth": "求财艰难，收入与付出不成正比",
        "marriage": "婚姻中约束感强（女命尤甚），需注意沟通方式",
        "health": "压力导致身心俱疲，注意心脏和神经系统",
        "advice": [
            "学会减压放松，培养兴趣爱好",
            "工作中善用印星化解压力（学习进修）",
            "避免承担过多责任，学会适当拒绝",
        ],
    },
    "食伤": {
        "description": "食伤为忌时，言语易伤人、想法过多不切实际",
        "career": "才华难以施展，容易怀才不遇，或频繁更换工作",
        "wealth": "赚钱辛苦，投资易因过于理想化而失误",
        "marriage": "感情中表达方式欠妥（女命伤官尤忌），影响婚姻稳定",
        "health": "思虑过度伤神，注意神经系统和消化系统",
        "advice": [
            "收敛锋芒，谨言慎行",
            "将才华转化为实际生产力而非空想",
            "培养耐心和持之以恒的精神",
        ],
    },
    "财星": {
        "description": "财星为忌时，易为钱所困、重物质轻精神",
        "career": "过于追求物质回报，容易忽视职业长远发展",
        "wealth": "财多身弱不担财，赚钱机会多但难守住",
        "marriage": "男命财多婚姻不稳定，感情中重物质条件",
        "health": "注意肾脏和泌尿系统，避免过度消耗",
        "advice": [
            "量力而行，不被钱财所困",
            "先强身健体再求财，身强才能担财",
            "培养精神层面的追求，平衡物质与精神",
        ],
    },
}


# ============================================================
# 忌神规避建议（与喜用神建议格式统一）
# ============================================================

JI_SHEN_AVOID_ADVICE = {
    "金": {
        "direction": "西方、西北方",
        "color": "白色、金色、银色",
        "career": "金融、法律、机械、工程、金属行业",
        "lifestyle": "减少金属饰品，居家少用白色调",
        "season": "秋季需注意",
        "warning": "忌金过旺则刚强易折，注意呼吸系统",
    },
    "木": {
        "direction": "东方、东南方",
        "color": "绿色、青色",
        "career": "教育、文化、出版、园林行业",
        "lifestyle": "减少绿植，少穿绿色衣物",
        "season": "春季需注意",
        "warning": "忌木过旺则固执己见，注意肝胆",
    },
    "水": {
        "direction": "北方",
        "color": "黑色、蓝色",
        "career": "贸易、物流、旅游、传媒行业",
        "lifestyle": "避免临水而居，少养鱼",
        "season": "冬季需注意",
        "warning": "忌水过旺则情绪波动，注意肾脏",
    },
    "火": {
        "direction": "南方",
        "color": "红色、紫色、橙色",
        "career": "餐饮、能源、演艺、互联网行业",
        "lifestyle": "避免暴晒，少用红色装饰",
        "season": "夏季需注意",
        "warning": "忌火过旺则急躁冲动，注意心脏血液",
    },
    "土": {
        "direction": "中部、西南方",
        "color": "黄色、棕色、咖啡色",
        "career": "房地产、建筑、农业、矿产行业",
        "lifestyle": "少用陶瓷器皿，居家宜简约风格",
        "season": "四季末需注意",
        "warning": "忌土过旺则思维僵化，注意脾胃消化",
    },
}


def analyze_ji_shen_avoid(ji_shen, wu_xing_count):
    """为忌神生成具体的规避建议，格式与喜用神一致。"""
    result = {
        "avoid_items": [],
        "avoid_detail": [],
    }
    
    if not ji_shen:
        return result
    
    ji_wx_list = []
    for js in ji_shen:
        wx = js.split("(")[0] if "(" in js else js
        ji_wx_list.append(wx)
    
    # 取命中数量最多的忌神作为主要规避对象
    strongest_ji = None
    max_cnt = 0
    for wx in ji_wx_list:
        cnt = wu_xing_count.get(wx, 0)
        if cnt > max_cnt:
            max_cnt = cnt
            strongest_ji = wx
    
    # 为每个忌神生成规避建议
    for wx in ji_wx_list:
        if wx in JI_SHEN_AVOID_ADVICE:
            adv = JI_SHEN_AVOID_ADVICE[wx]
            cnt = wu_xing_count.get(wx, 0)
            marker = " ⚠ 核心规避" if wx == strongest_ji else ""
            result["avoid_detail"].append({
                "wx": wx,
                "count": cnt,
                "advice": adv,
                "is_primary": wx == strongest_ji,
            })
            if wx == strongest_ji:
                result["avoid_items"].append(f"⚠ 核心忌神{wx}：{adv['warning']}")
                result["avoid_items"].append(f"   规避方位：{adv['direction']}")
                result["avoid_items"].append(f"   规避颜色：{adv['color']}")
                result["avoid_items"].append(f"   规避行业：{adv['career']}")
                result["avoid_items"].append(f"   生活注意：{adv['lifestyle']}")
                result["avoid_items"].append(f"   当心季节：{adv['season']}")
    
    return result



def analyze_ji_shen_detail(ji_shen, day_wx, wu_xing_count, strength_level):
    """对忌神进行详细分析，给出针对性的警告和建议。"""
    result = {
        "ji_shen_list": [],
        "warnings": [],
        "advice": [],
        "strongest_ji": None,
    }
    
    if not ji_shen:
        return result
    
    # 提取忌神五行
    ji_wx_map = {}
    for js in ji_shen:
        wx = js.split("(")[0] if "(" in js else js
        # 判断忌神类型
        if "比劫" in js:
            category = "比劫"
        elif "印星" in js:
            category = "印星"
        elif "官杀" in js:
            category = "官杀"
        elif "食伤" in js:
            category = "食伤"
        elif "财星" in js:
            category = "财星"
        else:
            category = wx
        
        cnt = wu_xing_count.get(wx, 0)
        ji_wx_map[wx] = {"category": category, "wx": wx, "count": cnt, "description": js}
    
    # 找出最强的忌神（命中数量最多的）
    if ji_wx_map:
        strongest = max(ji_wx_map.values(), key=lambda x: x["count"])
        result["strongest_ji"] = strongest["description"]
    
    # 为每个忌神生成详细分析
    for wx, info in ji_wx_map.items():
        category = info["category"]
        warning = JI_SHEN_WARNING.get(category)
        
        item = {
            "wx": wx,
            "category": category,
            "count": info["count"],
            "description": info["description"],
        }
        
        if warning:
            item["meaning"] = warning["description"]
            item["career_impact"] = warning["career"]
            item["wealth_impact"] = warning["wealth"]
            item["marriage_impact"] = warning["marriage"]
            item["health_impact"] = warning["health"]
            item["specific_advice"] = warning["advice"]
            
            # 添加到警告列表
            if info["count"] >= 2:
                result["warnings"].append(f"⚠ {wx}({category})过旺，{warning['description']}")
            else:
                result["warnings"].append(f"⚠ {wx}({category})为忌，{warning['description']}")
            
            # 添加建议
            result["advice"].extend(warning["advice"])
        
        result["ji_shen_list"].append(item)
    
    # 去重建议
    result["advice"] = list(dict.fromkeys(result["advice"]))
    
    return result


# ============================================================
# 喜用神深度分析（增强版）
# ============================================================

XI_YONG_SHEN_ADVICE_DETAIL = {
    "金": {
        "direction": "西方、西北方",
        "color": "白色、金色、银色",
        "career": "金融、法律、机械、工程、金属行业、汽车、珠宝",
        "lifestyle": "佩戴金属饰品，居家宜用白色调，多接触金属器皿",
        "season": "秋季最旺",
        "personality": "用金者刚毅果断，有决断力，适合需要魄力的角色",
        "partner": "金水相生，适合搭配水属性强的伴侣或合作伙伴",
        "wealth_style": "以刚克柔，适合硬资产投资（贵金属、机械设备）",
        "health_tip": "多补充矿物质，深呼吸有利肺金之气",
    },
    "木": {
        "direction": "东方、东南方",
        "color": "绿色、青色",
        "career": "教育、文化、出版、园林、医药、环保、设计",
        "lifestyle": "养绿植，穿绿色衣物，多接触大自然和森林",
        "season": "春季最旺",
        "personality": "用木者有仁爱之心，善于成长和开拓",
        "partner": "木火通明，适合搭配火属性强的伙伴以激发创造力",
        "wealth_style": "以柔克刚，适合长期成长型投资（教育、绿色产业）",
        "health_tip": "多吃绿色蔬菜，伸展运动有利肝胆木气",
    },
    "水": {
        "direction": "北方",
        "color": "黑色、蓝色",
        "career": "贸易、物流、旅游、传媒、通讯、水产、航海",
        "lifestyle": "多饮水，养鱼，靠近水源居住，穿深色衣物",
        "season": "冬季最旺",
        "personality": "用水者智慧灵活，善于变通和沟通",
        "partner": "水木相生，适合搭配木属性强的伙伴以助成长",
        "wealth_style": "流动生财，适合流动性强的投资（贸易、物流、金融产品）",
        "health_tip": "保持充足饮水，游泳有益肾水之气",
    },
    "火": {
        "direction": "南方",
        "color": "红色、紫色、橙色",
        "career": "餐饮、能源、演艺、互联网、电子、美容、化工",
        "lifestyle": "多接触阳光，穿暖色调，使用红色饰品",
        "season": "夏季最旺",
        "personality": "用火者热情主动，有感染力，善于表达和领导",
        "partner": "火土相生，适合搭配土属性强的伙伴以稳固根基",
        "wealth_style": "借势生财，适合热门行业和高增长投资",
        "health_tip": "适度晒太阳，保持心情愉悦有利心火之气",
    },
    "土": {
        "direction": "中部、西南方",
        "color": "黄色、棕色、咖啡色",
        "career": "房地产、建筑、农业、矿产、陶瓷、仓储",
        "lifestyle": "多用陶瓷器皿，穿暖黄棕色系，居家宜稳重风格",
        "season": "四季末（辰戌丑未月）最旺",
        "personality": "用土者稳重诚实，有信用，适合需要信任的岗位",
        "partner": "土金相生，适合搭配金属性强的伙伴以增强执行力",
        "wealth_style": "稳重增值，适合不动产和长期稳健投资",
        "health_tip": "注意饮食规律养脾胃，太极等温和运动有利土气",
    },
}

# ============================================================
# 十神深度分析
# ============================================================

SHI_SHEN_MEANING = {
    "比肩": "代表自己、兄弟姐妹、朋友、同事、竞争。比肩旺为人独立自主，但过旺易固执、不善合作。",
    "劫财": "代表同辈竞争、破财、冲动。劫财旺者行动力强，但需防冲动破财、人际关系复杂。",
    "食神": "代表才华、享受、口福、艺术天赋。食神旺者温和善良、有创造力，是福星。",
    "伤官": "代表聪明才智、创新、叛逆。伤官旺者才华横溢、思维敏捷，但锋芒太露易招是非。",
    "正财": "代表工资收入、正当财富、妻子（男命）。正财旺者勤俭持家、财运稳定。",
    "偏财": "代表意外之财、投资、父亲、情人。偏财旺者慷慨大方、善于理财，但不稳定。",
    "正官": "代表事业、官职、丈夫（女命）、纪律。正官旺者正直守法、事业有成。",
    "七杀": "代表权力、竞争、压力、魄力。七杀旺者果敢有魄力，但压力大，需印星化解。",
    "正印": "代表学识、母亲、贵人、庇护。正印旺者仁慈有学问，但过旺易懒散依赖。",
    "偏印": "代表特殊才能、偏门学问、继母。偏印旺者聪明独特，但孤僻不合群。",
}

SHI_SHEN_LIFE = {
    "比肩": {"婚姻": "比肩多者配偶缘薄，需注意竞争关系", "事业": "适合合伙创业、团队合作", "财运": "财运一般，需合作生财", "健康": "体质较好"},
    "劫财": {"婚姻": "劫财旺易有感情竞争或第三者", "事业": "适合竞争性行业、销售", "财运": "财来财去，需注意守财", "健康": "精力旺盛但易透支"},
    "食神": {"婚姻": "食神旺者温和体贴，婚姻较和谐", "事业": "适合艺术、创作、教育行业", "财运": "食神生财，靠才华赚钱", "健康": "心态好，但注意饮食过量"},
    "伤官": {"婚姻": "伤官见官不利婚姻（女命），感情多变", "事业": "适合创新、设计、技术行业", "财运": "靠聪明才智赚钱", "健康": "思虑过多，注意神经系统"},
    "正财": {"婚姻": "正财旺男命妻贤，婚姻稳定", "事业": "适合稳定职业、财务管理", "财运": "财运稳健，稳步增长", "健康": "注意肾水系统"},
    "偏财": {"婚姻": "偏财旺男命异性缘好，但婚姻不稳", "事业": "适合投资、贸易、自由职业", "财运": "有大财机会，但不稳定", "健康": "注意饮酒过度"},
    "正官": {"婚姻": "正官旺女命夫贵，婚姻美满", "事业": "适合公务员、管理岗位", "财运": "靠职位升迁赚钱", "健康": "压力大注意心脏"},
    "七杀": {"婚姻": "七杀旺女命感情波折，晚婚为宜", "事业": "适合军警、管理、竞争行业", "财运": "权力生财但压力大", "健康": "注意肝胆、压力管理"},
    "正印": {"婚姻": "正印旺者得长辈关爱，婚姻平稳", "事业": "适合教育、文化、学术研究", "财运": "靠知识学问赚钱", "健康": "体质偏弱但少大病"},
    "偏印": {"婚姻": "偏印旺者感情内敛，晚婚为宜", "事业": "适合研究、技术、特殊技能", "财运": "偏门生财，收入不稳定", "健康": "注意消化系统"},
}


def analyze_shi_shen_detail(bazi):
    """对命局中的十神进行深度分析。"""
    shi_shen_list = []
    for pillar in ["年", "月", "日", "时"]:
        ss = bazi.shi_shen.get(pillar, "")
        if ss and ss != "日主":
            shi_shen_list.append(ss)

    position_map = {}
    for pillar in ["年", "月", "日", "时"]:
        ss = bazi.shi_shen.get(pillar, "")
        if ss and ss != "日主":
            position_map[ss] = position_map.get(ss, []) + [pillar]

    shi_shen_analysis = []
    seen = set()
    for ss in shi_shen_list:
        if ss in seen:
            continue
        seen.add(ss)

        meaning = SHI_SHEN_MEANING.get(ss, "")
        life = SHI_SHEN_LIFE.get(ss, {})
        positions = position_map.get(ss, [])
        count = len(positions)

        if count >= 2:
            strength = "强"
        elif count == 1:
            strength = "中"
        else:
            strength = "弱"

        shi_shen_analysis.append({
            "name": ss,
            "count": count,
            "strength": strength,
            "positions": positions,
            "meaning": meaning,
            "life_impact": life,
        })

    shi_shen_analysis.sort(key=lambda x: -x["count"])
    return shi_shen_analysis


def full_bazi_analysis(bazi):
    """对 Bazi 对象进行完整分析，返回结构化结果。"""
    day_wx = bazi.day_wx

    # 1. 日主旺衰
    level, reasons = analyze_day_master_strength(
        bazi.day_gan, bazi.day_zhi, bazi.month_zhi,
        bazi.year_gan, bazi.month_gan, bazi.hour_gan,
        bazi.year_zhi, bazi.hour_zhi,
    )

    # 2. 用神忌神
    yong_shen, ji_shen, xian_shen = derive_yong_shen(bazi.day_gan, day_wx, level)

    # 3. 格局
    ge_ju = analyze_ge_ju(bazi.month_zhi, bazi.month_gan, bazi.day_gan, bazi.shi_shen)

    # 4. 五行分析
    wx_analysis = analyze_wu_xing_balance(bazi.wu_xing, day_wx, level)

    # 5. 大运分析
    da_yun_analysis = analyze_da_yun(day_wx, yong_shen, bazi.da_yun)

    # 6. 喜用神深度解读
    xi_yong = analyze_xi_yong_shen(yong_shen, bazi.wu_xing, level)

    # 7. 十神深度分析
    shi_shen_detail = analyze_shi_shen_detail(bazi)

    # 8. 忌神深度分析
    ji_shen_detail = analyze_ji_shen_detail(ji_shen, day_wx, bazi.wu_xing, level)

    # 9. 忌神规避建议（与喜用神同格式）
    ji_shen_avoid = analyze_ji_shen_avoid(ji_shen, bazi.wu_xing)

    # 10. 起运时间
    qi_yun_age = compute_qi_yun_age(bazi.birth.year, bazi.birth.month, bazi.birth.day,
                                     bazi.gender, bazi.year_gan)

    # 11. 大运吉凶评级
    yong_wx_list = [ys.split("(")[0] if "(" in ys else ys for ys in yong_shen]
    ji_wx_list = [js.split("(")[0] if "(" in js else js for js in ji_shen]
    da_yun_rated = rate_da_yun(bazi.da_yun, day_wx, yong_shen, ji_shen)

    # 12. 命盘综合评分
    overall_score = compute_overall_score(level, yong_shen, ji_shen, bazi.wu_xing,
                                           bazi.shen_sha, ge_ju)

    # 14. 纳音详解
    na_yin_detail = analyze_na_yin_detail(bazi.na_yin)

    # 15. 日柱论命
    ri_zhu_reading = analyze_ri_zhu(bazi.day_gan_zhi)

    # 16. 神煞详解
    shen_sha_detail = analyze_shen_sha_detail(bazi.shen_sha)

    # 17. 四柱逐柱详解
    pillars_detail = {}

    # We need a temp dict with needed fields to pass
    _temp_analysis = {
        "strength": {"level": level, "reasons": reasons},
        "yong_shen": yong_shen,
        "ji_shen": ji_shen,
    }
    pillars_detail = analyze_pillars_detail(bazi, _temp_analysis)

    return {
        "strength": {"level": level, "reasons": reasons},
        "yong_shen": yong_shen,
        "ji_shen": ji_shen,
        "xian_shen": xian_shen,
        "ge_ju": ge_ju,
        "wu_xing_analysis": wx_analysis,
        "da_yun_analysis": da_yun_analysis,
        "xi_yong_shen": xi_yong,
        "shi_shen_detail": shi_shen_detail,
        "ji_shen_detail": ji_shen_detail,
        "ji_shen_avoid": ji_shen_avoid,
        "qi_yun_age": qi_yun_age,
        "da_yun_rated": da_yun_rated,
        "overall_score": overall_score,
        "xing_chong_he": analyze_xing_chong_he([
            ("年", bazi.year_gan_zhi), ("月", bazi.month_gan_zhi),
            ("日", bazi.day_gan_zhi), ("时", bazi.hour_gan_zhi)], bazi.day_gan),
        "na_yin_detail": na_yin_detail,
        "ri_zhu_reading": ri_zhu_reading,
        "shen_sha_detail": shen_sha_detail,
        "pillars_detail": pillars_detail,
    }



# ============================================================
# 起运时间计算
# ============================================================

def compute_qi_yun_age(year, month, day, gender, year_gan):
    """计算起运年龄（从出生到第一个大运的岁数）。
    阳男阴女顺排（从出生到下一个节气），阴男阳女逆排（到上一个节气）。
    三天为一岁，一天为四个月，一个时辰为十天。
    """
    from .core import TIAN_GAN_YY, JIE_QI
    from .lunar import get_jie_qi_date
    from datetime import date

    gan_yy = TIAN_GAN_YY.get(year_gan, 1)
    is_male = (gender == "male")
    forward = (gan_yy == 1 and is_male) or (gan_yy == 0 and not is_male)

    birth = date(year, month, day)

    # 节气列表：立春(2), 惊蛰(4), 清明(6), 立夏(8), 芒种(10), 小暑(12),
    #           立秋(14), 白露(16), 寒露(18), 立冬(20), 大雪(22), 小寒(0)
    jie_indices = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 0]

    if forward:
        # 找出生日之后最近的一个节
        for ji in jie_indices:
            jm, jd = get_jie_qi_date(year, ji)
            if ji == 0:  # 小寒在次年
                j_year = year + 1
            else:
                j_year = year
            jie_date = date(j_year, jm, jd)
            if jie_date > birth:
                break
        else:
            # 未找到，取次年立春
            jm, jd = get_jie_qi_date(year + 1, 2)
            jie_date = date(year + 1, jm, jd)
    else:
        # 找出生日之前最近的一个节
        jie_indices_rev = list(reversed(jie_indices))
        for ji in jie_indices_rev:
            jm, jd = get_jie_qi_date(year, ji)
            if ji == 0:
                j_year = year
            else:
                j_year = year
            jie_date = date(j_year, jm, jd)
            if jie_date < birth:
                break
            # 如果是立春且在上年
            if ji == 2:
                jm2, jd2 = get_jie_qi_date(year - 1, 2)
                jie_date = date(year - 1, jm2, jd2)
                if jie_date < birth:
                    break
        else:
            jm, jd = get_jie_qi_date(year - 1, 0)
            jie_date = date(year - 1, jm, jd)

    days_diff = abs((birth - jie_date).days)
    age = round(days_diff / 3, 1)
    return age


# ============================================================
# 大运吉凶评级
# ============================================================

def rate_da_yun(da_yun, day_wx, yong_shen_wx_list, ji_shen_wx_list):
    """对每个大运进行吉凶评级。"""
    from .core import TIAN_GAN_WX, DI_ZHI_WX
    WX_SHENG_WO = {"金": "土", "木": "水", "水": "金", "火": "木", "土": "火"}
    WX_KE_WO = {"金": "火", "木": "金", "水": "土", "火": "水", "土": "木"}

    rated = []
    for gz, age in da_yun:
        g, z = gz[0], gz[1]
        g_wx = TIAN_GAN_WX[g]
        z_wx = DI_ZHI_WX[z]

        # 提取用神忌神五行（去除括号内容）
        yong_wx = set()
        for ys in yong_shen_wx_list:
            wx = ys.split("(")[0] if "(" in ys else ys
            yong_wx.add(wx)
        ji_wx = set()
        for js in ji_shen_wx_list:
            wx = js.split("(")[0] if "(" in js else js
            ji_wx.add(wx)

        # 判断天干吉凶
        gan_score = 0
        zhi_score = 0

        if g_wx in yong_wx:
            gan_score = 2
            gan_label = "吉"
        elif g_wx in ji_wx:
            gan_score = -2
            gan_label = "凶"
        elif g_wx == day_wx:
            gan_score = 0 if day_wx in ji_wx else 1
            gan_label = "平" if day_wx in ji_wx else "小吉"
        elif WX_SHENG_WO.get(day_wx) == g_wx:
            gan_score = 0 if g_wx in ji_wx else 1
            gan_label = "平" if g_wx in ji_wx else "小吉"
        else:
            gan_label = "平"
            gan_score = 0

        if z_wx in yong_wx:
            zhi_score = 2
            zhi_label = "吉"
        elif z_wx in ji_wx:
            zhi_score = -2
            zhi_label = "凶"
        elif z_wx == day_wx:
            zhi_score = 0 if day_wx in ji_wx else 1
            zhi_label = "平" if day_wx in ji_wx else "小吉"
        else:
            zhi_label = "平"
            zhi_score = 0

        total = gan_score + zhi_score
        if total >= 3:
            overall = "大吉"
        elif total >= 1:
            overall = "吉"
        elif total >= 0:
            overall = "平"
        elif total >= -2:
            overall = "小凶"
        else:
            overall = "凶"

        rated.append({
            "gz": gz, "age": age,
            "gan": g, "zhi": z,
            "gan_wx": g_wx, "zhi_wx": z_wx,
            "gan_label": gan_label, "zhi_label": zhi_label,
            "overall": overall,
            "gan_comment": f"天干{g}({g_wx}){gan_label}", 
            "zhi_comment": f"地支{z}({z_wx}){zhi_label}",
        })
    return rated


# ============================================================
# 流年运势
# ============================================================

def compute_current_year_ganzhi(current_year=None):
    """计算当前年份的干支。"""
    from datetime import date
    if current_year is None:
        current_year = date.today().year
    year_idx = (current_year - 4) % 60
    from .core import JIA_ZI
    return JIA_ZI[year_idx]


def analyze_liu_nian(day_gan, day_wx, year_gan_zhi, yong_shen_list, ji_shen_list, da_yun_current=None):
    """分析流年运势。"""
    from .core import TIAN_GAN_WX, DI_ZHI_WX, TIAN_GAN_YY
    from .bazi import compute_shi_shen

    year_gan = year_gan_zhi[0]
    year_zhi = year_gan_zhi[1]
    year_gan_wx = TIAN_GAN_WX[year_gan]
    year_zhi_wx = DI_ZHI_WX[year_zhi]

    # 流年十神
    liu_nian_shi_shen = compute_shi_shen(day_gan, year_gan)

    # 用神忌神
    yong_wx = set()
    for ys in yong_shen_list:
        wx = ys.split("(")[0] if "(" in ys else ys
        yong_wx.add(wx)
    ji_wx = set()
    for js in ji_shen_list:
        wx = js.split("(")[0] if "(" in js else js
        ji_wx.add(wx)

    # 评级
    if year_gan_wx in yong_wx:
        rating = "吉"
        desc = f"流年{year_gan_zhi}天干{year_gan_wx}为用神，{liu_nian_shi_shen}运，运势上扬"
    elif year_gan_wx in ji_wx:
        rating = "凶"
        desc = f"流年{year_gan_zhi}天干{year_gan_wx}为忌神，{liu_nian_shi_shen}运，需谨慎行事"
    else:
        rating = "平"
        desc = f"流年{year_gan_zhi}，{liu_nian_shi_shen}运，运势平稳"

    # 生肖关系
    from .core import SHENG_XIAO, DI_ZHI
    year_sheng_xiao = SHENG_XIAO[DI_ZHI.index(year_zhi)]

    return {
        "year_gan_zhi": year_gan_zhi,
        "year_sheng_xiao": year_sheng_xiao,
        "shi_shen": liu_nian_shi_shen,
        "rating": rating,
        "description": desc,
        "year_gan": year_gan,
        "year_zhi": year_zhi,
        "year_gan_wx": year_gan_wx,
        "year_zhi_wx": year_zhi_wx,
    }


# ============================================================
# 命盘综合评分
# ============================================================

def compute_overall_score(strength_level, yong_shen, ji_shen, wu_xing, shen_sha, ge_ju):
    """计算命盘综合评分（满分100）。"""
    score = 50  # 基础分

    # 日主旺衰（0-15分）
    if strength_level == "中和":
        score += 15
    elif strength_level in ("偏旺", "偏弱"):
        score += 10
    elif strength_level == "旺":
        score += 5

    # 用神明确性（0-10分）
    if len(yong_shen) >= 2:
        score += 10
    elif len(yong_shen) == 1:
        score += 5

    # 五行平衡（0-15分，缺一行-5，过旺一行-3）
    missing = sum(1 for v in wu_xing.values() if v == 0)
    excessive = sum(1 for v in wu_xing.values() if v >= 3.5)
    score -= missing * 5
    score -= excessive * 3
    score = max(score, 30)

    # 神煞加分（0-10分）
    good_shen = {"天乙贵人": 5, "文昌": 3, "将星": 3, "华盖": 2}
    bad_shen = {"羊刃": -3}
    for name, zhi_list in shen_sha.items():
        if name in good_shen:
            score += good_shen[name]
        if name in bad_shen:
            score += bad_shen[name]
    score = min(score, 100)

    # 格局加分
    if ge_ju:
        score += min(len(ge_ju) * 2, 5)

    score = max(min(score, 100), 20)

    if score >= 85:
        level = "上等"
    elif score >= 70:
        level = "中上"
    elif score >= 55:
        level = "中等"
    elif score >= 40:
        level = "中下"
    else:
        level = "下等"

    return {"score": score, "level": level}

# ============================================================
# 刑冲合害分析
# ============================================================

# 天干五合
TIAN_GAN_HE = [('甲','己'), ('乙','庚'), ('丙','辛'), ('丁','壬'), ('戊','癸')]

# 地支六合
DI_ZHI_LIU_HE = [('子','丑'), ('寅','亥'), ('卯','戌'), ('辰','酉'), ('巳','申'), ('午','未')]

# 地支三合局
DI_ZHI_SAN_HE = [('申','子','辰'), ('亥','卯','未'), ('寅','午','戌'), ('巳','酉','丑')]

# 地支六冲
DI_ZHI_CHONG = [('子','午'), ('丑','未'), ('寅','申'), ('卯','酉'), ('辰','戌'), ('巳','亥')]

# 地支相刑
DI_ZHI_XING = [('寅','巳'), ('巳','申'), ('申','寅'), ('丑','戌'), ('戌','未'), ('未','丑'), ('子','卯')]

# 地支相害
DI_ZHI_HAI = [('子','未'), ('丑','午'), ('寅','巳'), ('卯','辰'), ('申','亥'), ('酉','戌')]

HE_NAMES = {
    ('甲','己'): '甲己合土', ('乙','庚'): '乙庚合金', ('丙','辛'): '丙辛合水',
    ('丁','壬'): '丁壬合木', ('戊','癸'): '戊癸合火',
}


def analyze_xing_chong_he(pillars, day_gan):
    """分析命局中的刑冲合害关系。"""
    result = {"he": [], "chong": [], "xing": [], "hai": [], "san_he": []}

    # 收集所有天干和地支
    gans = []
    zhis = []
    for label, gz in pillars:
        gans.append((label, gz[0]))
        zhis.append((label, gz[1]))

    # 天干五合
    for i in range(len(gans)):
        for j in range(i+1, len(gans)):
            for a, b in TIAN_GAN_HE:
                if (gans[i][1] == a and gans[j][1] == b) or (gans[i][1] == b and gans[j][1] == a):
                    name = HE_NAMES.get((a,b), f'{a}{b}合')
                    # Check if 化神在月令
                    result["he"].append(f"{gans[i][0]}干{gans[i][1]}{gans[j][0]}干{gans[j][1]}→{name}")

    # 地支六合
    for i in range(len(zhis)):
        for j in range(i+1, len(zhis)):
            for a, b in DI_ZHI_LIU_HE:
                if (zhis[i][1] == a and zhis[j][1] == b) or (zhis[i][1] == b and zhis[j][1] == a):
                    result["he"].append(f"{zhis[i][0]}支{zhis[i][1]}{zhis[j][0]}支{zhis[j][1]}→{zhis[i][1]}{zhis[j][1]}六合")

    # 地支三合
    zhi_only = [z[1] for z in zhis]
    for a, b, c in DI_ZHI_SAN_HE:
        if a in zhi_only and b in zhi_only:
            result["san_he"].append(f"半合{a}{b}局")
        if a in zhi_only and c in zhi_only:
            result["san_he"].append(f"半合{a}{c}局")
        if b in zhi_only and c in zhi_only:
            result["san_he"].append(f"半合{b}{c}局")
        if a in zhi_only and b in zhi_only and c in zhi_only:
            result["san_he"].append(f"三合{a}{b}{c}全")

    # 六冲
    for i in range(len(zhis)):
        for j in range(i+1, len(zhis)):
            for a, b in DI_ZHI_CHONG:
                if (zhis[i][1] == a and zhis[j][1] == b) or (zhis[i][1] == b and zhis[j][1] == a):
                    result["chong"].append(f"{zhis[i][0]}支{zhis[i][1]}↔{zhis[j][0]}支{zhis[j][1]}六冲")

    # 相刑
    for i in range(len(zhis)):
        for j in range(i+1, len(zhis)):
            for a, b in DI_ZHI_XING:
                if (zhis[i][1] == a and zhis[j][1] == b) or (zhis[i][1] == b and zhis[j][1] == a):
                    result["xing"].append(f"{zhis[i][0]}支{zhis[i][1]}☓{zhis[j][0]}支{zhis[j][1]}相刑")

    # 相害
    for i in range(len(zhis)):
        for j in range(i+1, len(zhis)):
            for a, b in DI_ZHI_HAI:
                if (zhis[i][1] == a and zhis[j][1] == b) or (zhis[i][1] == b and zhis[j][1] == a):
                    result["hai"].append(f"{zhis[i][0]}支{zhis[i][1]}⊘{zhis[j][0]}支{zhis[j][1]}相害")

    return result

# ============================================================
# 14. 纳音详解
# ============================================================
NA_YIN_DETAIL = {
    "海中金": {"wx": "金", "desc": "海中金是深藏海底之金，需火炼方成器。命带海中金者外表温和内心坚定，不轻易显露才华。", "advice": "宜借助贵人提携，厚积薄发"},
    "炉中火": {"wx": "火", "desc": "炉中火是熔炉之火，热情且具创造力。命带炉中火者精力充沛，适合技术型或创意型工作。", "advice": "收敛锋芒，避免三分钟热度"},
    "大林木": {"wx": "木", "desc": "大林木是参天大树之木，正直坚韧。命带大林木者心胸开阔，有领导才能和包容心。", "advice": "多培养团队协作能力"},
    "路旁土": {"wx": "土", "desc": "路旁土是承载万物之土，朴实无华。命带路旁土者踏实稳重，善解人意。", "advice": "寻找适合自己的舞台"},
    "剑锋金": {"wx": "金", "desc": "剑锋金是利剑之金，锋芒毕露。命带剑锋金者果断刚毅，执行力强，适合军警、法律、金融。", "advice": "刚柔并济，避免过于刚直"},
    "山头火": {"wx": "火", "desc": "山头火是山巅之火，光芒远射。命带山头火者有追求和抱负，适合公众型事业。", "advice": "高处不胜寒，注意人际关系"},
    "涧下水": {"wx": "水", "desc": "涧下水是山涧清泉之水，纯净灵动。命带涧下水者心思细腻，适合文职和艺术。", "advice": "以柔克刚，保持初心"},
    "城头土": {"wx": "土", "desc": "城头土是城墙之土，坚固可靠。命带城头土者守信用，适合稳定型工作。", "advice": "适当变通，不要过于固执"},
    "白蜡金": {"wx": "金", "desc": "白蜡金是饰品之金，精美雅致。命带白蜡金者追求完美，有艺术天赋。", "advice": "注重细节但别吹毛求疵"},
    "杨柳木": {"wx": "木", "desc": "杨柳木是柔韧之木，随风而动。命带杨柳木者适应力强，人缘好。", "advice": "坚守原则，避免随波逐流"},
    "泉中水": {"wx": "水", "desc": "泉中水是地下泉水之水，源源不断。命带泉中水者内涵深厚，适合学术研究。", "advice": "适当展现自己，不要过于低调"},
    "屋上土": {"wx": "土", "desc": "屋上土是屋瓦之土，庇护家人。命带屋上土者家庭观念强，责任心重。", "advice": "兼顾事业与家庭"},
    "霹雳火": {"wx": "火", "desc": "霹雳火是雷电之火，来势猛烈。命带霹雳火者爆发力强，适合竞技和创业。", "advice": "控制情绪，避免大起大落"},
    "松柏木": {"wx": "木", "desc": "松柏木是长青之木，四季不凋。命带松柏木者意志坚定，经得起考验。", "advice": "保持韧性，持之以恒"},
    "长流水": {"wx": "水", "desc": "长流水是江河之水，奔流不息。命带长流水者思维活跃，适合贸易和传媒。", "advice": "制定计划，避免东奔西跑"},
    "砂中金": {"wx": "金", "desc": "砂中金是沙中之金，需淘洗方显。命带砂中金者需经历磨练才能发光。", "advice": "坚持努力，总有出头之日"},
    "山下火": {"wx": "火", "desc": "山下火是山脚之火，温暖近人。命带山下火者亲和力强，适合服务行业。", "advice": "保持热情，发挥感染力"},
    "平地木": {"wx": "木", "desc": "平地木是平原之木，根基稳固。命带平地木者按部就班，适合公职和大型企业。", "advice": "稳中求进，步步为营"},
    "壁上土": {"wx": "土", "desc": "壁上土是墙壁之土，分隔内外。命带壁上土者有边界感，适合设计和规划。", "advice": "打开心扉，学会分享"},
    "金箔金": {"wx": "金", "desc": "金箔金是金箔之金，华丽装饰。命带金箔金者外表出众，适合艺术和设计。", "advice": "内外兼修，厚德载物"},
    "覆灯火": {"wx": "火", "desc": "覆灯火是灯烛之火，照亮黑暗。命带覆灯火者乐于助人，适合教育和公益。", "advice": "照顾自己的同时照亮别人"},
    "天河水": {"wx": "水", "desc": "天河水是天河之水，浩瀚无边。命带天河水者志向远大，适合科技和学术。", "advice": "脚踏实地，梦想需要努力"},
    "大驿土": {"wx": "土", "desc": "大驿土是驿道之土，交通四方。命带大驿土者见识广阔，适合物流和外交。", "advice": "沉下心来深耕一处"},
    "钗钏金": {"wx": "金", "desc": "钗钏金是首饰之金，精致华美。命带钗钏金者品味高雅，审美出众。", "advice": "华丽之外也重实用"},
    "桑柘木": {"wx": "木", "desc": "桑柘木是桑树之木，滋养蚕桑。命带桑柘木者有奉献精神，适合农业和纺织。", "advice": "提升自己的核心竞争力"},
    "大溪水": {"wx": "水", "desc": "大溪水是山溪之水，清澈见底。命带大溪水者心地纯净，适合医疗和护理。", "advice": "增强自我保护意识"},
    "沙中土": {"wx": "土", "desc": "沙中土是沙中之土，松散自由。命带沙中土者不拘一格，适合创意行业。", "advice": "建立稳定的基础结构"},
    "天上火": {"wx": "火", "desc": "天上火是太阳之火，普照万物。命带天上火者光明磊落，适合领导岗位。", "advice": "注意身体健康，劳逸结合"},
    "石榴木": {"wx": "木", "desc": "石榴木是果木之花，多子多福。命带石榴木者人丁兴旺，子女运好。", "advice": "培养下一代，传承家业"},
    "大海水": {"wx": "水", "desc": "大海水是汪洋之水，包容万象。命带大海水者气度不凡，适合国际贸易。", "advice": "有容乃大，但要专精一处"},
}

def analyze_na_yin_detail(na_yin):
    """纳音五行详解。"""
    results = {}
    for pillar, name in na_yin.items():
        detail = NA_YIN_DETAIL.get(name, {"wx": "?", "desc": "暂无详细资料", "advice": ""})
        results[pillar] = {
            "name": name,
            "wx": detail["wx"],
            "description": detail["desc"],
            "advice": detail["advice"],
        }
    return results


# ============================================================
# 15. 日柱论命（60甲子日柱详解）
# ============================================================
RI_ZHU_INTERPRETATION = {
    "甲子": "甲子日生人，天干甲木坐子水正印。聪明好学，有领导才能，早年多得长辈帮扶。婚姻宜晚，配偶温和。",
    "乙丑": "乙丑日生人，天干乙木坐丑土偏财。务实稳重，理财能力强。性格坚韧，但有时固执。",
    "丙寅": "丙寅日生人，天干丙火坐寅木偏印。热情开朗，思维敏捷，有创造力。适合文化教育行业。",
    "丁卯": "丁卯日生人，天干丁火坐卯木偏印。外柔内刚，有艺术天赋。人缘好，桃花旺。",
    "戊辰": "戊辰日生人，天干戊土坐辰土比肩。沉稳厚重，诚信可靠。财运稳定，宜置不动产。",
    "己巳": "己巳日生人，天干己土坐巳火正印。温文尔雅，善解人意。有福气，贵人运好。",
    "庚午": "庚午日生人，天干庚金坐午火正官。刚毅果断，事业心强。适合军警、管理、金融行业。",
    "辛未": "辛未日生人，天干辛金坐未土偏印。心思缜密，追求完美。有艺术品味，适合珠宝、设计。",
    "壬申": "壬申日生人，天干壬水坐申金偏印。聪明灵活，适应力强。适合贸易、传媒、外交。",
    "癸酉": "癸酉日生人，天干癸水坐酉金偏印。细腻敏感，直觉准确。有神秘气质，适合心理学和玄学。",
    "甲戌": "甲戌日生人，天干甲木坐戌土偏财。务实进取，有商业头脑。财富积累能力强。",
    "乙亥": "乙亥日生人，天干乙木坐亥水正印。温柔善良，内心纯净。有才艺天赋，适合文艺工作。",
    "丙子": "丙子日生人，天干丙火坐子水正官。外热内冷，事业心强。有能力但需注意人际关系。",
    "丁丑": "丁丑日生人，天干丁火坐丑土食神。性格温和，有口福。适合餐饮、服务行业。",
    "戊寅": "戊寅日生人，天干戊土坐寅木七杀。有魄力，敢作敢为。适合创业和开拓型工作。",
    "己卯": "己卯日生人，天干己土坐卯木七杀。外柔内刚，思虑周全。适合幕后策划工作。",
    "庚辰": "庚辰日生人，天干庚金坐辰土偏印。稳重有智，善于规划。财运不错，宜投资理财。",
    "辛巳": "辛巳日生人，天干辛金坐巳火正官。自律严谨，追求卓越。适合技术和管理。",
    "壬午": "壬午日生人，天干壬水坐午火正财。财运亨通，性格豪爽。适合贸易和投资。",
    "癸未": "癸未日生人，天干癸水坐未土七杀。心思细腻但内心强大。适合研究和学术。",
    "甲申": "甲申日生人，天干甲木坐申金七杀。能力出众，应对挑战。适合竞争性行业。",
    "乙酉": "乙酉日生人，天干乙木坐酉金七杀。精细认真，有专业特长。适合技术和手工艺。",
    "丙戌": "丙戌日生人，天干丙火坐戌土食神。乐观大方，喜爱自由。适合创意和娱乐行业。",
    "丁亥": "丁亥日生人，天干丁火坐亥水正官。温和有礼，有责任心。适合公职和大型企业。",
    "戊子": "戊子日生人，天干戊土坐子水正财。财富稳定，性格稳重。适合金融和地产。",
    "己丑": "己丑日生人，天干己土坐丑土比肩。诚信厚道，团队意识强。适合工薪阶层稳定发展。",
    "庚寅": "庚寅日生人，天干庚金坐寅木偏财。商业头脑好，财运颇佳。适合经商和投资。",
    "辛卯": "辛卯日生人，天干辛金坐卯木偏财。眼光独到，审美好。适合珠宝、艺术品行业。",
    "壬辰": "壬辰日生人，天干壬水坐辰土七杀。心胸开阔，有能力。适合管理和领导岗位。",
    "癸巳": "癸巳日生人，天干癸水坐巳火正财。财运良好，性格温和。家庭生活美满。",
    "甲午": "甲午日生人，天干甲木坐午火伤官。聪明有才，个性突出。适合创意和技术行业。",
    "乙未": "乙未日生人，天干乙木坐未土偏财。稳重务实，理财能力强。宜从事会计和金融。",
    "丙申": "丙申日生人，天干丙火坐申金偏财。精力旺盛，财运不错。适合销售和市场。",
    "丁酉": "丁酉日生人，天干丁火坐酉金偏财。优雅有品味，财运亨通。适合时尚和奢侈品行业。",
    "戊戌": "戊戌日生人，天干戊土坐戌土比肩。坚定有主见，不轻易动摇。适合独立创业。",
    "己亥": "己亥日生人，天干己土坐亥水正财。温和务实，财富稳定。宜从事教育和护理。",
    "庚子": "庚子日生人，天干庚金坐子水伤官。聪明锐利，有创新思维。适合科技和研发。",
    "辛丑": "辛丑日生人，天干辛金坐丑土偏印。内敛有才，适合需要精细操作的工作。",
    "壬寅": "壬寅日生人，天干壬水坐寅木食神。思维活跃，有创造力。适合传媒和写作。",
    "癸卯": "癸卯日生人，天干癸水坐卯木食神。温柔有才，适合艺术和教育行业。",
    "甲辰": "甲辰日生人，天干甲木坐辰土偏财。务实能干，财运不错。宜从事实业。",
    "乙巳": "乙巳日生人，天干乙木坐巳火伤官。有才艺，思维灵敏。适合设计和创意行业。",
    "丙午": "丙午日生人，天干丙火坐午火劫财。精力充沛，热情似火。适合演艺和体育。",
    "丁未": "丁未日生人，天干丁火坐未土食神。温和乐观，喜爱美食。适合餐饮和服务行业。",
    "戊申": "戊申日生人，天干戊土坐申金食神。稳重有智，能够积累财富。宜投资和地产。",
    "己酉": "己酉日生人，天干己土坐酉金食神。温和内秀，有专业特长。适合技术和手工艺。",
    "庚戌": "庚戌日生人，天干庚金坐戌土偏印。刚毅有谋，能成大事。适合工程和建筑。",
    "辛亥": "辛亥日生人，天干辛金坐亥水伤官。聪明灵巧，有创新精神。适合科技和发明。",
    "壬子": "壬子日生人，天干壬水坐子水劫财。聪明但较自我，有领导潜质。适合自由职业。",
    "癸丑": "癸丑日生人，天干癸水坐丑土七杀。内心坚强，能够承受压力。适合需要耐力的工作。",
    "甲寅": "甲寅日生人，天干甲木坐寅木比肩。独立自主，有开拓精神。适合创业和领导。",
    "乙卯": "乙卯日生人，天干乙木坐卯木比肩。温柔但有自己的坚持。适合文艺创作。",
    "丙辰": "丙辰日生人，天干丙火坐辰土食神。开朗大方，有领导魅力。适合管理和公关。",
    "丁巳": "丁巳日生人，天干丁火坐巳火劫财。热情积极，适合销售和市场开拓。",
    "戊午": "戊午日生人，天干戊土坐午火正印。稳重有智慧，适合学术和教育。",
    "己未": "己未日生人，天干己土坐未土比肩。诚信可靠，团队合作能力强。",
    "庚申": "庚申日生人，天干庚金坐申金比肩。刚毅果断，独立自主。适合军警和武术。",
    "辛酉": "辛酉日生人，天干辛金坐酉金比肩。精致追求完美，适合珠宝和精密制造。",
    "壬戌": "壬戌日生人，天干壬水坐戌土七杀。胸怀大志，能承担重任。适合高层管理。",
    "癸亥": "癸亥日生人，天干癸水坐亥水劫财。聪明机灵，但需注意人际关系。适合自由职业。",
}

def analyze_ri_zhu(day_gan_zhi):
    """日柱论命解读。"""
    return RI_ZHU_INTERPRETATION.get(day_gan_zhi, "日柱暂无详细解读，请参考十神和五行综合分析。")


# ============================================================
# 16. 神煞详解
# ============================================================
SHEN_SHA_DETAIL = {
    "天乙贵人": {
        "symbol": "✨", "level": "大吉", "color": "#FFC107",
        "desc": "天乙贵人是命中最吉之神，遇之主智慧聪明，出入近贵，逢凶化吉。",
        "impact": "贵人相助，事业顺遂。在关键时刻总有人出手相助。",
    },
    "文昌": {
        "symbol": "📖", "level": "吉", "color": "#00E5FF",
        "desc": "文昌星主文运、科甲、学业。命带文昌者聪明好学，有文采。",
        "impact": "学业运佳，适合从事学术、写作、教育等文职工作。",
    },
    "桃花": {
        "symbol": "🌸", "level": "中性", "color": "#FF6B9D",
        "desc": "桃花星主人缘、异性缘、魅力。命带桃花者人缘好，有吸引力。",
        "impact": "异性缘佳，社交能力强。但需注意节制，避免感情纠葛。",
    },
    "驿马": {
        "symbol": "🐎", "level": "中性", "color": "#FFB000",
        "desc": "驿马星主走动、变动、奔波。命带驿马者好动不喜静。",
        "impact": "适合外勤、出差、交通物流行业。但需注意奔波劳累。",
    },
    "华盖": {
        "symbol": "🏛️", "level": "中性", "color": "#00FF41",
        "desc": "华盖星主孤独、艺术、宗教缘分。命带华盖者有独特气质。",
        "impact": "有艺术天赋和宗教缘分。性格可能偏内向，但才华内蕴。",
    },
    "羊刃": {
        "symbol": "⚔️", "level": "凶", "color": "#FF3131",
        "desc": "羊刃星主刚强、固执、竞争。命带羊刃者性格刚烈。",
        "impact": "做事果断有魄力，但容易冲动。适合军警、外科医生等需要胆量的职业。",
    },
    "将星": {
        "symbol": "⭐", "level": "吉", "color": "#FFC107",
        "desc": "将星主领导才能、统御能力。命带将星者有大将之风。",
        "impact": "有领导才能和统御力，适合管理和指挥岗位。",
    },
}

def analyze_shen_sha_detail(shen_sha):
    """神煞详解分析。"""
    results = {}
    for name, zhis in (shen_sha or {}).items():
        detail = SHEN_SHA_DETAIL.get(name, {})
        if detail:
            results[name] = {
                "symbol": detail.get("symbol", ""),
                "level": detail.get("level", ""),
                "color": detail.get("color", "#6a6a7a"),
                "description": detail.get("desc", ""),
                "impact": detail.get("impact", ""),
                "appears_in": zhis,
            }
    return results


# ============================================================
# 17. 四柱逐柱详解
# ============================================================

# 各柱代表的人生领域
PILLAR_MEANING = {
    "年": {
        "name": "年柱", "age": "0-16岁",
        "domain": "祖上根基、童年运势、家庭背景",
        "gan_key": "祖上/远祖", "zhi_key": "早年环境",
        "icon": "🏛️", "color": "#FFC107",
    },
    "月": {
        "name": "月柱", "age": "17-32岁",
        "domain": "父母兄弟、少年运势、事业根基",
        "gan_key": "父母/上司", "zhi_key": "月令提纲",
        "icon": "🌙", "color": "#00E5FF",
    },
    "日": {
        "name": "日柱", "age": "33-48岁",
        "domain": "自身配偶、中年运势、婚姻家庭",
        "gan_key": "自身/日主", "zhi_key": "配偶宫",
        "icon": "☀️", "color": "#FF3131",
    },
    "时": {
        "name": "时柱", "age": "49岁以后",
        "domain": "子女晚运、晚年归宿、下属晚辈",
        "gan_key": "子女/下属", "zhi_key": "晚年归宿",
        "icon": "🌅", "color": "#FFB000",
    },
}

# 十神在各柱的独特含义
SHI_SHEN_PILLAR_MEANING = {
    "年": {
        "正官": "祖上可能有官宦背景，家世清白。幼年受传统教育，规矩多。",
        "七杀": "祖上可能有武职或军警背景。幼年生活压力大，早熟独立。",
        "正印": "祖上书香门第，重视教育。童年多得长辈疼爱和庇护。",
        "偏印": "祖上有特殊技艺传承。童年环境独特，可能由非父母抚养。",
        "正财": "祖上经商或务农，家境殷实。幼年物质生活有保障。",
        "偏财": "祖上财富来路多样，家境宽裕。幼年生活环境宽松自由。",
        "食神": "祖上安逸富足，家庭氛围温馨。童年快乐无拘束。",
        "伤官": "祖上有才艺之人。幼年聪明但可能不服管教。",
        "比肩": "祖上人丁兴旺，兄弟姐妹多。幼年与同辈互动频繁。",
        "劫财": "祖上慷慨好义，人来人往。幼年环境热闹多变。",
    },
    "月": {
        "正官": "父母管教严格，少年自律上进。事业初期的贵人多为上司。",
        "七杀": "少年时期面临竞争压力，锻炼出坚韧性格。兄弟中有强势者。",
        "正印": "母亲贤惠慈爱，在关键时期能得到长辈提携。学业运好。",
        "偏印": "与母亲缘分特殊。少年时期有独特技能或兴趣养成。",
        "正财": "父母理财有道，少年时期懂得珍惜财物。事业早期收入稳定。",
        "偏财": "父亲善于经营，少年见识广。事业早期机会多，偏财运佳。",
        "食神": "少年生活安逸，家庭氛围轻松。与兄弟姐妹关系融洽。",
        "伤官": "少年聪明但叛逆，有独立思想。与长辈可能意见不合。",
        "比肩": "兄弟姐妹多，竞争激烈。独立性强，事业靠自身打拼。",
        "劫财": "朋友圈广但消耗也多。少年时期花费大，需注意理财。",
    },
    "日": {
        "正官": "自身正直有原则，配偶有责任感。婚姻稳定但缺少浪漫。",
        "七杀": "自身果敢有魄力，配偶个性强势。婚姻有激情但时有摩擦。",
        "正印": "自身善良有智慧，配偶体贴照顾型。婚姻温馨有归属感。",
        "偏印": "自身思维独特，配偶可能有特殊才能。婚姻需精神契合。",
        "正财": "自身重视物质基础，配偶有理财能力。婚姻务实稳定。",
        "偏财": "自身慷慨大方，异性缘好。需注意区分正缘和偏缘。",
        "食神": "自身温和乐观，配偶性格好。婚姻生活和谐愉快。",
        "伤官": "自身才华横溢但有锋芒。女性需注意婚姻中的表达方式。",
        "比肩": "自身独立自强，配偶性格独立。婚姻需互相尊重个人空间。",
        "劫财": "自身社交能力强，重视朋友。需注意婚姻中第三方的干扰。",
    },
    "时": {
        "正官": "子女有责任感，教育得当。晚年生活中规中矩，有秩序。",
        "七杀": "子女独立有冲劲。晚年可能为子女操心较多，但后继有人。",
        "正印": "子女孝顺体贴，晚年有人照料。精神生活充实。",
        "偏印": "子女有独特才能或天赋。晚年可享受子女带来的独特成就。",
        "正财": "子女理财能力强。晚年物质生活无忧，经济独立。",
        "偏财": "子女事业心强，赚钱能力强。晚年可享受子女的经济支持。",
        "食神": "子女性格好，相处愉快。晚年含饴弄孙，生活安逸。",
        "伤官": "子女聪明有才但个性强。晚年需要尊重子女的独立选择。",
        "比肩": "子女独立志气高。晚年与子女像朋友般相处。",
        "劫财": "子女社交广、朋友多。晚年家庭热闹，但花费也多。",
    },
}

# 十二长生在各柱的含义
CHANG_SHENG_PILLAR_MEANING = {
    "长生": "此柱处于长生之地，代表此阶段充满生机与活力，是一切开始的良好时机。",
    "沐浴": "此柱处于沐浴之地，代表此阶段有桃花运和人际交往机会，但也需注意情感波动。",
    "冠带": "此柱处于冠带之地，代表此阶段步入成熟，开始承担更多责任。",
    "临官": "此柱处于临官之地，代表此阶段事业有成，处于上升期，运势旺盛。",
    "帝旺": "此柱处于帝旺之地，代表此阶段运势达到顶峰，是最辉煌的时期。但物极必反，需防盛极而衰。",
    "衰": "此柱处于衰地，代表此阶段由盛转衰，需调整心态，放慢节奏。",
    "病": "此柱处于病地，代表此阶段运势疲软，需注意身体健康，不宜冒进。",
    "死": "此柱处于死地，代表此阶段运势低迷，宜守不宜攻，韬光养晦。",
    "墓": "此柱处于墓地，代表此阶段运势内敛，适合蓄力和积累，不宜大展拳脚。",
    "绝": "此柱处于绝地，代表此阶段运势触底，但绝处逢生，是重新开始的契机。",
    "胎": "此柱处于胎地，代表此阶段是新周期的孕育期，宜筹划未来，积蓄力量。",
    "养": "此柱处于养地，代表此阶段运势逐渐回暖，是稳步上升的时期。",
}

# 地支在各柱的独特含义
ZHI_PILLAR_MEANING = {
    "子": {"年":"祖居近水或北方，早年环境湿润","月":"少年时期灵活多变，适应力强","日":"配偶聪慧灵动，婚姻需防第三者","时":"晚年思维活跃，子女聪明"},
    "丑": {"年":"祖上务农或经商，根基深厚","月":"少年踏实稳重，学业按部就班","日":"配偶务实可靠，婚姻稳定传统","时":"晚年积蓄丰厚，子女稳重"},
    "寅": {"年":"祖上有开创精神，家族有变革","月":"少年有魄力，早立志向","日":"配偶有事业心，婚姻有活力","时":"晚年仍有作为，子女能干"},
    "卯": {"年":"祖上文雅，家中有文化底蕴","月":"少年温和善良，人际关系好","日":"配偶温柔，婚姻和谐但防轻浮","时":"晚年清闲，子女性格好"},
    "辰": {"年":"祖居近山或高地，家族厚重","月":"少年稳重自信，学业扎实","日":"配偶有主见，婚姻需互相尊重","时":"晚运安康，子女有地位"},
    "巳": {"年":"祖上可能有技艺传承","月":"少年聪明好动，多才多艺","日":"配偶热情主动，婚姻有激情","时":"晚年精神矍铄，子女出众"},
    "午": {"年":"祖上光明磊落，家族有地位","月":"少年热情开朗，人缘好","日":"配偶大方热情，婚姻需防过度","时":"晚年生活丰富多彩"},
    "未": {"年":"祖上重视文化和礼仪","月":"少年温和有礼，环境稳定","日":"配偶顾家温柔，婚姻温馨","时":"晚年安逸平和"},
    "申": {"年":"祖上有变革精神，或出远门","月":"少年思维灵活，有创意","日":"配偶能干果断，婚姻需沟通","时":"晚年有所创新和突破"},
    "酉": {"年":"祖上精致讲排场，或从事金融","月":"少年精致有品位，注意细节","日":"配偶相貌端正，婚姻讲究仪式","时":"晚年精致讲究"},
    "戌": {"年":"祖上忠义，可能有军旅背景","月":"少年有正义感，意志坚定","日":"配偶可靠忠诚，婚姻稳固","时":"晚年受人尊敬"},
    "亥": {"年":"祖居近水，家族有包容心","月":"少年有想象力，思维开阔","日":"配偶浪漫有情趣，婚姻有新鲜感","时":"晚年悠闲自在"},
}


def analyze_pillars_detail(bazi, bazi_analysis):
    """对年月日时四柱逐一进行深度解析。"""
    from .core import TIAN_GAN_WX, DI_ZHI_WX, DI_ZHI_CANG_GAN

    strength = bazi_analysis.get("strength", {})
    day_wx = bazi.day_wx

    pillar_names = ["年", "月", "日", "时"]
    gans = [bazi.year_gan, bazi.month_gan, bazi.day_gan, bazi.hour_gan]
    zhis = [bazi.year_zhi, bazi.month_zhi, bazi.day_zhi, bazi.hour_zhi]
    ganzhis = [bazi.year_gan_zhi, bazi.month_gan_zhi, bazi.day_gan_zhi, bazi.hour_gan_zhi]
    shi_shens = [bazi.shi_shen.get("年", ""), bazi.shi_shen.get("月", ""), bazi.shi_shen.get("日", ""), bazi.shi_shen.get("时", "")]
    chang_shengs = [bazi.chang_sheng.get("年", ""), bazi.chang_sheng.get("月", ""), bazi.chang_sheng.get("日", ""), bazi.chang_sheng.get("时", "")]
    nayins = [bazi.na_yin.get("年", ""), bazi.na_yin.get("月", ""), bazi.na_yin.get("日", ""), bazi.na_yin.get("时", "")]
    di_zhi_shi_shens = [bazi.di_zhi_shi_shen.get("年", []), bazi.di_zhi_shi_shen.get("月", []), bazi.di_zhi_shi_shen.get("日", []), bazi.di_zhi_shi_shen.get("时", [])]

    results = {}

    for i, pname in enumerate(pillar_names):
        gan = gans[i]
        zhi = zhis[i]
        ganzhi = ganzhis[i]
        shi_shen = shi_shens[i] if i != 2 else "日主"  # 日柱十神是日主自身
        cs = chang_shengs[i]
        nayin = nayins[i]
        dz_ss = di_zhi_shi_shens[i]
        cang_gan = DI_ZHI_CANG_GAN.get(zhi, [])
        shen_shas = bazi.pillar_shen_sha.get(pname, [])

        # 基本信息
        p_info = PILLAR_MEANING.get(pname, {})
        gan_wx = TIAN_GAN_WX[gan]
        zhi_wx = DI_ZHI_WX[zhi]

        # 构建解读
        interpretations = []

        # 1. 柱位含义
        interpretations.append(f"此柱代表{p_info.get('domain', '')}，对应{p_info.get('age', '')}阶段。")

        # 2. 天干解读
        gan_meaning = _interpret_gan_in_pillar(gan, gan_wx, pname, day_wx)
        if gan_meaning:
            interpretations.append(f"【天干{gan}】{gan_meaning}")

        # 3. 地支解读
        zhi_meaning = _interpret_zhi_in_pillar(zhi, zhi_wx, pname, day_wx)
        if zhi_meaning:
            interpretations.append(f"【地支{zhi}】{zhi_meaning}")

        # 4. 干支组合解读
        combo = _interpret_ganzhi_combo(gan, zhi, gan_wx, zhi_wx, pname)
        if combo:
            interpretations.append(f"【干支配合】{combo}")

        # 5. 十神解读
        if pname != "日":
            ss_meaning = SHI_SHEN_PILLAR_MEANING.get(pname, {}).get(shi_shen, "")
            if ss_meaning:
                interpretations.append(f"【{shi_shen}在此柱】{ss_meaning}")

        # 6. 地支十神（藏干对应的十神）
        if dz_ss and cang_gan:
            dz_items = []
            for j, (cg, dss) in enumerate(zip(cang_gan, dz_ss)):
                cg_wx = TIAN_GAN_WX.get(cg, "?")
                dz_items.append(f"藏{cg}({cg_wx})为{dss}")
            if dz_items:
                interpretations.append(f"【地支藏干】{'，'.join(dz_items)}")

        # 7. 十二长生状态
        cs_meaning = CHANG_SHENG_PILLAR_MEANING.get(cs, "")
        if cs_meaning:
            interpretations.append(f"【长生状态·{cs}】{cs_meaning}")

        # 8. 神煞
        if shen_shas:
            ss_names = "、".join(shen_shas)
            ss_meaning = _interpret_shensha_on_pillar(shen_shas, pname)
            interpretations.append(f"【神煞】此柱带{ss_names}。{ss_meaning}")

        # 9. 纳音性情
        nayin_meaning = _interpret_nayin_on_pillar(nayin, pname)
        if nayin_meaning:
            interpretations.append(f"【纳音】{nayin}，{nayin_meaning}")

        # 10. 日柱特有分析
        if pname == "日":
            ri_extra = _analyze_day_pillar_special(gan, zhi, gan_wx, zhi_wx, day_wx, strength, bazi.gender)
            if ri_extra:
                interpretations.append(ri_extra)

        results[pname] = {
            "ganzhi": ganzhi,
            "gan": gan,
            "zhi": zhi,
            "gan_wx": gan_wx,
            "zhi_wx": zhi_wx,
            "shi_shen": shi_shen,
            "nayin": nayin,
            "chang_sheng": cs,
            "shen_shas": shen_shas,
            "cang_gan": cang_gan,
            "di_zhi_shi_shen": dz_ss,
            "interpretations": interpretations,
            "icon": p_info.get("icon", ""),
            "color": p_info.get("color", "#fff"),
            "age_range": p_info.get("age", ""),
            "domain": p_info.get("domain", ""),
        }

    return results


def _interpret_gan_in_pillar(gan, gan_wx, pillar, day_wx):
    """解读天干在某柱的含义。"""
    # 天干个性
    gan_personality = {
        "甲": "甲木参天，正直仁德，有领导力和进取心。",
        "乙": "乙木柔韧，温和细腻，适应力强。",
        "丙": "丙火热烈，光明磊落，热情有感染力。",
        "丁": "丁火柔中，外柔内刚，心思缜密。",
        "戊": "戊土厚重，诚信可靠，稳重有担当。",
        "己": "己土田园，温和包容，善于培育滋养。",
        "庚": "庚金刚健，果断刚毅，执行力强。",
        "辛": "辛金精致，追求完美，有艺术品味。",
        "壬": "壬水浩荡，智慧豁达，思维开阔。",
        "癸": "癸水至柔，细腻敏锐，直觉准确。",
    }

    # 天干与日主的关系
    rel = ""
    if gan_wx == day_wx:
        rel = "与日主同气，代表此柱与自身关系紧密，影响直接。"
    else:
        from .core import WX_RELATION
        relation = WX_RELATION.get((day_wx, gan_wx), "")
        if "生我" in str(relation):
            rel = "为日主之印星，代表此柱有滋养助力之象。"
        elif "我生" in str(relation):
            rel = "为日主之食伤，代表此柱有消耗但亦有才华展现。"
        elif "克我" in str(relation):
            rel = "为日主之官杀，代表此柱有约束责任之象。"
        elif "我克" in str(relation):
            rel = "为日主之财星，代表此柱有财富利益之象。"

    return gan_personality.get(gan, "") + rel


def _interpret_zhi_in_pillar(zhi, zhi_wx, pillar, day_wx):
    """解读地支在某柱的含义。"""
    zhi_info = ZHI_PILLAR_MEANING.get(zhi, {})
    base = zhi_info.get(pillar, "")

    # 地支生克关系补充
    from .core import WX_RELATION
    rel = WX_RELATION.get((day_wx, zhi_wx), "")

    return base


def _interpret_ganzhi_combo(gan, zhi, gan_wx, zhi_wx, pillar):
    """解读干支组合在某柱的含义。"""
    # 干支五行关系
    combos = []
    
    # 天干坐支的关系
    if gan_wx == zhi_wx:
        combos.append("天干与地支同类，此柱力量集中。")
    elif [gan_wx, zhi_wx] in [["木","水"],["火","木"],["土","火"],["金","土"],["水","金"]]:
        combos.append("地支生天干，此柱根气充足，天干得力。")
    elif [gan_wx, zhi_wx] in [["水","木"],["木","火"],["火","土"],["土","金"],["金","水"]]:
        combos.append("天干生地支，此柱精神外泄，地支得养。")

    # 特殊干支组合
    special_combos = {
        "甲寅": "甲木坐寅为临官禄地，根基极稳。",
        "乙卯": "乙木坐卯为临官禄地，根基稳固。",
        "丙午": "丙火坐午为帝旺羊刃，力量极强但需防过刚。",
        "丁巳": "丁火坐巳为帝旺，力量充沛。",
        "戊辰": "戊土坐辰为冠带，内藏乙木癸水，土得滋养。",
        "己未": "己土坐未为冠带，土气厚重。",
        "庚申": "庚金坐申为临官禄地，金气刚健。",
        "辛酉": "辛金坐酉为临官禄地，金气纯粹。",
        "壬子": "壬水坐子为帝旺羊刃，水势浩荡但需防过激。",
        "癸亥": "癸水坐亥为帝旺，水气充沛。",
    }
    special = special_combos.get(gan+zhi, "")
    if special:
        combos.append(special)

    return " ".join(combos) if combos else None


def _interpret_shensha_on_pillar(shen_shas, pillar):
    """解读神煞在特定柱位的含义。"""
    meanings = []
    for ss in shen_shas:
        pillar_ss = {
            "天乙贵人": {"年":"祖上有贵人庇护","月":"少年得贵人相助","日":"中年贵人运旺","时":"晚年有贵人照应"},
            "文昌": {"年":"幼年学业顺利","月":"少年科甲有望","日":"中年学术有成","时":"晚年仍有学习机缘"},
            "桃花": {"年":"幼年讨人喜欢","月":"少年异性缘好","日":"中年桃花运旺","时":"晚年仍有魅力"},
            "驿马": {"年":"早年搬迁多动","月":"少年多外出求学","日":"中年奔波劳碌","时":"晚年好动旅游"},
            "华盖": {"年":"幼年孤僻有天赋","月":"少年特立独行","日":"中年有独特才华","时":"晚年有修行机缘"},
            "羊刃": {"年":"幼年好强不服输","月":"少年锐气十足","日":"中年刚烈有魄力","时":"晚年仍精力旺盛"},
            "将星": {"年":"幼年有领导气质","月":"少年便有统御力","日":"中年适合管理岗位","时":"晚年仍有威望"},
        }
        m = pillar_ss.get(ss, {}).get(pillar, f"此柱有{ss}，为吉兆。")
        meanings.append(m)
    return "；".join(meanings)


def _interpret_nayin_on_pillar(nayin, pillar):
    """解读纳音在特定柱位的含义。"""
    from .bazi_analysis import NA_YIN_DETAIL
    detail = NA_YIN_DETAIL.get(nayin, {})
    desc = detail.get("description", "")
    if desc:
        # Truncate and adapt for pillar context
        if len(desc) > 60:
            desc = desc[:60] + "..."
        return desc
    return None


def _analyze_day_pillar_special(gan, zhi, gan_wx, zhi_wx, day_wx, strength, gender):
    """日柱特有深度分析。"""
    parts = []

    # 日坐（配偶宫）深度分析
    spouse_analysis = _analyze_spouse_palace(zhi, zhi_wx, day_wx, gender)
    if spouse_analysis:
        parts.append(spouse_analysis)

    # 日主旺衰提示
    level = strength.get("level", "中和")
    level_tips = {
        "旺": "日主旺相，精力充沛，适合主动出击、开拓事业。但需注意刚则易折，需官杀或食伤来平衡。",
        "偏旺": "日主偏旺，有能力有干劲，宜以财官为用。注意自我约束和情绪管理。",
        "中和": "日主中和，五行均衡，是难得的好命格。能屈能伸，适应力强。",
        "偏弱": "日主偏弱，宜借助外力，择良师益友同行。走帮扶运时大有可为。",
        "弱": "日主较弱，需寻强有力的印星或比劫为依托。宜韬光养晦，厚积薄发。",
    }
    tip = level_tips.get(level, "")
    if tip:
        parts.append(f"【日主{level}】{tip}")

    return " ".join(parts)


def _analyze_spouse_palace(zhi, zhi_wx, day_wx, gender):
    """分析配偶宫（日支）。"""
    from .core import WX_RELATION
    rel = WX_RELATION.get((day_wx, zhi_wx), "")

    base = ""

    if "同我" in str(rel):
        base = "日坐比劫，配偶与你性格相似，独立自强。婚姻中需互相尊重对方的空间和事业。"
    elif "生我" in str(rel):
        base = "日坐印星，配偶体贴照顾，有母性/父性光辉。婚姻温馨稳定，得配偶滋养。"
    elif "我生" in str(rel):
        base = "日坐食伤，配偶有才华和情趣，但需注意沟通方式。婚姻中充满创意和新鲜感。"
    elif "克我" in str(rel):
        base = "日坐官星，配偶有责任心和原则性。婚姻有秩序，但约束感较强。"
        if gender == "female":
            base += " 女命日坐官星为得位，丈夫有事业心，是良缘配置。"
        else:
            base += " 男命日坐官星，配偶能力出众，事业上有助益。"
    elif "我克" in str(rel):
        base = "日坐财星，配偶有理财能力，重视物质基础。婚姻务实稳定。"
        if gender == "male":
            base += " 男命日坐财星为得位，妻子贤惠持家，是经典良配。"
        else:
            base += " 女命日坐财星，配偶慷慨大方，经济条件不错。"

    # 地支特殊性
    special_zhi = {
        "子": " 子为桃花之地，配偶有魅力，但需注意感情中的第三方干扰。",
        "午": " 午为桃花之地且为羊刃，配偶热情但有个性，婚姻激情与挑战并存。",
        "卯": " 卯为桃花之地，配偶相貌清秀，人缘好。",
        "酉": " 酉为桃花之地，配偶精致有品位，容貌端正。",
    }
    base += special_zhi.get(zhi, "")

    return f"【配偶宫·{zhi}】{base}"


def format_pillars_detail(analysis):
    """格式化为可读文本。"""
    lines = []
    lines.append("")
    lines.append("=" * 50)
    lines.append("                    四柱逐柱详解")
    lines.append("=" * 50)

    for pname in ["年", "月", "日", "时"]:
        p = analysis.get(pname, {})
        if not p:
            continue
        lines.append("\n" + "─" * 40)
        lines.append(f"  【{pname}柱】{p['ganzhi']}  {p.get('age_range','')}")
        lines.append(f"  十神：{p.get('shi_shen','')}  纳音：{p.get('nayin','')}  长生：{p.get('chang_sheng','')}")
        lines.append(f"  神煞：{'、'.join(p.get('shen_shas',[])) or '无'}")
        lines.append(f"  解读：")
        for interp in p.get("interpretations", []):
            lines.append(f"    {interp}")

    return "\n".join(lines)

def format_bazi_analysis(analysis):
    """将分析结果格式化为可读文本。"""
    lines = []
    lines.append("")
    lines.append("=" * 50)
    lines.append("                    八字命理分析")
    lines.append("=" * 50)

    # 日主旺衰
    s = analysis["strength"]
    lines.append(f"\n【日主旺衰】{s['level']}")
    for r in s["reasons"]:
        lines.append(f"  · {r}")

    # 格局
    lines.append(f"\n【格局】{'、'.join(analysis['ge_ju']) if analysis['ge_ju'] else '暂无特殊格局'}")

    # === 喜用神深度解读 ===
    xi_yong = analysis.get("xi_yong_shen", {})
    if xi_yong and xi_yong.get("first_yong_shen"):
        lines.append(f"\n【喜用神解读】")
        lines.append(f"  ▶ 第一用神：{xi_yong['first_yong_shen']}")
        lines.append(f"  ▶ 用神列表：{'、'.join(analysis['yong_shen']) if analysis['yong_shen'] else '需具体格局判断'}")
        lines.append(f"  ▶ 忌神：{'、'.join(analysis['ji_shen']) if analysis['ji_shen'] else '需具体格局判断'}")
        lines.append("")
        lines.append("  【补运建议】")
        for s_item in xi_yong.get("supplement", []):
            lines.append(f"    · {s_item}")
        if xi_yong.get("avoid"):
            lines.append("")
            lines.append("  【注意事项】")
            for a_item in xi_yong["avoid"]:
                lines.append(f"    · {a_item}")
    else:
        lines.append(f"\n【用神】{'、'.join(analysis['yong_shen']) if analysis['yong_shen'] else '需结合具体格局判断'}")
        lines.append(f"【忌神】{'、'.join(analysis['ji_shen']) if analysis['ji_shen'] else '需结合具体格局判断'}")

    # === 忌神规避建议（与喜用神同格式） ===
    ji_avoid = analysis.get("ji_shen_avoid", {})
    if ji_avoid and ji_avoid.get("avoid_items"):
        lines.append("")
        lines.append("【忌神规避】")
        for item in ji_avoid["avoid_items"]:
            lines.append(f"  {item}")
    
    # === 忌神深度解读 ===
    ji_detail = analysis.get("ji_shen_detail", {})
    if ji_detail and ji_detail.get("ji_shen_list"):
        lines.append("")
        lines.append("【忌神警示】")
        for js in ji_detail.get("ji_shen_list", []):
            lines.append(f"  ▼ {js.get('description', '')}")
            if "meaning" in js:
                lines.append(f"    本质：{js['meaning']}")
            if "career_impact" in js:
                lines.append(f"    事业：{js['career_impact']}")
            if "wealth_impact" in js:
                lines.append(f"    财运：{js['wealth_impact']}")
            if "marriage_impact" in js:
                lines.append(f"    婚姻：{js['marriage_impact']}")
            if "health_impact" in js:
                lines.append(f"    健康：{js['health_impact']}")
            if "specific_advice" in js:
                lines.append(f"    化解：{'、'.join(js['specific_advice'])}")
            lines.append("")

    # === 十神分析 ===
    shi_shen_detail = analysis.get("shi_shen_detail", [])
    if shi_shen_detail:
        lines.append(f"\n【十神分析】")
        for ss in shi_shen_detail:
            pos_str = f"在{','.join(ss['positions'])}柱" if ss['positions'] else "在命局中"
            lines.append(f"  ▶ {ss['name']}（{ss['strength']}，{pos_str}）")
            lines.append(f"    {ss['meaning']}")
            life = ss.get("life_impact", {})
            for aspect in ["婚姻", "事业", "财运", "健康"]:
                if aspect in life:
                    lines.append(f"    {aspect}：{life[aspect]}")
            lines.append("")

    # 五行分析
    lines.append(f"【五行综合分析】")
    for wa in analysis["wu_xing_analysis"]:
        lines.append(f"  · {wa}")

    # 大运简析
    lines.append(f"\n【大运简析】")
    for dy in analysis["da_yun_analysis"]:
        lines.append(f"  {dy['gz']}({dy['age']}岁): {dy['gan_comment']}，"
                     f"天干{dy['gan_wx']}·地支{dy['zhi']}({dy['zhi_wx']})")

    lines.append("")
    lines.append("=" * 50)
    return "\n".join(lines)

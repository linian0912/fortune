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

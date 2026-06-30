# -*- coding: utf-8 -*-
"""性格分析模块：结合八字日主五行+十神+紫微命宫主星，生成人格画像。"""

from .core import TIAN_GAN_WX, DI_ZHI_WX

WX_PERSONALITY = {
    "金": {
        "traits": ["果断", "刚毅", "重义", "坚韧"],
        "strengths": ["执行力强", "有原则", "讲信用", "逻辑清晰"],
        "weaknesses": ["固执", "过于刚直", "缺乏变通", "易冲动"],
        "style": "金型人格，如宝剑出鞘，锋芒毕露。行事果断，不拖泥带水。",
        "suitable": ["管理", "金融", "法律", "军警", "工程"],
        "color": "#FFC107",
    },
    "木": {
        "traits": ["仁慈", "正直", "上进", "包容"],
        "strengths": ["有理想", "善于成长", "富有同情心", "创造性强"],
        "weaknesses": ["有时优柔寡断", "好高骛远", "情绪化", "易受挫"],
        "style": "木型人格，如大树参天，不断向上生长。有理想有追求。",
        "suitable": ["教育", "文化", "环保", "医疗", "出版"],
        "color": "#00FF41",
    },
    "水": {
        "traits": ["智慧", "灵活", "沉静", "变通"],
        "strengths": ["思维敏捷", "适应力强", "直觉敏锐", "善于沟通"],
        "weaknesses": ["善变", "过于圆滑", "缺乏恒心", "多愁善感"],
        "style": "水型人格，如江河奔流，随圆就方。智慧灵动，善于变通。",
        "suitable": ["贸易", "传媒", "物流", "旅游", "咨询"],
        "color": "#00E5FF",
    },
    "火": {
        "traits": ["热情", "积极", "礼貌", "奔放"],
        "strengths": ["感染力强", "行动迅速", "乐观开朗", "有领导力"],
        "weaknesses": ["急躁", "冲动", "好面子", "缺乏耐心"],
        "style": "火型人格，如烈焰燃烧，光芒四射。热情奔放，感染力强。",
        "suitable": ["演艺", "餐饮", "能源", "互联网", "销售"],
        "color": "#FF3131",
    },
    "土": {
        "traits": ["诚信", "稳重", "包容", "务实"],
        "strengths": ["踏实可靠", "有耐心", "顾家", "善于理财"],
        "weaknesses": ["保守", "固执", "反应慢", "不善变通"],
        "style": "土型人格，如大地承载万物。稳重可靠，值得信赖。",
        "suitable": ["房地产", "建筑", "农业", "仓储", "行政"],
        "color": "#FFB000",
    },
}


def analyze_personality(bazi, bazi_analysis, ziwei_analysis):
    """
    综合八字和紫微命盘生成性格分析。
    返回结构化性格画像。
    """
    day_wx = bazi.day_wx

    # 1. 五行人格
    wx_profile = WX_PERSONALITY.get(day_wx, WX_PERSONALITY["土"])

    # 2. 十神影响
    shi_shen_detail = bazi_analysis.get("shi_shen_detail", [])
    shi_shen_traits = []
    for ss in shi_shen_detail:
        trait_map = {
            "正官": "正直守信，有责任心",
            "七杀": "果断敢为，有魄力",
            "正印": "温和善良，有智慧",
            "偏印": "思维独特，有创意",
            "正财": "务实节俭，重视物质",
            "偏财": "慷慨大方，善于理财",
            "食神": "温和乐观，有才艺",
            "伤官": "聪明敏锐，才华横溢",
            "比肩": "独立自主，有竞争心",
            "劫财": "社交能力强，重情义",
        }
        trait = trait_map.get(ss["name"])
        if trait:
            shi_shen_traits.append({"name": ss["name"], "trait": trait, "strength": ss.get("strength", "中")})

    # 3. 紫微命宫
    full_gongs = ziwei_analysis.get("full_gongs", {})
    ming_gong = full_gongs.get("命宫", {})
    ming_stars = ming_gong.get("main_stars", [])
    star_personality = _get_star_personality(ming_stars)

    # 4. 综合评估
    strength_level = bazi_analysis.get("strength", {}).get("level", "中和")
    yong_shen = bazi_analysis.get("yong_shen", [])

    # 5. 生成综合描述
    composite = _generate_composite_description(day_wx, wx_profile, shi_shen_traits, star_personality, strength_level)

    return {
        "day_wx": day_wx,
        "wx_profile": wx_profile,
        "shi_shen_traits": shi_shen_traits,
        "star_personality": star_personality,
        "strength_level": strength_level,
        "composite_description": composite,
    }


def _get_star_personality(ming_stars):
    """根据命宫主星获取性格描述。"""
    star_map = {
        "紫微": {"traits": ["尊贵", "领导力", "自信"], "desc": "天生具有领导气质，自信从容，有王者风范。", "advice": "注意谦逊，避免自负。"},
        "天机": {"traits": ["聪慧", "灵活", "善谋"], "desc": "头脑灵活，善于策划分析，是优秀的智囊型人才。", "advice": "需要果决，避免犹豫不决。"},
        "太阳": {"traits": ["热心", "慷慨", "光明"], "desc": "热情开朗，乐于助人，是人群中的小太阳。", "advice": "注意付出有度，劳逸结合。"},
        "武曲": {"traits": ["刚毅", "果断", "理财"], "desc": "性格刚强，执行力一流，对财富有天然嗅觉。", "advice": "刚柔并济，培养感性一面。"},
        "天同": {"traits": ["和善", "知足", "人缘"], "desc": "性格温和，知足常乐，人际关系非常融洽。", "advice": "适当进取，别太过安逸。"},
        "廉贞": {"traits": ["个性", "才华", "自我"], "desc": "个性鲜明，才华横溢，有强烈的自我意识。", "advice": "控制情绪，避免偏执。"},
        "天府": {"traits": ["稳重", "包容", "守成"], "desc": "稳重可靠，善于管理守成，有大家风范。", "advice": "勇于创新，别太保守。"},
        "太阴": {"traits": ["温柔", "细腻", "审美"], "desc": "心思细腻，有艺术细胞，是浪漫的理想主义者。", "advice": "增强决断力，避免优柔。"},
        "贪狼": {"traits": ["多才", "善交", "魅力"], "desc": "多才多艺，社交能力强，是人群中的焦点。", "advice": "专注一处，避免贪多嚼不烂。"},
        "巨门": {"traits": ["善辩", "深思", "诚信"], "desc": "口才出众，善于思考分析，重视信誉。", "advice": "谨言慎行，避免口舌之争。"},
        "天相": {"traits": ["正直", "公正", "服务"], "desc": "为人正直，善于协调，是天生的服务型人才。", "advice": "学会拒绝，避免过度付出。"},
        "天梁": {"traits": ["长者", "助人", "稳重"], "desc": "有长者之风，乐于助人，深受信赖。", "advice": "关注自身，别总为别人操心。"},
        "七杀": {"traits": ["开拓", "勇敢", "果断"], "desc": "敢作敢为，有开拓精神，适合开创性工作。", "advice": "三思而行，避免冒进。"},
        "破军": {"traits": ["变革", "创新", "个性"], "desc": "勇于打破常规，不拘一格，有独特的创造力。", "advice": "稳扎稳打，避免大起大落。"},
    }
    results = []
    for star in ming_stars:
        info = star_map.get(star)
        if info:
            results.append({"star": star, **info})
    return results


def _generate_composite_description(day_wx, wx_profile, shi_shen_traits, star_personality, strength_level):
    """生成综合性格描述文本。"""
    parts = []

    # 五行根基
    parts.append(f"命主五行属{day_wx}，{wx_profile['style']}")

    # 日主旺衰
    level_desc = {
        "旺": "日主旺相，精力充沛，个性鲜明，有较强的自我意识。",
        "偏旺": "日主偏旺，有一定的进取心和行动力。",
        "中和": "日主中和，性格平衡，能屈能伸，适应性好。",
        "偏弱": "日主偏弱，性格相对随和，需外界支持。",
        "弱": "日主较弱，内心敏感，需借助外力发挥潜力。",
    }
    parts.append(level_desc.get(strength_level, ""))

    # 十神汇聚
    if shi_shen_traits:
        top_traits = sorted(shi_shen_traits, key=lambda x: {"强": 3, "中": 2, "弱": 1}.get(x["strength"], 1), reverse=True)[:3]
        traits_text = "，".join([f"{t['name']}使其{t['trait']}" for t in top_traits])
        parts.append(f"命局中{traits_text}。")

    # 紫微星耀
    if star_personality:
        star_texts = [sp["desc"] for sp in star_personality[:2]]
        parts.append("紫微命盘中，" + "；".join(star_texts))

    return "".join(parts)


def format_personality(analysis):
    """格式化为可读文本。"""
    lines = []
    lines.append("")
    lines.append("=" * 50)
    lines.append("                    性格综合分析")
    lines.append("=" * 50)

    wx = analysis["wx_profile"]
    lines.append(f"\n【五行人格】{analysis['day_wx']}型")
    lines.append(f"  {wx['style']}")
    lines.append(f"  特质：{'、'.join(wx['traits'])}")
    lines.append(f"  优势：{'、'.join(wx['strengths'])}")
    lines.append(f"  弱点：{'、'.join(wx['weaknesses'])}")
    lines.append(f"  适合行业：{'、'.join(wx['suitable'][:5])}")

    lines.append(f"\n【日主状态】{analysis['strength_level']}")

    if analysis["shi_shen_traits"]:
        lines.append(f"\n【十神影响】")
        for st in analysis["shi_shen_traits"]:
            lines.append(f"  {st['name']}({st['strength']})：{st['trait']}")

    if analysis["star_personality"]:
        lines.append(f"\n【紫微星耀】")
        for sp in analysis["star_personality"]:
            lines.append(f"  {sp['star']}：{sp['desc']}")
            lines.append(f"    建议：{sp['advice']}")

    lines.append(f"\n【综合画像】")
    lines.append(f"  {analysis['composite_description']}")

    lines.append("")
    lines.append("=" * 50)
    return "\n".join(lines)

# -*- coding: utf-8 -*-
"""紫微斗数命盘分析模块：三方四正、星曜格局、四化解读、宫位分析。"""

# 三方四正：对宫 + 三合宫
# 十二宫从寅(0)开始顺时针：寅卯辰巳午未申酉戌亥子丑

SAN_HE_MAP = {
    0: [0, 4, 8],    # 寅午戌
    1: [1, 5, 9],    # 卯未亥
    2: [2, 6, 10],   # 辰申子
    3: [3, 7, 11],   # 巳酉丑
    4: [0, 4, 8],
    5: [1, 5, 9],
    6: [2, 6, 10],
    7: [3, 7, 11],
    8: [0, 4, 8],
    9: [1, 5, 9],
    10: [2, 6, 10],
    11: [3, 7, 11],
}

DUI_GONG_MAP = {i: (i + 6) % 12 for i in range(12)}

MAIN_STARS = {"紫微", "天机", "太阳", "武曲", "天同", "廉贞",
              "天府", "太阴", "贪狼", "巨门", "天相", "天梁", "七杀", "破军"}


def analyze_san_fang_si_zheng(gongs):
    """分析每个宫位的三方四正星曜组合。"""
    # 先获取每个地支索引对应的宫位
    gong_by_zhi_idx = {}
    for g in gongs:
        from .core import DI_ZHI
        zhi_idx = DI_ZHI.index(g["zhi"])
        gong_by_zhi_idx[zhi_idx] = g

    results = {}
    for g in gongs:
        from .core import DI_ZHI
        zhi_idx = DI_ZHI.index(g["zhi"])
        name = g["name"]

        # 对宫
        dui_idx = DUI_GONG_MAP[zhi_idx]
        dui_gong = gong_by_zhi_idx.get(dui_idx)

        # 三合宫
        san_he_indices = SAN_HE_MAP[zhi_idx]
        san_he_gongs = [gong_by_zhi_idx.get(i) for i in san_he_indices if i != zhi_idx and gong_by_zhi_idx.get(i)]

        # 收集三方四正所有主星
        all_stars = set()
        star_sources = []

        # 本宫
        for s_name, prefix in g["stars"]:
            if s_name in MAIN_STARS:
                all_stars.add(s_name)

        # 对宫
        if dui_gong:
            for s_name, prefix in dui_gong["stars"]:
                if s_name in MAIN_STARS:
                    all_stars.add(s_name)
                    star_sources.append(f"对宫{dui_gong['name']}照{s_name}")

        # 三合宫
        for sg in san_he_gongs:
            for s_name, prefix in sg["stars"]:
                if s_name in MAIN_STARS:
                    all_stars.add(s_name)
                    star_sources.append(f"三合{sg['name']}会{s_name}")

        # 格局判断
        pattern = _check_ziwei_pattern(g, all_stars, dui_gong, san_he_gongs)

        results[name] = {
            "all_stars": sorted(list(all_stars)),
            "star_sources": star_sources,
            "dui_gong": dui_gong["name"] if dui_gong else None,
            "san_he_gongs": [sg["name"] for sg in san_he_gongs],
            "pattern": pattern,
        }

    return results


def _check_ziwei_pattern(gong, all_stars, dui_gong, san_he_gongs):
    """检测星曜格局。"""
    patterns = []

    # 紫微相关格局
    if "紫微" in all_stars:
        if "天府" in all_stars:
            patterns.append("紫府同宫格（紫微天府同宫或会照，主富贵）")
        if "天相" in all_stars:
            patterns.append("紫微天相（权威辅佐，事业有成）")
        if "七杀" in all_stars:
            patterns.append("紫杀（紫微七杀，权威果断）")
        if "破军" in all_stars:
            patterns.append("紫破（紫微破军，变动中开创）")

    # 天府相关
    if "天府" in all_stars:
        if "武曲" in all_stars:
            patterns.append("府武（天府武曲，财库丰厚）")

    # 廉贞相关
    if "廉贞" in all_stars:
        if "贪狼" in all_stars:
            patterns.append("廉贪（廉贞贪狼，才华横溢但需自制）")
        if "七杀" in all_stars:
            patterns.append("廉杀（廉贞七杀，刚烈果决）")

    # 武曲相关
    if "武曲" in all_stars:
        if "贪狼" in all_stars:
            patterns.append("武贪（武曲贪狼，晚发之财）")
        if "天府" in all_stars:
            patterns.append("武府（武曲天府，财富稳定）")

    # 太阳太阴
    if "太阳" in all_stars and "太阴" in all_stars:
        patterns.append("日月并明（阴阳调和，光明磊落）")

    # 空宫
    if not all_stars.intersection(MAIN_STARS):
        patterns.append("借星安宫（本宫无主星，借对宫星曜为用）")

    # 命宫特判
    if gong.get("is_ming") and len(all_stars) >= 3:
        patterns.append(f"命宫主星汇聚（{len(all_stars)}颗主星），命局有力")

    return patterns if patterns else ["普通格局"]


def analyze_si_hua(si_hua, gongs):
    """分析四化在各宫位的含义。"""
    si_hua_map = {
        "化禄": "增加、福气、财禄、人缘",
        "化权": "权力、掌控、专业、权威",
        "化科": "名声、科甲、贵人、才艺",
        "化忌": "困扰、执着、缺失、需注意",
    }

    ziwei_gong_names = {
        "命宫": "自我、个性、一生运势",
        "兄弟": "兄弟姐妹、同辈关系",
        "夫妻": "婚姻、配偶、感情",
        "子女": "子女、晚辈、享乐",
        "财帛": "财运、金钱观、理财",
        "疾厄": "健康、身体、灾厄",
        "迁移": "外出、变动、外地发展",
        "交友": "朋友、下属、社交",
        "官禄": "事业、工作、成就",
        "田宅": "房产、家庭、居住",
        "福德": "精神、福气、心态",
        "父母": "父母、长辈、上司",
    }

    # Build gong lookup by name
    gong_by_name = {}
    for g in gongs:
        gong_by_name[g["name"]] = g

    results = []
    for transform, star in si_hua.items():
        if not star:
            continue
        # Find which gong this star is in
        gong_name = None
        for g in gongs:
            for s_name, prefix in g["stars"]:
                if s_name == star:
                    gong_name = g["name"]
                    break
            if gong_name:
                break

        meaning = si_hua_map.get(transform, "")
        gong_meaning = ziwei_gong_names.get(gong_name, "") if gong_name else "未知宫位"

        results.append({
            "star": star,
            "transform": transform,
            "gong": gong_name or "未知",
            "meaning": meaning,
            "gong_meaning": gong_meaning,
            "interpretation": f"{star}{transform}在{gong_name or '未知'}宫：{meaning}，影响{gong_meaning}",
        })

    return results


def analyze_key_gongs(gongs, san_fang_results):
    """专项宫位解读。"""
    key_gongs = ["命宫", "财帛", "官禄", "夫妻", "疾厄"]
    results = {}

    ziwei_gong_interpretation = {
        "命宫": "代表命主自身性格、天赋、一生运势基调",
        "财帛": "代表赚钱能力、理财观念、财富状况",
        "官禄": "代表事业发展、工作运势、社会成就",
        "夫妻": "代表婚姻状况、配偶特征、感情缘分",
        "疾厄": "代表身体健康、疾病倾向、意外灾祸",
    }

    for g in gongs:
        name = g["name"]
        if name not in key_gongs:
            continue

        # 收集本宫主星
        main_stars = [s_name for s_name, p in g["stars"] if s_name in MAIN_STARS]
        aux_stars = [s_name for s_name, p in g["stars"] if s_name not in MAIN_STARS]

        # 三方四正
        sf = san_fang_results.get(name, {})
        all_stars = sf.get("all_stars", [])
        pattern = sf.get("pattern", [])

        results[name] = {
            "description": ziwei_gong_interpretation.get(name, ""),
            "main_stars": main_stars,
            "aux_stars": aux_stars,
            "san_fang_stars": all_stars,
            "patterns": pattern,
            "kong": len(main_stars) == 0,
        }

    return results


def full_ziwei_analysis(ziwei):
    """对 Ziwei 对象进行完整分析。"""
    gongs = ziwei.gongs

    # 1. 三方四正
    san_fang = analyze_san_fang_si_zheng(gongs)

    # 2. 四化解读
    si_hua_analysis = analyze_si_hua(ziwei.si_hua, gongs)

    # 3. 专项宫位
    key_gongs = analyze_key_gongs(gongs, san_fang)

    # 4. 命宫格局
    ming_patterns = san_fang.get("命宫", {}).get("pattern", [])

    return {
        "san_fang_si_zheng": san_fang,
        "si_hua_analysis": si_hua_analysis,
        "key_gongs": key_gongs,
        "ming_patterns": ming_patterns,
    }


def format_ziwei_analysis(analysis):
    """将紫微分析结果格式化为可读文本。"""
    lines = []
    lines.append("")
    lines.append("=" * 60)
    lines.append("                    紫微斗数命盘分析")
    lines.append("=" * 60)

    # 命宫格局
    lines.append(f"\n【命宫格局】")
    for p in analysis["ming_patterns"]:
        lines.append(f"  · {p}")

    # 四化解读
    lines.append(f"\n【四化飞星解读】")
    for sh in analysis["si_hua_analysis"]:
        lines.append(f"  · {sh['interpretation']}")

    # 重点宫位
    lines.append(f"\n【重点宫位分析】")
    for gong_name, info in analysis["key_gongs"].items():
        lines.append(f"\n  ▶ {gong_name}（{info['description']}）")
        if info["kong"]:
            lines.append(f"    本宫无主星（借星安宫），三方四正：{'、'.join(info['san_fang_stars']) if info['san_fang_stars'] else '空'}")
        else:
            lines.append(f"    主星：{'、'.join(info['main_stars'])}")
            if info["aux_stars"]:
                lines.append(f"    辅星：{'、'.join(info['aux_stars'][:4])}")
        if info["patterns"]:
            lines.append(f"    格局：{'、'.join(info['patterns'])}")

    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)

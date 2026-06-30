# -*- coding: utf-8 -*-
"""紫微斗数命盘分析模块：星曜亮度、三方四正、星曜格局、四化解读、
   宫位全解、大限分析、命盘评分。"""

from .core import TIAN_GAN, DI_ZHI, TIAN_GAN_WX, TIAN_GAN_YY, DI_ZHI_WX

# ============================================================
# 星曜亮度表（庙旺利陷）
# ============================================================
BRIGHTNESS_NAMES = {5: "庙", 4: "旺", 3: "得地", 2: "利益", 1: "平和", 0.5: "不", 0: "陷"}
BRIGHTNESS_COLORS = {5: "#FF3131", 4: "#FFC107", 3: "#00FF41", 2: "#00E5FF", 1: "#6a6a7a", 0.5: "#FFB000", 0: "#6a6a7a"}

_ZW_BRIGHTNESS = {
    "紫微": {0:5,1:5,2:5,3:5,4:4,5:4,6:5,7:4,8:4,9:4,10:3,11:4},
    "天机": {0:4,1:0,2:4,3:4,4:4,5:0,6:4,7:0,8:4,9:4,10:4,11:0},
    "太阳": {0:0,1:2,2:5,3:5,4:4,5:5,6:5,7:2,8:2,9:1,10:0,11:0},
    "武曲": {0:4,1:2,2:2,3:4,4:4,5:4,6:5,7:2,8:5,9:5,10:2,11:2},
    "天同": {0:3,1:3,2:4,3:4,4:2,5:5,6:4,7:2,8:2,9:2,10:2,11:5},
    "廉贞": {0:2,1:2,2:2,3:5,4:2,5:2,6:4,7:2,8:2,9:2,10:2,11:2},
    "天府": {0:4,1:5,2:5,3:4,4:5,5:4,6:5,7:4,8:3,9:4,10:4,11:5},
    "太阴": {0:5,1:5,2:2,3:2,4:5,5:2,6:2,7:2,8:4,9:5,10:2,11:5},
    "贪狼": {0:2,1:2,2:5,3:2,4:2,5:2,6:5,7:2,8:2,9:4,10:2,11:4},
    "巨门": {0:4,1:4,2:3,3:5,4:2,5:2,6:4,7:3,8:5,9:4,10:2,11:3},
    "天相": {0:4,1:2,2:4,3:2,4:3,5:2,6:4,7:2,8:4,9:4,10:2,11:3},
    "天梁": {0:4,1:5,2:2,3:2,4:5,5:2,6:5,7:4,8:2,9:3,10:2,11:2},
    "七杀": {0:4,1:2,2:5,3:3,4:2,5:3,6:4,7:2,8:2,9:3,10:2,11:3},
    "破军": {0:5,1:4,2:2,3:2,4:2,5:2,6:5,7:2,8:2,9:3,10:2,11:5},
}


def get_star_brightness(star_name, zhi):
    """获取星曜在指定地支的亮度。"""
    zhi_idx = DI_ZHI.index(zhi)
    if star_name in _ZW_BRIGHTNESS:
        level = _ZW_BRIGHTNESS[star_name].get(zhi_idx, 1)
        return {"level": level, "name": BRIGHTNESS_NAMES.get(level, "平"), "color": BRIGHTNESS_COLORS.get(level, "#6a6a7a")}
    return {"level": 1, "name": "平", "color": "#6a6a7a"}


# ============================================================
# 十二宫全解读文本
# ============================================================
_GONG_FULL_DESC = {
    "命宫": {"symbol": "👤", "desc": "命宫为十二宫之首，代表命主先天性格、天赋才能、一生运势根基。", "keywords": ["自我","性格","先天禀赋","运势基调"]},
    "兄弟": {"symbol": "👥", "desc": "代表与兄弟姐妹、同辈、密友之间的缘分。也反映母亲的身体状况。", "keywords": ["手足","同辈","合作","母亲健康"]},
    "夫妻": {"symbol": "💑", "desc": "代表配偶特征、婚姻感情状况、恋爱缘分。判断婚姻质量的核心宫位。", "keywords": ["配偶","婚姻","感情","恋爱观"]},
    "子女": {"symbol": "👶", "desc": "代表子女缘分、子女性格、生育能力。也反映性生活、享乐和偏财运。", "keywords": ["子女","生育","享乐","偏财"]},
    "财帛": {"symbol": "💰", "desc": "主一生财运、赚钱能力、理财观念、金钱运势。财富分析的首要宫位。", "keywords": ["正财","理财","赚钱方式","财富格局"]},
    "疾厄": {"symbol": "🏥", "desc": "反映先天体质、疾病倾向、意外灾害。健康分析的重要宫位。", "keywords": ["健康","疾病","意外","体质"]},
    "迁移": {"symbol": "✈️", "desc": "代表外出运势、异乡发展、旅行搬迁。在外表现和机遇。", "keywords": ["外出","异地","旅行","社交形象"]},
    "交友": {"symbol": "🤝", "desc": "代表朋友、下属、同事、社交圈。反映人际关系质量和助力。", "keywords": ["朋友","下属","社交","人脉"]},
    "官禄": {"symbol": "💼", "desc": "主事业发展、工作运势、社会地位和成就。事业分析核心宫位。", "keywords": ["事业","工作","成就","社会地位"]},
    "田宅": {"symbol": "🏠", "desc": "代表房产运势、家庭环境、居住条件、祖业传承。", "keywords": ["房产","家庭","居住","祖业"]},
    "福德": {"symbol": "😊", "desc": "主精神世界、福气享受、晚年运势、内心平和。", "keywords": ["福气","精神","享受","晚年"]},
    "父母": {"symbol": "👨‍👩‍👧", "desc": "代表与父母长辈的关系、父母运势、上司缘。也反映资质和学业运。", "keywords": ["父母","长辈","上司","学业"]},
}


# ============================================================
# 三方四正
# ============================================================
SAN_HE_MAP = {
    0: [0, 4, 8], 1: [1, 5, 9], 2: [2, 6, 10], 3: [3, 7, 11],
    4: [0, 4, 8], 5: [1, 5, 9], 6: [2, 6, 10], 7: [3, 7, 11],
    8: [0, 4, 8], 9: [1, 5, 9], 10: [2, 6, 10], 11: [3, 7, 11],
}

DUI_GONG_MAP = {i: (i + 6) % 12 for i in range(12)}

MAIN_STARS = {"紫微","天机","太阳","武曲","天同","廉贞",
              "天府","太阴","贪狼","巨门","天相","天梁","七杀","破军"}

# 六吉星
JI_XING = {"文昌","文曲","左辅","右弼","天魁","天钺","禄存","天马"}
# 六煞星
SHA_XING = {"擎羊","陀罗","火星","铃星","地空","地劫"}


def analyze_san_fang_si_zheng(gongs):
    """分析每个宫位的三方四正星曜组合。"""
    gong_by_zhi_idx = {}
    for g in gongs:
        zhi_idx = DI_ZHI.index(g["zhi"])
        gong_by_zhi_idx[zhi_idx] = g

    results = {}
    for g in gongs:
        zhi_idx = DI_ZHI.index(g["zhi"])
        name = g["name"]

        dui_idx = DUI_GONG_MAP[zhi_idx]
        dui_gong = gong_by_zhi_idx.get(dui_idx)

        san_he_indices = SAN_HE_MAP[zhi_idx]
        san_he_gongs = [gong_by_zhi_idx.get(i) for i in san_he_indices if i != zhi_idx and gong_by_zhi_idx.get(i)]

        all_stars = set()
        star_sources = []

        for s_name, prefix in g["stars"]:
            if s_name in MAIN_STARS:
                all_stars.add(s_name)

        if dui_gong:
            for s_name, prefix in dui_gong["stars"]:
                if s_name in MAIN_STARS:
                    all_stars.add(s_name)
                    star_sources.append(f"对宫{dui_gong['name']}照{s_name}")

        for sg in san_he_gongs:
            for s_name, prefix in sg["stars"]:
                if s_name in MAIN_STARS:
                    all_stars.add(s_name)
                    star_sources.append(f"三合{sg['name']}会{s_name}")

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
    if "紫微" in all_stars:
        if "天府" in all_stars: patterns.append("紫府同宫格（紫微天府同宫或会照，主富贵）")
        if "天相" in all_stars: patterns.append("紫微天相（权威辅佐，事业有成）")
        if "七杀" in all_stars: patterns.append("紫杀（紫微七杀，权威果断）")
        if "破军" in all_stars: patterns.append("紫破（紫微破军，变动中开创）")
    if "武曲" in all_stars:
        if "贪狼" in all_stars: patterns.append("武贪（武曲贪狼，晚发之财）")
        if "天府" in all_stars: patterns.append("武府（武曲天府，财富稳定）")
    if "廉贞" in all_stars:
        if "贪狼" in all_stars: patterns.append("廉贪（廉贞贪狼，才华横溢但需自制）")
        if "七杀" in all_stars: patterns.append("廉杀（廉贞七杀，刚烈果决）")
    if "太阳" in all_stars and "太阴" in all_stars:
        patterns.append("日月并明（阴阳调和，光明磊落）")
    if "天同" in all_stars and "天梁" in all_stars:
        patterns.append("同梁（天同天梁，福寿双全）")
    if not all_stars.intersection(MAIN_STARS):
        patterns.append("借星安宫（本宫无主星，借对宫星曜为用）")
    if gong.get("is_ming") and len(all_stars) >= 3:
        patterns.append(f"命宫主星汇聚（{len(all_stars)}颗主星），命局有力")
    return patterns if patterns else ["普通格局"]


def analyze_si_hua(si_hua, gongs):
    """分析四化在各宫位的含义。"""
    si_hua_map = {"化禄":"增加、福气、财禄、人缘","化权":"权力、掌控、专业、权威","化科":"名声、科甲、贵人、才艺","化忌":"困扰、执着、缺失、需注意"}
    ziwei_gong_names = {"命宫":"自我、个性、一生运势","兄弟":"兄弟姐妹、同辈关系","夫妻":"婚姻、配偶、感情","子女":"子女、晚辈、享乐","财帛":"财运、金钱观、理财","疾厄":"健康、身体、灾厄","迁移":"外出、变动、外地发展","交友":"朋友、下属、社交","官禄":"事业、工作、成就","田宅":"房产、家庭、居住","福德":"精神、福气、心态","父母":"父母、长辈、上司"}
    gong_by_name = {}
    for g in gongs: gong_by_name[g["name"]] = g

    results = []
    for transform, star in si_hua.items():
        if not star: continue
        gong_name = None
        for g in gongs:
            for s_name, prefix in g["stars"]:
                if s_name == star: gong_name = g["name"]; break
            if gong_name: break
        meaning = si_hua_map.get(transform, "")
        gong_meaning = ziwei_gong_names.get(gong_name, "") if gong_name else "未知宫位"
        results.append({"star":star,"transform":transform,"gong":gong_name or "未知","meaning":meaning,"gong_meaning":gong_meaning,"interpretation":f"{star}{transform}在{gong_name or '未知'}宫：{meaning}，影响{gong_meaning}"})
    return results


# ============================================================
# 十二宫全解读
# ============================================================
def analyze_full_twelve_gongs(gongs, san_fang_results):
    """完整十二宫解读（含星曜亮度）。"""
    results = {}
    for g in gongs:
        name = g["name"]
        desc_data = _GONG_FULL_DESC.get(name, {})
        main_stars = [s_name for s_name, p in g["stars"] if s_name in MAIN_STARS]
        aux_stars = [s_name for s_name, p in g["stars"] if s_name not in MAIN_STARS]

        star_brightness = {}
        for ms in main_stars:
            star_brightness[ms] = get_star_brightness(ms, g["zhi"])

        sf = san_fang_results.get(name, {})
        all_stars = sf.get("all_stars", [])
        patterns = sf.get("pattern", [])

        interpretation = _generate_gong_interpretation(name, main_stars, star_brightness, patterns, g)

        # 辅星吉凶分类
        aux_ji = [s for s in aux_stars if s in JI_XING]
        aux_sha = [s for s in aux_stars if s in SHA_XING]
        aux_other = [s for s in aux_stars if s not in JI_XING and s not in SHA_XING]

        results[name] = {
            "symbol": desc_data.get("symbol", ""),
            "description": desc_data.get("desc", ""),
            "keywords": desc_data.get("keywords", []),
            "main_stars": main_stars,
            "aux_stars": aux_stars,
            "aux_ji": aux_ji,
            "aux_sha": aux_sha,
            "star_brightness": star_brightness,
            "san_fang_stars": all_stars,
            "patterns": patterns,
            "kong": len(main_stars) == 0,
            "interpretation": interpretation,
        }
    return results


def _generate_gong_interpretation(gong_name, main_stars, star_brightness, patterns, gong):
    """生成单个宫位的命理解读文本。"""
    parts = []
    if gong.get("is_ming"): parts.append("命宫统摄全局。")
    if gong.get("is_shen"): parts.append("身宫代表后天重心。")
    if not main_stars:
        parts.append("本宫无主星（空宫），借对宫为用。")
    else:
        star_descs = []
        for ms in main_stars:
            bright = star_brightness.get(ms, {})
            b_name = bright.get("name", "平")
            star_descs.append(f"{ms}({b_name})")
        parts.append(f"主星{'、'.join(star_descs)}。")

    gen_map = {"命宫":_gen_ming,"财帛":_gen_caibo,"官禄":_gen_guanlu,"夫妻":_gen_fuqi,"疾厄":_gen_jie,"子女":_gen_zinv,"田宅":_gen_tianzhai,"迁移":_gen_qianyi,"福德":_gen_fude}
    gen_func = gen_map.get(gong_name)
    if gen_func:
        gen_text = gen_func(main_stars, star_brightness)
        if gen_text: parts.append(gen_text)

    if len(main_stars) == 0 and not gong.get("is_ming"):
        parts.append("此宫为空，运势以此宫对宫和三方四正为主。")

    return "".join(parts)


def _gen_ming(stars, br):
    m = {"紫微":"命主有领导气质，天生尊贵。","天机":"命主聪明机敏，思维灵活。","太阳":"命主热情开朗，乐于助人。","武曲":"命主刚毅果断，执行力强。","天同":"命主温和友善，知足常乐。","廉贞":"命主个性鲜明，才华横溢。","天府":"命主稳重可靠，有包容心。","太阴":"命主温柔细腻，直觉敏锐。","贪狼":"命主多才多艺，擅长社交。","巨门":"命主口才好，善于思考辩论。","天相":"命主正直公道，善于协调。","天梁":"命主有长者之风，乐于助人。","七杀":"命主有开拓精神，敢作敢为。","破军":"命主勇于变革，人生起伏较大。"}
    for s in stars:
        if s in m: return m[s]
    return None

def _gen_caibo(stars, br):
    m = {"武曲":"财星入财帛宫，财运旺盛。","太阴":"财源细水长流，适合理性投资。","天府":"财库丰厚，善于守财。","贪狼":"偏财运佳，但需节制消费。","廉贞":"财运波动，需谨慎投资。","紫微":"贵人助财，权财相生。"}
    for s in stars:
        if s in m: return m[s]
    return None

def _gen_guanlu(stars, br):
    m = {"紫微":"事业有领导运，适合管理或创业。","天府":"事业稳定，适合大企业和公职。","七杀":"事业有冲劲，适合创业和竞争。","破军":"事业多变有机遇，适合创新。","天相":"适合协调型工作如行政公关。","太阳":"适合公众型事业如教育传媒。","天梁":"适合教育医疗司法等行业。","巨门":"靠口才和专业知识发展。"}
    for s in stars:
        if s in m: return m[s]
    return None

def _gen_fuqi(stars, br):
    m = {"紫微":"配偶有领导气质，需互相尊重。","天府":"配偶稳重可靠，婚姻安定。","太阴":"配偶温柔体贴，注重情感。","贪狼":"配偶有魅力，桃花旺需信任。","七杀":"配偶性格刚烈，有激情需包容。","破军":"婚姻多变，需双方共同经营。","天同":"婚姻和谐美满，夫妻融洽。","巨门":"需加强沟通，避免口舌之争。","天相":"配偶正直可靠，婚姻稳定。"}
    for s in stars:
        if s in m: return m[s]
    return None

def _gen_jie(stars, br):
    m = {"太阳":"需注意心脏、眼睛和血液循环。","太阴":"需注意肾脏、泌尿和情绪。","武曲":"需注意呼吸系统和骨骼关节。","贪狼":"需注意肝脏和内分泌。","巨门":"需注意消化系统和口腔。","天同":"先天体质较好，大病不侵。","天梁":"虽有病痛但能逢凶化吉。","七杀":"需注意意外伤害，多加小心。","破军":"身体状况易波动，规律生活。"}
    for s in stars:
        if s in m: return m[s]
    return None

def _gen_zinv(stars, br):
    m = {"紫微":"子女有领导才能，优秀有作为。","天机":"子女聪明好学，多才多艺。","太阳":"子女热情开朗，有事业心。","武曲":"子女性格刚强独立。","天同":"子女乖巧可爱，亲子和谐。"}
    for s in stars:
        if s in m: return m[s]
    return None

def _gen_tianzhai(stars, br):
    m = {"天府":"房产运好，有不动产缘。","紫微":"居住环境气派，家庭地位高。","太阴":"喜欢清静优雅的居住环境。","贪狼":"对居住品质要求高。"}
    for s in stars:
        if s in m: return m[s]
    return None

def _gen_qianyi(stars, br):
    m = {"太阳":"外出发展有利，适合异地工作。","天机":"常有机遇在外，适合出差旅行。","七杀":"外出有冲劲，适合开拓新市场。","破军":"搬迁或异地发展机会多。"}
    for s in stars:
        if s in m: return m[s]
    return None

def _gen_fude(stars, br):
    m = {"天同":"福气深厚，知足常乐，晚年安逸。","天梁":"有福德庇佑，晚年有善缘。","天府":"精神富足，生活品质高。","太阴":"内心丰富，懂得享受生活。"}
    for s in stars:
        if s in m: return m[s]
    return None


# ============================================================
# 大限分析
# ============================================================
def analyze_da_xian(ming_zhi_idx, wx_ju_name, gender, year_gan, gongs):
    """紫微大限分析：每十年一限。阳男/阴女顺行，阴男/阳女逆行。"""
    gan_yy = TIAN_GAN_YY.get(year_gan, 1)
    is_male = (gender == "male")
    shun_xing = (gan_yy == 1 and is_male) or (gan_yy == 0 and not is_male)

    ju_num = {"金":4,"木":3,"水":2,"火":6,"土":5}.get(wx_ju_name, 5)
    da_xian = []

    start_age = ju_num
    for i in range(12):
        if shun_xing:
            gong_idx = (ming_zhi_idx + i) % 12
        else:
            gong_idx = (ming_zhi_idx - i) % 12

        age_from = start_age + i * 10
        age_to = age_from + 9

        gong = gongs[gong_idx] if gong_idx < len(gongs) else {"name":"未知","zhi":"?","stars":[]}
        main_stars = [s_name for s_name, p in gong["stars"] if s_name in MAIN_STARS]

        if not main_stars:
            comment = "运势平稳，宜稳扎稳打"
        elif "紫微" in main_stars or "天府" in main_stars or "天相" in main_stars:
            comment = "大运亨通，贵人相助，事业上升"
        elif "七杀" in main_stars or "破军" in main_stars:
            comment = "变动较大，机遇与挑战并存"
        elif "贪狼" in main_stars:
            comment = "多机遇，需把握方向"
        elif "廉贞" in main_stars:
            comment = "需谨慎行事，注意人际"
        elif "巨门" in main_stars:
            comment = "口舌是非多，谨言慎行"
        else:
            comment = "运势平稳，宜深耕发展"

        da_xian.append({
            "age_range": f"{age_from}-{age_to}",
            "start_age": age_from,
            "gong_name": gong["name"],
            "gong_zhi": gong.get("zhi", "?"),
            "main_stars": main_stars,
            "comment": comment,
            "is_current": False,
        })

    return da_xian


# ============================================================
# 完整分析 + 评分
# ============================================================
def _compute_ziwei_score(full_gongs, ming_patterns, san_fang):
    """紫微命盘综合评分。"""
    score = 50
    details = []
    ming = full_gongs.get("命宫", {})
    ming_stars = ming.get("main_stars", [])
    if len(ming_stars) >= 2:
        score += 10; details.append("命宫双主星汇聚，格局有力")
    elif len(ming_stars) == 1:
        score += 5
    else:
        score -= 5; details.append("命宫空宫，需借星安宫")

    good_patterns = 0
    for p in ming_patterns:
        if "普通" not in p: good_patterns += 1
    score += good_patterns * 5
    if good_patterns >= 2:
        details.append(f"格局优良：{good_patterns}个吉格")

    caibo = full_gongs.get("财帛", {})
    if "武曲" in caibo.get("main_stars", []) or "天府" in caibo.get("main_stars", []):
        score += 8; details.append("财帛宫有财星坐守")
    elif caibo.get("main_stars"):
        score += 3

    guanlu = full_gongs.get("官禄", {})
    if "紫微" in guanlu.get("main_stars", []) or "天府" in guanlu.get("main_stars", []):
        score += 8; details.append("官禄宫有吉星坐守")
    elif guanlu.get("main_stars"):
        score += 3

    jx_count = 0
    sha_count = 0
    for g in full_gongs.values():
        for s in g.get("aux_stars", []):
            if s in JI_XING: jx_count += 1
            if s in SHA_XING: sha_count += 1
    score += min(jx_count * 3, 15)
    score -= min(sha_count * 2, 12)
    if jx_count >= 4:
        details.append(f"辅星得力：{jx_count}颗吉星拱照")

    level = "上等" if score >= 75 else "中上" if score >= 60 else "中等" if score >= 45 else "中下" if score >= 35 else "下等"
    return {"score": min(score, 98), "level": level, "details": details}


def full_ziwei_analysis(ziwei):
    """对 Ziwei 对象进行完整分析（扩展版）。"""
    gongs = ziwei.gongs

    san_fang = analyze_san_fang_si_zheng(gongs)
    si_hua_analysis = analyze_si_hua(ziwei.si_hua, gongs)
    full_gongs = analyze_full_twelve_gongs(gongs, san_fang)

    ming_zhi = ziwei.gongs[0]["zhi"] if ziwei.gongs else "寅"
    ming_zhi_idx = DI_ZHI.index(ming_zhi)
    wx_ju_name = ziwei.wx_ju_name
    year_gan = ziwei.ming_gan_zhi[0] if ziwei.ming_gan_zhi else "甲"
    da_xian = analyze_da_xian(ming_zhi_idx, wx_ju_name, ziwei.gender, year_gan, ziwei.gongs)

    ming_patterns = san_fang.get("命宫", {}).get("pattern", [])
    overall_score = _compute_ziwei_score(full_gongs, ming_patterns, san_fang)

    return {
        "san_fang_si_zheng": san_fang,
        "si_hua_analysis": si_hua_analysis,
        "full_gongs": full_gongs,
        "key_gongs": {k: v for k, v in full_gongs.items() if k in ["命宫","财帛","官禄","夫妻","疾厄"]},
        "ming_patterns": ming_patterns,
        "da_xian": da_xian,
        "overall_score": overall_score,
    }


def format_ziwei_analysis(analysis):
    """将紫微分析结果格式化为可读文本。"""
    lines = []
    lines.append("")
    lines.append("=" * 60)
    lines.append("                    紫微斗数命盘分析")
    lines.append("=" * 60)

    lines.append(f"\n【命宫格局】")
    for p in analysis["ming_patterns"]:
        lines.append(f"  · {p}")

    lines.append(f"\n【四化飞星解读】")
    for sh in analysis["si_hua_analysis"]:
        lines.append(f"  · {sh['interpretation']}")

    lines.append(f"\n【重点宫位分析】")
    for gong_name, info in analysis["key_gongs"].items():
        lines.append(f"\n  ▶ {gong_name}（{info['description']}）")
        if info.get("kong"):
            lines.append(f"    本宫无主星（借星安宫）")
        else:
            for ms in info.get("main_stars", []):
                bright = info.get("star_brightness", {}).get(ms, {})
                lines.append(f"    {ms}({bright.get('name','平')})")
        if info.get("patterns"):
            lines.append(f"    格局：{'、'.join(info['patterns'])}")
        if info.get("interpretation"):
            lines.append(f"    解读：{info['interpretation']}")

    if analysis.get("da_xian"):
        lines.append(f"\n【大限走势】")
        for dx in analysis["da_xian"]:
            stars_str = '、'.join(dx['main_stars'][:3]) if dx['main_stars'] else '—'
            lines.append(f"  {dx['age_range']}岁 {dx['gong_name']}({dx['gong_zhi']}): {dx['comment']}  {stars_str}")

    score = analysis.get("overall_score", {})
    if score:
        lines.append(f"\n【命盘评分】{score.get('score',0)}分（{score.get('level','')}）")
        for d in score.get("details", []):
            lines.append(f"  · {d}")

    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


# 向后兼容
def analyze_key_gongs(gongs, san_fang_results):
    return analyze_full_twelve_gongs(gongs, san_fang_results)

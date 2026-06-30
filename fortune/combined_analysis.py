# -*- coding: utf-8 -*-
"""
综合命理分析模块：将八字和紫微斗数分析结果
按生活维度（婚姻、事业、财运、子女、健康）整合输出。
八字体系与紫微体系分开陈列，两者分析方法不同、内容不同。
"""

from .core import TIAN_GAN_WX, DI_ZHI_WX, DI_ZHI_CANG_GAN, SHENG_XIAO

# ============================================================
# 五行关系辅助
# ============================================================

def _sheng_wo(wx):
    m = {"金": ["土"], "木": ["水"], "水": ["金"], "火": ["木"], "土": ["火"]}
    return m.get(wx, [])

def _wo_sheng(wx):
    m = {"金": ["水"], "木": ["火"], "水": ["木"], "火": ["土"], "土": ["金"]}
    return m.get(wx, [])

def _wo_ke(wx):
    m = {"金": ["木"], "木": ["土"], "水": ["火"], "火": ["金"], "土": ["水"]}
    return m.get(wx, [])

def _ke_wo(wx):
    m = {"金": ["火"], "木": ["金"], "水": ["土"], "火": ["水"], "土": ["木"]}
    return m.get(wx, [])


# ============================================================
# 1. 婚姻分析
# ============================================================

def analyze_marriage_bazi(bazi, bazi_analysis):
    result = {
        "title": "婚姻情感", "icon": "💑", "color": "#FF6B9D",
        "summary": "", "details": [], "advice": [],
    }
    day_wx = bazi.day_wx
    day_zhi = bazi.day_zhi
    ri_zhi_wx = DI_ZHI_WX[day_zhi]
    gender = bazi.gender
    details, advice = [], []

    if day_wx == ri_zhi_wx:
        details.append(f"日坐{ri_zhi_wx}，配偶宫为比劫，配偶性格独立强势，婚姻中有竞争意识")
        advice.append("婚姻中需注意沟通，避免因个性太强产生摩擦")
    elif ri_zhi_wx in _sheng_wo(day_wx):
        details.append(f"日坐{ri_zhi_wx}，配偶宫为印星，配偶体贴照顾，婚姻温馨稳定")
    elif ri_zhi_wx in _wo_sheng(day_wx):
        details.append(f"日坐{ri_zhi_wx}，配偶宫为食伤，对方有才艺但需注意沟通方式")
    elif ri_zhi_wx in _wo_ke(day_wx):
        details.append(f"日坐{ri_zhi_wx}，配偶宫为财星，配偶有理财能力，婚姻有物质基础")
        if gender == "male":
            details.append("男命日坐财星，配偶贤惠持家")
    elif ri_zhi_wx in _ke_wo(day_wx):
        details.append(f"日坐{ri_zhi_wx}，配偶宫为官星，配偶有责任心，但约束较多")
        if gender == "female":
            details.append("女命日坐官星，丈夫有事业心")

    ss_map = {s["name"]: s for s in bazi_analysis.get("shi_shen_detail", [])}
    if gender == "male":
        zc, pc = ss_map.get("正财", {}), ss_map.get("偏财", {})
        if zc:
            details.append("正财现于命局，婚姻基础较稳，适合稳定家庭生活")
            advice.append("珍惜正缘，避免因偏财动摇婚姻")
        if pc and pc.get("count", 0) >= 2:
            details.append("偏财过旺，异性缘好但须防感情波折")
            advice.append("注意区分正缘偏缘，避免多角关系")
        if not zc and not pc:
            details.append("财星不显，婚缘较晚，需主动拓展社交")
            advice.append("多参加社交活动，扩大交际圈有助婚姻")
    else:
        zg, qs = ss_map.get("正官", {}), ss_map.get("七杀", {})
        if zg:
            details.append("正官现于命局，婚缘较顺，配偶正直可靠")
        if qs:
            if qs.get("count", 0) >= 2:
                details.append("七杀多现，感情经历较丰富，晚婚为宜")
                advice.append("感情中需理性抉择")
            else:
                details.append("七杀一位，配偶有魄力，婚姻有激情但需包容")
        if not zg and not qs:
            details.append("官杀不显，姻缘较晚，配偶或为外地人/年龄差大")

    sg = ss_map.get("伤官", {})
    if gender == "female" and sg:
        details.append("女命伤官，感情道路较曲折，需注意表达方式")
        advice.append("收敛锋芒，学会以柔克刚")
    ss = ss_map.get("食神", {})
    if ss and ss.get("count", 0) >= 2:
        details.append("食神旺相，性情温和注重生活品质")

    xi_yong = bazi_analysis.get("xi_yong_shen", {})
    if xi_yong.get("first_yong_shen"):
        wx_adv = _wx_marriage_advice(xi_yong["first_yong_shen"])
        if wx_adv:
            advice.append(wx_adv)

    ji_detail = bazi_analysis.get("ji_shen_detail", {})
    if ji_detail and ji_detail.get("ji_shen_list"):
        for js in ji_detail.get("ji_shen_list", []):
            if js.get("marriage_impact"):
                advice.append(js["marriage_impact"])

    result["details"] = details
    result["advice"] = advice
    result["summary"] = details[0] if details else "婚姻运势需结合具体命局详批"
    return result


def analyze_marriage_ziwei(ziwei, ziwei_analysis):
    result = {"details": [], "advice": []}
    key_gongs = ziwei_analysis.get("key_gongs", {})
    san_fang = ziwei_analysis.get("san_fang_si_zheng", {})
    si_hua = ziwei_analysis.get("si_hua_analysis", [])

    fq = key_gongs.get("夫妻", {})
    if fq:
        main_stars = fq.get("main_stars", [])
        sf_stars = fq.get("san_fang_stars", [])
        if fq.get("kong"):
            result["details"].append("夫妻宫无主星，婚姻缘分需靠后天经营")
        else:
            sd = _star_marriage_desc(main_stars)
            if sd:
                result["details"].append(sd)
        peach = {"贪狼", "廉贞", "天同"}
        pf = [s for s in sf_stars if s in peach]
        if pf:
            result["details"].append(f"三方四正有{'、'.join(pf)}，异性缘旺，桃花较多")

    for sh in si_hua:
        if sh.get("gong") == "夫妻":
            result["details"].append(sh.get("interpretation", ""))
            if sh.get("transform") == "化禄":
                result["details"].append("化禄入夫妻宫，婚姻福气深厚，配偶旺夫/旺妻")
            elif sh.get("transform") == "化忌":
                result["details"].append("化忌入夫妻宫，婚姻中需多加包容与沟通")
                result["advice"].append("以柔克刚，退一步海阔天空")
    return result


# ============================================================
# 2. 事业分析
# ============================================================

def analyze_career_bazi(bazi, bazi_analysis):
    result = {
        "title": "事业运势", "icon": "💼", "color": "#00E5FF",
        "summary": "", "details": [], "advice": [], "suitable_careers": [],
    }
    ss_map = {s["name"]: s for s in bazi_analysis.get("shi_shen_detail", [])}
    da_yun = bazi_analysis.get("da_yun_analysis", [])
    xi_yong = bazi_analysis.get("xi_yong_shen", {})
    strength = bazi_analysis.get("strength", {})
    details, advice, careers = [], [], []

    zg = ss_map.get("正官", {})
    qs = ss_map.get("七杀", {})
    zy = ss_map.get("正印", {})
    py = ss_map.get("偏印", {})
    ss = ss_map.get("食神", {})
    sg = ss_map.get("伤官", {})

    if zg:
        if zg.get("count", 0) >= 2:
            details.append("正官旺盛，有领导才能和管理天赋，适合体制内或管理岗位")
            careers.extend(["公务员", "企业管理", "法律"])
        else:
            details.append("正官一位清透，正直守规矩，做事有章法")
            careers.extend(["行政", "管理"])
    if qs:
        if qs.get("count", 0) >= 2:
            details.append("七杀多现，有魄力和决断力，适合竞争性行业或创业")
            careers.extend(["创业", "军警", "竞技"])
        else:
            details.append("七杀一位有威，进取心强，敢于挑战权威")
            careers.extend(["管理", "项目经理"])
    if zy or py:
        details.append("有印星加持，学习能力强，适合学术研究或专业技术路线")
        careers.extend(["教育", "科研", "技术专家"])
    if ss and ss.get("count", 0) >= 2:
        details.append("食神旺盛，有艺术才华和创造力，适合创意型或服务型行业")
        careers.extend(["艺术", "美食", "设计"])
    if sg and sg.get("count", 0) >= 2:
        details.append("伤官旺盛，思维敏捷富有创新，适合科技设计等领域")
        careers.extend(["科技", "创新设计", "技术研发"])
    for g in bazi_analysis.get("ge_ju", []):
        if g:
            details.append(f"格局：{g}")
    level = strength.get("level", "")
    if level in ("旺", "偏旺"):
        details.append("日主旺相，精力充沛，适合高强度高压力工作环境")
        advice.append("工作中注意劳逸结合，避免过度透支")
    elif level in ("弱", "偏弱"):
        details.append("日主偏弱，适合在团队中发挥专长，不必独当一面")
        advice.append("善用贵人资源，不必凡事亲力亲为")
    if xi_yong.get("first_yong_shen"):
        first = xi_yong["first_yong_shen"]
        wx_c = _wx_career_advice(first)
        if wx_c:
            careers.extend(wx_c)
            details.append(f"喜用神为{first}，适合{first}属性行业：{'、'.join(wx_c)}")
    ji_detail = bazi_analysis.get("ji_shen_detail", {})
    if ji_detail and ji_detail.get("ji_shen_list"):
        for js in ji_detail.get("ji_shen_list", []):
            if js.get("career_impact"):
                advice.append(js["career_impact"])
    good_years = []
    for dy in da_yun[:6]:
        if dy.get("gan_comment") in ("官杀运", "财运", "印运"):
            good_years.append(f"{dy['age']}岁{dy['gan_comment']}")
    if good_years:
        details.append(f"事业机遇期：{'、'.join(good_years[:3])}")
    result["details"] = details
    result["advice"] = advice
    result["suitable_careers"] = list(set(careers))[:8]
    result["summary"] = details[0] if details else "事业运势平稳，需结合大运把握机遇"
    return result


def analyze_career_ziwei(ziwei, ziwei_analysis):
    result = {"details": [], "advice": []}
    key_gongs = ziwei_analysis.get("key_gongs", {})
    si_hua = ziwei_analysis.get("si_hua_analysis", [])
    gl = key_gongs.get("官禄", {})
    if gl:
        if gl.get("kong"):
            result["details"].append("官禄宫无主星，事业方向需参考对宫或三方四正")
        else:
            sd = _star_career_desc(gl.get("main_stars", []))
            if sd:
                result["details"].append(sd)
        sf_stars = gl.get("san_fang_stars", [])
        if any(s in sf_stars for s in {"紫微","天府","太阳","武曲"}):
            result["details"].append("三方四正有领导型星曜，适合管理或创业路线")
        if any(s in sf_stars for s in {"贪狼","天同","太阴","廉贞"}):
            result["details"].append("三方四正有才艺型星曜，适合创意或服务行业")
    qy = key_gongs.get("迁移", {})
    if qy and qy.get("main_stars"):
        result["details"].append("迁移宫有主星，适合外出发展或异地就业")
    for sh in si_hua:
        if sh.get("gong") == "官禄":
            result["details"].append(sh.get("interpretation", ""))
            if sh.get("transform") == "化禄":
                result["details"].append("化禄入官禄宫，事业运势旺盛，易得贵人提携")
            elif sh.get("transform") == "化权":
                result["details"].append("化权入官禄宫，有管理才能，可在职场掌权")
            elif sh.get("transform") == "化忌":
                result["details"].append("化忌入官禄宫，事业中需防小人或变数")
                result["advice"].append("以稳为主，避免频繁跳槽")
    return result


# ============================================================
# 3. 财运分析
# ============================================================

def analyze_wealth_bazi(bazi, bazi_analysis):
    result = {
        "title": "财运财富", "icon": "💰", "color": "#FFC107",
        "summary": "", "details": [], "advice": [], "wealth_traits": [],
    }
    ss_map = {s["name"]: s for s in bazi_analysis.get("shi_shen_detail", [])}
    da_yun = bazi_analysis.get("da_yun_analysis", [])
    xi_yong = bazi_analysis.get("xi_yong_shen", {})
    details, advice, traits = [], [], []

    zc = ss_map.get("正财", {})
    pc = ss_map.get("偏财", {})
    ss = ss_map.get("食神", {})
    sg = ss_map.get("伤官", {})

    if zc:
        if zc.get("count", 0) >= 2:
            details.append("正财旺盛，财运稳健，适合固定收入和长期投资")
            traits.append("稳定型收入")
        else:
            details.append("正财一位清透，有稳定财富基础，理财观念良好")
            traits.append("稳健理财")
    if pc:
        if pc.get("count", 0) >= 2:
            details.append("偏财旺盛，有投资眼光和意外财运，但稳定性不足")
            traits.append("投资型收入")
            advice.append("见好就收，不宜将所有资产投入高风险领域")
        else:
            details.append("偏财一位，有投资灵感但需谨慎操作")
            traits.append("有投资眼光")
    if ss and (zc or pc):
        details.append("食神生财，以才华技艺赚钱，财富与个人能力紧密相关")
        traits.append("靠才华赚钱")
    if sg and (zc or pc) and sg.get("count", 0) >= 2:
        details.append("伤官生财，聪明才智化为财富，收入渠道多但波动大")
        traits.append("多渠道收入")
    if not zc and not pc:
        details.append("财星不显，不以财富为主要追求，更重精神价值")
        advice.append("可借助食伤或官杀间接求财")
        traits.append("非财主导型")
    good_years = []
    for dy in da_yun[:6]:
        if dy.get("gan_comment") == "财运":
            good_years.append(f"{dy['age']}岁")
    if good_years:
        details.append(f"财运高峰期：{'、'.join(good_years)}前后")
    if xi_yong.get("first_yong_shen"):
        wx_w = _wx_wealth_advice(xi_yong["first_yong_shen"])
        if wx_w:
            advice.append(wx_w)
    ji_detail = bazi_analysis.get("ji_shen_detail", {})
    if ji_detail and ji_detail.get("ji_shen_list"):
        for js in ji_detail.get("ji_shen_list", []):
            if js.get("wealth_impact"):
                advice.append(js["wealth_impact"])
    result["details"] = details
    result["advice"] = advice
    result["wealth_traits"] = traits
    result["summary"] = details[0] if details else "财运平稳，需根据大运把握机遇"
    return result


def analyze_wealth_ziwei(ziwei, ziwei_analysis):
    result = {"details": [], "advice": []}
    key_gongs = ziwei_analysis.get("key_gongs", {})
    si_hua = ziwei_analysis.get("si_hua_analysis", [])
    cb = key_gongs.get("财帛", {})
    if cb:
        if cb.get("kong"):
            result["details"].append("财帛宫无主星，财运起伏较大，需借对宫之力求财")
        else:
            sd = _star_wealth_desc(cb.get("main_stars", []))
            if sd:
                result["details"].append(sd)
    tz = key_gongs.get("田宅", {})
    if tz and tz.get("main_stars"):
        result["details"].append(f"田宅宫有{'、'.join(tz['main_stars'])}，不动产运势较旺")
    for sh in si_hua:
        if sh.get("gong") == "财帛":
            result["details"].append(sh.get("interpretation", ""))
            if sh.get("transform") == "化禄":
                result["details"].append("化禄入财帛宫，财运亨通，收入源源不断")
            elif sh.get("transform") == "化忌":
                result["details"].append("化忌入财帛宫，财务上需精打细算")
                result["advice"].append("保守理财，避免高风险投资")
    return result


# ============================================================
# 4. 子女分析
# ============================================================

def analyze_children_bazi(bazi, bazi_analysis):
    result = {"title": "子女运程", "icon": "👶", "color": "#00FF41", "summary": "", "details": [], "advice": []}
    ss_map = {s["name"]: s for s in bazi_analysis.get("shi_shen_detail", [])}
    day_wx = bazi.day_wx
    gender = bazi.gender
    hour_zhi = bazi.hour_zhi
    hour_gan = bazi.hour_gan
    details, advice = [], []

    ss = ss_map.get("食神", {})
    sg = ss_map.get("伤官", {})

    if gender == "female":
        if ss and sg:
            details.append("食神伤官皆有，子女双全之象")
        elif ss:
            details.append(f"食神{'旺' if ss.get('count',0)>=2 else '现'}于命局，子女缘佳")
        elif sg:
            details.append(f"伤官{'旺' if sg.get('count',0)>=2 else '现'}于命局，子女聪明有才但个性较强")
        else:
            details.append("食伤不显，子女缘分较浅或有领养之象")
    else:
        zg = ss_map.get("正官", {})
        qs = ss_map.get("七杀", {})
        if zg:
            details.append("正官现于命局，子女正派有出息")
        if qs:
            details.append("七杀现于命局，子女有个性有魄力")
        if not zg and not qs:
            details.append("官杀不显，子女缘分较晚")

    hour_zhi_wx = DI_ZHI_WX[hour_zhi]
    details.append(f"时柱{hour_gan}{hour_zhi}为子女宫，时支{hour_zhi}({hour_zhi_wx})决定子女运基储")
    if day_wx == hour_zhi_wx:
        details.append("时支为日主之根，子女与命主关系密切")
    elif hour_zhi_wx in _sheng_wo(day_wx):
        details.append("时支为印星，子女孝顺有学识")
    result["details"] = details
    result["advice"] = advice
    result["summary"] = details[0] if details else "子女运程平稳"
    return result


def analyze_children_ziwei(ziwei, ziwei_analysis):
    result = {"details": [], "advice": []}
    key_gongs = ziwei_analysis.get("key_gongs", {})
    si_hua = ziwei_analysis.get("si_hua_analysis", [])
    zn = key_gongs.get("子女", {})
    if zn:
        if zn.get("kong"):
            result["details"].append("子女宫无主星，子女缘较浅或晚得子")
        else:
            sd = _star_children_desc(zn.get("main_stars", []))
            if sd:
                result["details"].append(sd)
    for sh in si_hua:
        if sh.get("gong") == "子女":
            result["details"].append(sh.get("interpretation", ""))
    return result


# ============================================================
# 5. 健康分析
# ============================================================

def analyze_health_bazi(bazi, bazi_analysis):
    result = {
        "title": "健康分析", "icon": "🏥", "color": "#FF3131",
        "summary": "", "details": [], "advice": [], "weak_organs": [],
    }
    wu_xing = bazi.wu_xing
    strength = bazi_analysis.get("strength", {})
    xi_yong = bazi_analysis.get("xi_yong_shen", {})
    ji_detail = bazi_analysis.get("ji_shen_detail", {})
    day_zhi = bazi.day_zhi
    day_zhi_wx = DI_ZHI_WX[day_zhi]
    wx_organ = {
        "金": "肺、呼吸道、皮肤、大肠", "木": "肝胆、筋骨、神经系统",
        "水": "肾、膀胱、泌尿系统、耳朵", "火": "心脏、血液、眼睛、小肠",
        "土": "脾胃、肌肉、消化系统",
    }
    details, advice, weak_organs = [], [], []

    for wx, cnt in wu_xing.items():
        if cnt >= 4:
            organ = wx_organ.get(wx, "")
            details.append(f"{wx}过旺（{cnt}），需注意{organ}相关健康问题")
            weak_organs.append(f"{wx}→{organ}")
            advice.append(f"适度运动排解{organ}方面的压力")
        elif cnt == 0:
            organ = wx_organ.get(wx, "")
            details.append(f"{wx}缺失，{organ}功能偏弱，需加强保养")
            weak_organs.append(f"{wx}→{organ}")
            advice.append(f"通过饮食和生活习惯补充{organ}所需的营养")

    level = strength.get("level", "")
    if level in ("弱", "偏弱"):
        details.append("日主偏弱，体质容易疲劳，需注意休息和营养")
        advice.append("保持规律作息，适当锻炼增强体质")
    elif level in ("旺", "偏旺"):
        details.append("日主旺相，体质较强，但需防过度消耗")
    if day_zhi_wx != bazi.day_wx:
        organ = wx_organ.get(day_zhi_wx, "")
        details.append(f"日支{day_zhi_wx}与日主{bazi.day_wx}不同，需留意{organ}")
    if ji_detail and ji_detail.get("ji_shen_list"):
        for js in ji_detail.get("ji_shen_list", []):
            if js.get("health_impact"):
                details.append(f"忌神健康提示：{js['health_impact']}")
    if xi_yong.get("first_yong_shen"):
        wx_h = _wx_health_advice(xi_yong["first_yong_shen"])
        if wx_h:
            advice.append(wx_h)
    result["details"] = details
    result["advice"] = advice
    result["weak_organs"] = weak_organs
    result["summary"] = details[0] if details else "整体健康状况良好，需注意日常保养"
    return result


def analyze_health_ziwei(ziwei, ziwei_analysis):
    result = {"details": [], "advice": []}
    key_gongs = ziwei_analysis.get("key_gongs", {})
    si_hua = ziwei_analysis.get("si_hua_analysis", [])
    jie = key_gongs.get("疾厄", {})
    if jie:
        if jie.get("kong"):
            result["details"].append("疾厄宫无主星，先天体质较好，大病不侵")
        else:
            sd = _star_health_desc(jie.get("main_stars", []))
            if sd:
                result["details"].append(sd)
    for sh in si_hua:
        if sh.get("gong") == "疾厄":
            result["details"].append(sh.get("interpretation", ""))
            if sh.get("transform") == "化忌":
                result["details"].append("化忌入疾厄宫，需特别关注身体健康，定期体检")
                result["advice"].append("建立定期体检习惯，防患于未然")
    return result


# ============================================================
# 综合整合
# ============================================================

def full_combined_analysis(bazi, bazi_analysis, ziwei, ziwei_analysis):
    """综合八字和紫微斗数，按生活维度输出完整分析。
    八字视角与紫微视角分开陈列，两者体系不同、分析内容不同。"""
    aspects = {}

    marriage_bazi = analyze_marriage_bazi(bazi, bazi_analysis)
    marriage_zw = analyze_marriage_ziwei(ziwei, ziwei_analysis)
    aspects["marriage"] = {
        "title": "婚姻情感", "icon": "💑", "color": "#FF6B9D",
        "summary": marriage_bazi.get("summary", ""),
        "bazi": {"label": "八字视角", "details": marriage_bazi.get("details", []), "advice": marriage_bazi.get("advice", [])},
        "ziwei": {"label": "紫微斗数视角", "details": marriage_zw.get("details", []), "advice": marriage_zw.get("advice", [])},
    }

    career_bazi = analyze_career_bazi(bazi, bazi_analysis)
    career_zw = analyze_career_ziwei(ziwei, ziwei_analysis)
    aspects["career"] = {
        "title": "事业运势", "icon": "💼", "color": "#00E5FF",
        "summary": career_bazi.get("summary", ""),
        "suitable_careers": career_bazi.get("suitable_careers", []),
        "bazi": {"label": "八字视角", "details": career_bazi.get("details", []), "advice": career_bazi.get("advice", [])},
        "ziwei": {"label": "紫微斗数视角", "details": career_zw.get("details", []), "advice": career_zw.get("advice", [])},
    }

    wealth_bazi = analyze_wealth_bazi(bazi, bazi_analysis)
    wealth_zw = analyze_wealth_ziwei(ziwei, ziwei_analysis)
    aspects["wealth"] = {
        "title": "财运财富", "icon": "💰", "color": "#FFC107",
        "summary": wealth_bazi.get("summary", ""),
        "wealth_traits": wealth_bazi.get("wealth_traits", []),
        "bazi": {"label": "八字视角", "details": wealth_bazi.get("details", []), "advice": wealth_bazi.get("advice", [])},
        "ziwei": {"label": "紫微斗数视角", "details": wealth_zw.get("details", []), "advice": wealth_zw.get("advice", [])},
    }

    children_bazi = analyze_children_bazi(bazi, bazi_analysis)
    children_zw = analyze_children_ziwei(ziwei, ziwei_analysis)
    aspects["children"] = {
        "title": "子女运程", "icon": "👶", "color": "#00FF41",
        "summary": children_bazi.get("summary", ""),
        "bazi": {"label": "八字视角", "details": children_bazi.get("details", []), "advice": children_bazi.get("advice", [])},
        "ziwei": {"label": "紫微斗数视角", "details": children_zw.get("details", []), "advice": children_zw.get("advice", [])},
    }

    health_bazi = analyze_health_bazi(bazi, bazi_analysis)
    health_zw = analyze_health_ziwei(ziwei, ziwei_analysis)
    aspects["health"] = {
        "title": "健康分析", "icon": "🏥", "color": "#FF3131",
        "summary": health_bazi.get("summary", ""),
        "weak_organs": health_bazi.get("weak_organs", []),
        "bazi": {"label": "八字视角", "details": health_bazi.get("details", []), "advice": health_bazi.get("advice", [])},
        "ziwei": {"label": "紫微斗数视角", "details": health_zw.get("details", []), "advice": health_zw.get("advice", [])},
    }

    return aspects


def format_combined_analysis(aspects):
    """将综合分析格式化为可读文本，八字与紫微分开展示。"""
    lines = []
    lines.append("")
    lines.append("=" * 60)
    lines.append("              命理综合解读 · 生活维度分析")
    lines.append("   八字体系（天干地支·十神·五行） ≠ 紫微体系（星曜·宫位·四化）")
    lines.append("=" * 60)

    for key, aspect in aspects.items():
        if not aspect:
            continue
        icon = aspect.get("icon", "")
        title = aspect.get("title", key)
        lines.append(f"\n{icon} 【{title}】")
        lines.append("=" * 40)

        summary = aspect.get("summary", "")
        if summary:
            lines.append(f"  ▶ 概述：{summary}")

        bazi = aspect.get("bazi", {})
        if bazi:
            lines.append(f"\n  ┌─ 🪐 {bazi.get('label', '八字视角')} ─┐")
            for d in bazi.get("details", []):
                lines.append(f"  │ · {d}")
            for a in bazi.get("advice", []):
                lines.append(f"  │ 💡 {a}")
            lines.append("  └" + "─" * 30 + "┘")

        ziwei = aspect.get("ziwei", {})
        if ziwei:
            lines.append(f"\n  ┌─ ✨ {ziwei.get('label', '紫微斗数视角')} ─┐")
            for d in ziwei.get("details", []):
                lines.append(f"  │ · {d}")
            for a in ziwei.get("advice", []):
                lines.append(f"  │ 💡 {a}")
            lines.append("  └" + "─" * 30 + "┘")

        careers = aspect.get("suitable_careers", [])
        if careers:
            lines.append(f"\n  适合行业：{'、'.join(careers)}")
        traits = aspect.get("wealth_traits", [])
        if traits:
            lines.append(f"  财富特质：{'、'.join(traits)}")
        organs = aspect.get("weak_organs", [])
        if organs:
            lines.append("  需关注器官：")
            for wo in organs:
                lines.append(f"    ⚠ {wo}")

    lines.append("")
    lines.append("=" * 60)
    lines.append("⚠ 以上分析仅供参考，命运掌握在自己手中")
    lines.append("  八字与紫微是两个独立体系，分析方法和角度不同，可互为印证")
    return "\n".join(lines)


# ============================================================
# 星曜解读
# ============================================================

def _star_marriage_desc(stars):
    m = {
        "紫微":"夫妻宫有紫微，配偶有领导气质，家庭地位较高，婚姻需互相尊重",
        "天机":"夫妻宫有天机，配偶聪明灵活，但感情中可能多变，需增进沟通",
        "太阳":"夫妻宫有太阳，配偶热情开朗，社交能力强，婚姻充满活力",
        "武曲":"夫妻宫有武曲，配偶务实刚强，婚姻重视物质基础",
        "天同":"夫妻宫有天同，配偶温柔体贴，婚姻和谐美满",
        "廉贞":"夫妻宫有廉贞，感情浓烈但需防情绪波动",
        "天府":"夫妻宫有天府，配偶稳重可靠，婚姻稳定有依靠",
        "太阴":"夫妻宫有太阴，配偶温柔细腻，感情细腻深沉",
        "贪狼":"夫妻宫有贪狼，配偶有魅力但桃花多，需互相信任",
        "巨门":"夫妻宫有巨门，沟通中需注意口舌是非",
        "天相":"夫妻宫有天相，配偶正直善良，婚姻和谐",
        "天梁":"夫妻宫有天梁，配偶有长者风范，婚姻有依靠",
        "七杀":"夫妻宫有七杀，感情中较强势，需彼此包容",
        "破军":"夫妻宫有破军，婚姻有波折变动，需坚定信念",
    }
    for s in stars:
        if s in m: return m[s]
    return None

def _star_career_desc(stars):
    m = {
        "紫微":"官禄宫有紫微，事业心强，有领导才能和权威潜质，适合高位管理",
        "天机":"官禄宫有天机，适合策划、咨询、技术等需要脑力的工作",
        "太阳":"官禄宫有太阳，事业光明磊落，适合公众事业或能源行业",
        "武曲":"官禄宫有武曲，适合金融、财务、军警等需要刚毅果决的行业",
        "天同":"官禄宫有天同，适合服务业、文教等温和型行业",
        "廉贞":"官禄宫有廉贞，事业有魄力但需防纷争",
        "天府":"官禄宫有天府，适合稳定型事业，如大型企业管理",
        "太阴":"官禄宫有太阴，适合文化艺术、女性相关行业",
        "贪狼":"官禄宫有贪狼，适合交际、娱乐、创意类行业",
        "巨门":"官禄宫有巨门，适合法律、咨询、销售等口才行业",
        "天相":"官禄宫有天相，适合行政、协调、服务类工作",
        "天梁":"官禄宫有天梁，适合教育、医疗、公益事业",
        "七杀":"官禄宫有七杀，事业上有冲劲，适合创业或竞争性行业",
        "破军":"官禄宫有破军，事业多变，适合创新或开拓型工作",
    }
    for s in stars:
        if s in m: return m[s]
    return None

def _star_wealth_desc(stars):
    m = {
        "武曲":"财帛宫有武曲，财运旺盛，擅长理财，是财星入财宫的上佳格局",
        "太阴":"财帛宫有太阴，财源稳定细水长流，适合长期投资",
        "天府":"财帛宫有天府，财库丰厚，善于守财理财",
        "紫微":"财帛宫有紫微，有贵人助财，权力生财",
        "贪狼":"财帛宫有贪狼，偏财运佳但需节制消费",
        "廉贞":"财帛宫有廉贞，财运波动较大，需谨慎投资",
        "天同":"财帛宫有天同，知足常乐，财运随缘",
        "巨门":"财帛宫有巨门，靠口才和沟通赚钱，财源与社交相关",
        "破军":"财帛宫有破军，财来财去，需做好财务规划",
    }
    for s in stars:
        if s in m: return m[s]
    return None

def _star_children_desc(stars):
    m = {
        "紫微":"子女宫有紫微，子女有领导才能，优秀有作为",
        "天机":"子女宫有天机，子女聪明好学，多才多艺",
        "太阳":"子女宫有太阳，子女热情开朗，有事业心",
        "武曲":"子女宫有武曲，子女性格刚强独立",
        "天同":"子女宫有天同，子女乖巧可爱，亲子关系和谐",
        "廉贞":"子女宫有廉贞，子女个性鲜明，需注意引导",
        "天府":"子女宫有天府，子女稳重可靠，家庭和睦",
        "太阴":"子女宫有太阴，子女温柔体贴，尤其女儿缘好",
        "贪狼":"子女宫有贪狼，子女人缘好，活泼外向",
        "七杀":"子女宫有七杀，子女性格刚烈有主见",
        "破军":"子女宫有破军，养育过程中多变动，但子女有个性",
    }
    for s in stars:
        if s in m: return m[s]
    return None

def _star_health_desc(stars):
    m = {
        "太阳":"疾厄宫有太阳，需注意心脏、眼睛和血液循环",
        "太阴":"疾厄宫有太阴，需注意肾脏、泌尿系统和情绪",
        "武曲":"疾厄宫有武曲，需注意呼吸系统和骨骼关节",
        "贪狼":"疾厄宫有贪狼，需注意肝脏和内分泌系统",
        "巨门":"疾厄宫有巨门，需注意消化系统和口腔",
        "天同":"疾厄宫有天同，先天体质较好，大病不侵",
        "天梁":"疾厄宫有天梁，虽有病痛但总能逢凶化吉",
        "七杀":"疾厄宫有七杀，需注意意外伤害，多加小心",
        "破军":"疾厄宫有破军，身体状况易波动，需规律作息",
        "廉贞":"疾厄宫有廉贞，需注意血液和免疫系统",
    }
    for s in stars:
        if s in m: return m[s]
    return None

def _gong_impact_desc(gong_name):
    d = {"官禄":"事业发展有深远影响","财帛":"财富获取方式有重要关联","田宅":"家庭生活和财产积累有影响","父母":"原生家庭有引导作用","福德":"精神层面有深刻共鸣"}
    return d.get(gong_name, "有影响")


# ============================================================
# 五行生活建议
# ============================================================

def _wx_marriage_advice(wx):
    m = {"金":"选择西方或从事金融、法律行业的伴侣更有利","木":"选择东方或从事教育、文职的伴侣更和谐","水":"选择北方或从事贸易、传媒的伴侣更互补","火":"选择南方或从事能源、演艺的伴侣更有激情","土":"选择中西部或从事房地产、建筑的伴侣更稳定"}
    return m.get(wx, "")

def _wx_career_advice(wx):
    m = {"金":["金融","法律","机械","汽车","珠宝"],"木":["教育","文化","出版","医药","环保"],"水":["贸易","物流","传媒","通讯","旅游"],"火":["餐饮","能源","互联网","电子","演艺"],"土":["房地产","建筑","农业","矿产","仓储"]}
    return m.get(wx, [])

def _wx_wealth_advice(wx):
    m = {"金":"适合投资贵金属、金融产品，佩戴金属饰品有助于财运","木":"绿色产业、文化教育投资前景好，绿植有助财运","水":"流动性强的投资方式更合适，养鱼有助财气","火":"热门行业、互联网投资机会多，保持热情能吸引财富","土":"不动产投资为佳，稳健型理财更适合"}
    return m.get(wx, "")

def _wx_health_advice(wx):
    m = {"金":"多补充矿物质，呼吸新鲜空气，适当练习深呼吸","木":"多吃绿色蔬菜，多做伸展运动，亲近大自然","水":"保持充足饮水，游泳有益健康，注意保暖","火":"适度晒太阳，保持心情愉悦，避免过度劳累","土":"注意饮食规律养脾胃，可练习太极等温和运动"}
    return m.get(wx, "")

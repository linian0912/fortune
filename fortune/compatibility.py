# -*- coding: utf-8 -*-
"""合婚配对分析模块：基于八字和紫微斗数的合婚指数。"""

from .core import TIAN_GAN_WX, DI_ZHI_WX, TIAN_GAN, DI_ZHI

# 天干五合
GAN_HE = {('甲','己'),('乙','庚'),('丙','辛'),('丁','壬'),('戊','癸')}

# 地支六合
ZHI_HE = {('子','丑'),('寅','亥'),('卯','戌'),('辰','酉'),('巳','申'),('午','未')}

# 地支三合
ZHI_SAN_HE = [
    ('申','子','辰'), ('亥','卯','未'), ('寅','午','戌'), ('巳','酉','丑'),
]

# 地支六冲
ZHI_CHONG = {('子','午'),('丑','未'),('寅','申'),('卯','酉'),('辰','戌'),('巳','亥')}

# 五行相生相克
WX_SHENG = {"金":"水","水":"木","木":"火","火":"土","土":"金"}
WX_KE = {"金":"木","木":"土","土":"水","水":"火","火":"金"}

# 生肖配对
SHENG_XIAO_HE = {
    ('鼠','牛'):"六合·上等婚配", ('虎','猪'):"六合·上等婚配",
    ('兔','狗'):"六合·上等婚配", ('龙','鸡'):"六合·上等婚配",
    ('蛇','猴'):"六合·上等婚配", ('马','羊'):"六合·上等婚配",
    ('鼠','龙'):"三合·佳配", ('鼠','猴'):"三合·佳配",
    ('牛','蛇'):"三合·佳配", ('牛','鸡'):"三合·佳配",
    ('虎','马'):"三合·佳配", ('虎','狗'):"三合·佳配",
    ('兔','羊'):"三合·佳配", ('兔','猪'):"三合·佳配",
    ('龙','鼠'):"三合·佳配", ('龙','猴'):"三合·佳配",
    ('蛇','鸡'):"三合·佳配", ('蛇','牛'):"三合·佳配",
    ('马','狗'):"三合·佳配", ('马','虎'):"三合·佳配",
    ('羊','猪'):"三合·佳配", ('羊','兔'):"三合·佳配",
    ('猴','鼠'):"三合·佳配", ('猴','龙'):"三合·佳配",
    ('鸡','牛'):"三合·佳配", ('鸡','蛇'):"三合·佳配",
    ('狗','虎'):"三合·佳配", ('狗','马'):"三合·佳配",
    ('猪','兔'):"三合·佳配", ('猪','羊'):"三合·佳配",
}

SHENG_XIAO_CHONG = {
    ('鼠','马'):"六冲·需谨慎", ('牛','羊'):"六冲·需谨慎",
    ('虎','猴'):"六冲·需谨慎", ('兔','鸡'):"六冲·需谨慎",
    ('龙','狗'):"六冲·需谨慎", ('蛇','猪'):"六冲·需谨慎",
}


def analyze_compatibility(bazi1, bazi2, ziwei1, ziwei2):
    """
    分析两人合婚指数。
    返回评分和详细分析。
    """
    score = 50
    details = []

    # 1. 日干五行关系（核心）
    wx1 = TIAN_GAN_WX[bazi1.day_gan]
    wx2 = TIAN_GAN_WX[bazi2.day_gan]

    if wx1 == wx2:
        score += 10
        details.append({"aspect": "日主同气", "score": "+10", "desc": f"两人日主同为{wx1}，性格相似，志趣相投。", "color": "#00FF41"})
    elif WX_SHENG.get(wx1) == wx2:
        score += 12
        details.append({"aspect": "日主相生", "score": "+12", "desc": f"你的{wx1}生对方的{wx2}，你能滋养对方，关系和谐。", "color": "#00FF41"})
    elif WX_SHENG.get(wx2) == wx1:
        score += 8
        details.append({"aspect": "日主受生", "score": "+8", "desc": f"对方的{wx2}生你的{wx1}，对方能滋养你，被爱被呵护。", "color": "#00E5FF"})
    elif WX_KE.get(wx1) == wx2:
        score -= 5
        details.append({"aspect": "日主被克", "score": "-5", "desc": f"对方的{wx2}克你的{wx1}，需注意相处中的约束感。", "color": "#FF3131"})
    elif WX_KE.get(wx2) == wx1:
        score += 3
        details.append({"aspect": "日主克对方", "score": "+3", "desc": f"你的{wx1}克对方的{wx2}，你在关系中占主导地位。", "color": "#FFC107"})

    # 2. 天干五合
    gan_pair = (bazi1.day_gan, bazi2.day_gan)
    if gan_pair in GAN_HE or (gan_pair[1], gan_pair[0]) in GAN_HE:
        score += 15
        details.append({"aspect": "日干五合", "score": "+15", "desc": "天作之合！两人日干为天干五合，缘分深厚，是前世注定的伴侣。", "color": "#FF3131"})

    # 3. 地支关系
    zhi_pair = (bazi1.day_zhi, bazi2.day_zhi)
    if zhi_pair in ZHI_HE or (zhi_pair[1], zhi_pair[0]) in ZHI_HE:
        score += 10
        details.append({"aspect": "日支六合", "score": "+10", "desc": "两人日支为地支六合，生活默契度高。", "color": "#00FF41"})
    elif zhi_pair in ZHI_CHONG or (zhi_pair[1], zhi_pair[0]) in ZHI_CHONG:
        score -= 8
        details.append({"aspect": "日支六冲", "score": "-8", "desc": "两人日支相冲，生活中容易产生摩擦，需要更多包容。", "color": "#FF3131"})
    else:
        # Check 三合
        for trio in ZHI_SAN_HE:
            if bazi1.day_zhi in trio and bazi2.day_zhi in trio:
                score += 8
                details.append({"aspect": "日支三合", "score": "+8", "desc": "两人日支为三合局，价值观相近，相处愉快。", "color": "#00E5FF"})
                break

    # 4. 生肖配对
    shengxiao1 = bazi1.sheng_xiao
    shengxiao2 = bazi2.sheng_xiao
    sx_pair = (shengxiao1, shengxiao2)
    sx_rev = (shengxiao2, shengxiao1)

    if sx_pair in SHENG_XIAO_HE:
        val = SHENG_XIAO_HE[sx_pair]
        score += 10
        details.append({"aspect": f"生肖{val}", "score": "+10", "desc": f"生肖{shengxiao1}与{shengxiao2}相合，缘分深厚。", "color": "#00FF41"})
    elif sx_rev in SHENG_XIAO_HE:
        val = SHENG_XIAO_HE[sx_rev]
        score += 10
        details.append({"aspect": f"生肖{val}", "score": "+10", "desc": f"生肖{shengxiao1}与{shengxiao2}相合，缘分深厚。", "color": "#00FF41"})
    elif sx_pair in SHENG_XIAO_CHONG:
        val = SHENG_XIAO_CHONG[sx_pair]
        score -= 10
        details.append({"aspect": f"生肖{val}", "score": "-10", "desc": f"生肖{shengxiao1}与{shengxiao2}相冲，性格差异大。", "color": "#FF3131"})

    # 5. 紫微夫妻宫互看
    if ziwei1 and ziwei2:
        fuqi1_stars = _get_gong_main_stars(ziwei1, "夫妻")
        fuqi2_stars = _get_gong_main_stars(ziwei2, "夫妻")

        # 夫妻宫有吉星
        good_stars = {"紫微","天府","天相","天同","太阴"}
        for s in fuqi1_stars:
            if s in good_stars:
                score += 5
                details.append({"aspect": "夫妻宫吉星", "score": "+5", "desc": f"你的夫妻宫有{s}，婚姻运势不错。", "color": "#00E5FF"})
        for s in fuqi2_stars:
            if s in good_stars:
                score += 5
                details.append({"aspect": "对方夫妻宫吉星", "score": "+5", "desc": f"对方的夫妻宫有{s}，婚姻运势不错。", "color": "#00E5FF"})

        # 共同吉星
        common = set(fuqi1_stars) & set(fuqi2_stars) & MAIN_STARS
        if common:
            score += 5
            details.append({"aspect": "夫妻宫同星", "score": "+5", "desc": f"双方夫妻宫均有{'、'.join(common)}，缘分奇妙。", "color": "#FFC107"})

    # 综合评级
    score = max(20, min(98, score))
    if score >= 80:
        level = "天作之合"
        summary = "两人缘分深厚，是天造地设的一对，婚姻幸福美满。"
    elif score >= 65:
        level = "佳偶良缘"
        summary = "两人相配度较高，婚后相互扶持，家庭和睦。"
    elif score >= 50:
        level = "中平姻缘"
        summary = "两人有一定缘分，但需互相包容和理解，婚姻可成。"
    elif score >= 35:
        level = "需多磨合"
        summary = "两人性格差异较大，需要更多时间和耐心来适应对方。"
    else:
        level = "挑战较大"
        summary = "两人缘分较浅，若要结合需要双方付出极大的努力和包容。"

    return {
        "score": score,
        "level": level,
        "summary": summary,
        "details": details,
        "person1": {"sheng_xiao": shengxiao1, "day_gan": bazi1.day_gan, "day_zhi": bazi1.day_zhi, "day_wx": TIAN_GAN_WX[bazi1.day_gan]},
        "person2": {"sheng_xiao": shengxiao2, "day_gan": bazi2.day_gan, "day_zhi": bazi2.day_zhi, "day_wx": TIAN_GAN_WX[bazi2.day_gan]},
    }


MAIN_STARS = {"紫微","天机","太阳","武曲","天同","廉贞","天府","太阴","贪狼","巨门","天相","天梁","七杀","破军"}

def _get_gong_main_stars(ziwei, gong_name):
    for g in ziwei.gongs:
        if g["name"] == gong_name:
            return [s_name for s_name, p in g["stars"] if s_name in MAIN_STARS]
    return []

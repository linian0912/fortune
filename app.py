#!/usr/bin/env python3
"""命理推算 WSGI 应用 —— 生产部署入口"""

import json, os, sys
from urllib.parse import parse_qs

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from fortune.bazi import Bazi
from fortune.ziwei import Ziwei
from fortune.core import DI_ZHI_CANG_GAN, TIAN_GAN_WX, DI_ZHI_WX
from fortune.bazi_analysis import full_bazi_analysis
from fortune.ziwei_analysis import full_ziwei_analysis
from fortune.combined_analysis import full_combined_analysis
from fortune.personality import analyze_personality

HTML_PATH = os.path.join(BASE, "index.html")
with open(HTML_PATH, "r", encoding="utf-8") as f:
    INDEX_HTML = f.read().encode("utf-8")


def calc_fortune(year, month, day, hour, gender, lunar):
    result = {}
    try:
        b = Bazi(year, month, day, hour, gender, lunar)
        result["bazi"] = {
            "pillars": {"year": b.year_gan_zhi, "month": b.month_gan_zhi, "day": b.day_gan_zhi, "hour": b.hour_gan_zhi},
            "shi_shen": b.shi_shen, "wu_xing": b.wu_xing, "day_wx": b.day_wx,
            "na_yin": b.na_yin, "sheng_xiao": b.sheng_xiao,
            "lunar_date": f"{b.lunar_date[0]}年{b.lunar_date[1]}月{b.lunar_date[2]}日",
            "day_master": f"{b.day_gan}({b.day_wx})", "tai_yuan": b.tai_yuan, "ming_gong": b.ming_gong, "shen_gong": b.shen_gong,
            "shen_sha": b.shen_sha,
            "xun_kong": b.xun_kong,
            "chang_sheng": b.chang_sheng,
            "di_zhi_shi_shen": b.di_zhi_shi_shen,
            "pillar_shen_sha": b.pillar_shen_sha,
            "year_gan_wx": f"{b.year_gan}({TIAN_GAN_WX[b.year_gan]})",
            "month_gan_wx": f"{b.month_gan}({TIAN_GAN_WX[b.month_gan]})",
            "day_gan_wx": f"{b.day_gan}({TIAN_GAN_WX[b.day_gan]})",
            "hour_gan_wx": f"{b.hour_gan}({TIAN_GAN_WX[b.hour_gan]})",
            "year_zhi_wx": f"{b.year_zhi}({DI_ZHI_WX[b.year_zhi]})",
            "month_zhi_wx": f"{b.month_zhi}({DI_ZHI_WX[b.month_zhi]})",
            "day_zhi_wx": f"{b.day_zhi}({DI_ZHI_WX[b.day_zhi]})",
            "hour_zhi_wx": f"{b.hour_zhi}({DI_ZHI_WX[b.hour_zhi]})",
            "year_cang": ', '.join([f"{g}({TIAN_GAN_WX[g]})" for g in DI_ZHI_CANG_GAN.get(b.year_zhi, [])]),
            "month_cang": ', '.join([f"{g}({TIAN_GAN_WX[g]})" for g in DI_ZHI_CANG_GAN.get(b.month_zhi, [])]),
            "day_cang": ', '.join([f"{g}({TIAN_GAN_WX[g]})" for g in DI_ZHI_CANG_GAN.get(b.day_zhi, [])]),
            "hour_cang": ', '.join([f"{g}({TIAN_GAN_WX[g]})" for g in DI_ZHI_CANG_GAN.get(b.hour_zhi, [])]),
            "da_yun": [{"gz": gz, "age": age} for gz, age in b.da_yun[:8]],
            "cang_gan_detail": {
                "年支" + b.year_zhi: DI_ZHI_CANG_GAN.get(b.year_zhi, []),
                "月支" + b.month_zhi: DI_ZHI_CANG_GAN.get(b.month_zhi, []),
                "日支" + b.day_zhi: DI_ZHI_CANG_GAN.get(b.day_zhi, []),
                "时支" + b.hour_zhi: DI_ZHI_CANG_GAN.get(b.hour_zhi, []),
            },
        }
        try:
            result["bazi_analysis"] = full_bazi_analysis(b)
        except Exception:
            result["bazi_analysis"] = {"error": "analysis failed"}
    except Exception as e:
        result["bazi"] = {"error": str(e)}
    try:
        z = Ziwei(year, month, day, hour, gender, lunar)
        gong_data = []
        for g in z.gongs:
            stars = []
            for s_name, prefix in g["stars"]:
                stars.append(f"{prefix}{s_name}" if prefix else s_name)
            gong_data.append({
                "name": g["name"], "zhi": g["zhi"], "gz": g["gz"],
                "stars": stars, "is_ming": g["is_ming"], "is_shen": g["is_shen"],
            })
        result["ziwei"] = {
            "ming_gong": z.ming_gan_zhi, "shen_gong_name": z.shen_gong_name,
            "wx_ju": f"{z.wx_ju_name}({z.wx_ju}局)", "si_hua": z.si_hua,
            "gongs": gong_data,
        }
        try:
            result["ziwei_analysis"] = full_ziwei_analysis(z)
        except Exception:
            result["ziwei_analysis"] = {"error": "analysis failed"}
    except Exception as e:
        result["ziwei"] = {"error": str(e)}
    try:
        if "bazi" in result and "ziwei" in result and \
           "error" not in result.get("bazi", {}) and "error" not in result.get("ziwei", {}):
            b = Bazi(year, month, day, hour, gender, lunar)
            z = Ziwei(year, month, day, hour, gender, lunar)
            ba = result.get("bazi_analysis", {})
            za = result.get("ziwei_analysis", {})
            if "error" not in ba and "error" not in za:
                result["combined_analysis"] = full_combined_analysis(b, ba, z, za)
    except Exception:
        result["combined_analysis"] = {"error": "combined analysis failed"}
    try:
        if "bazi_analysis" in result and "ziwei_analysis" in result:
            ba = result.get("bazi_analysis", {})
            za = result.get("ziwei_analysis", {})
            if "error" not in ba and "error" not in za:
                b = Bazi(year, month, day, hour, gender, lunar)
                result["personality"] = analyze_personality(b, ba, za)
    except Exception:
        result["personality"] = {"error": "personality analysis failed"}
    return result


def application(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET")

    if method == "GET" and (path in {"/", "/index.html", "/bazi", "/ziwei", "/hehun"}):
        start_response("200 OK", [
            ("Content-Type", "text/html; charset=utf-8"),
            ("Content-Length", str(len(INDEX_HTML))),
        ])
        return [INDEX_HTML]

    if method == "POST" and path == "/api/fortune":
        try:
            length = int(environ.get("CONTENT_LENGTH", 0))
            body = environ["wsgi.input"].read(length).decode("utf-8")
            params = parse_qs(body)
            year = int(params.get("year", [0])[0])
            month = int(params.get("month", [0])[0])
            day = int(params.get("day", [0])[0])
            hour = int(params.get("hour", [12])[0])
            gender = params.get("gender", ["male"])[0]
            lunar = params.get("lunar", ["false"])[0] == "true"
            result = calc_fortune(year, month, day, hour, gender, lunar)
            resp = json.dumps(result, ensure_ascii=False).encode("utf-8")
            start_response("200 OK", [
                ("Content-Type", "application/json; charset=utf-8"),
                ("Content-Length", str(len(resp))),
            ])
            return [resp]
        except Exception as e:
            resp = json.dumps({"error": str(e)}, ensure_ascii=False).encode("utf-8")
            start_response("500 Internal Server Error", [
                ("Content-Type", "application/json; charset=utf-8"),
                ("Content-Length", str(len(resp))),
            ])
            return [resp]

    start_response("404 Not Found", [("Content-Type", "text/plain")])
    return [b"Not Found"]

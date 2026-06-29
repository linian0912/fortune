#!/usr/bin/env python3
"""命理推算 Web 服务 —— 启动后访问 http://localhost:8888"""
import json, os, sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
PORT = 8888
BASE = os.path.dirname(os.path.abspath(__file__))

from fortune.bazi import Bazi
from fortune.ziwei import Ziwei
from fortune.core import DI_ZHI_CANG_GAN

def calc_fortune(year, month, day, hour, gender, lunar):
    result = {}
    try:
        b = Bazi(year, month, day, hour, gender, lunar)
        result["bazi"] = {
            "pillars": {"year": b.year_gan_zhi, "month": b.month_gan_zhi, "day": b.day_gan_zhi, "hour": b.hour_gan_zhi},
            "shi_shen": b.shi_shen, "wu_xing": b.wu_xing, "day_wx": b.day_wx,
            "na_yin": b.na_yin, "sheng_xiao": b.sheng_xiao,
            "lunar_date": f"{b.lunar_date[0]}年{b.lunar_date[1]}月{b.lunar_date[2]}日",
            "day_master": f"{b.day_gan}({b.day_wx})",
            "da_yun": [{"gz": gz, "age": age} for gz, age in b.da_yun[:8]],
            "cang_gan_detail": {
                "年支" + b.year_zhi: DI_ZHI_CANG_GAN.get(b.year_zhi, []),
                "月支" + b.month_zhi: DI_ZHI_CANG_GAN.get(b.month_zhi, []),
                "日支" + b.day_zhi: DI_ZHI_CANG_GAN.get(b.day_zhi, []),
                "时支" + b.hour_zhi: DI_ZHI_CANG_GAN.get(b.hour_zhi, []),
            },
        }
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
    except Exception as e:
        result["ziwei"] = {"error": str(e)}
    return result


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            try:
                with open(os.path.join(BASE, "index.html"), "rb") as f:
                    data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", len(data))
                self.end_headers()
                self.wfile.write(data)
            except Exception as e:
                self.send_error(500, str(e))
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/api/fortune":
            try:
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length).decode("utf-8")
                params = parse_qs(body)
                year = int(params.get("year", [0])[0])
                month = int(params.get("month", [0])[0])
                day = int(params.get("day", [0])[0])
                hour = int(params.get("hour", [12])[0])
                gender = params.get("gender", ["male"])[0]
                lunar = params.get("lunar", ["false"])[0] == "true"
                result = calc_fortune(year, month, day, hour, gender, lunar)
                resp = json.dumps(result, ensure_ascii=False).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", len(resp))
                self.end_headers()
                self.wfile.write(resp)
            except Exception as e:
                self.send_error(500, str(e))
        else:
            self.send_error(404)

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    if not os.path.exists(os.path.join(BASE, "index.html")):
        print("错误: index.html 不存在")
        sys.exit(1)
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"\n{'='*50}")
    print(f"  命理推算系统已启动！")
    print(f"  打开浏览器访问: http://localhost:{PORT}")
    print(f"  按 Ctrl+C 停止")
    print(f"{'='*50}\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止。")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""命理推算 CLI 界面。支持命令行参数和交互式两种模式。"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def display_bazi(year, month, day, hour, gender, lunar):
    from fortune.bazi import Bazi
    bazi = Bazi(year, month, day, hour, gender, lunar)
    print(bazi.display())


def display_ziwei(year, month, day, hour, gender, lunar):
    from fortune.ziwei import Ziwei
    ziwei = Ziwei(year, month, day, hour, gender, lunar)
    print(ziwei.display_simple())


def parse_args():
    import argparse
    p = argparse.ArgumentParser(
        description="八字 + 紫微斗数 命理推算工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 -m fortune                                    # 交互式
  python3 -m fortune -y 1984 -m 2 -d 4 -H 8 --bazi      # 仅八字
  python3 -m fortune -y 1990 -m 5 -d 20 -H 14 --ziwei   # 仅紫微
  python3 -m fortune -y 2000 -m 1 -d 1 -H 12 -g f       # 女性
  python3 -m fortune --demo                              # 运行演示
        """
    )
    p.add_argument("-y", "--year", type=int, help="出生年份")
    p.add_argument("-m", "--month", type=int, help="出生月份")
    p.add_argument("-d", "--day", type=int, help="出生日期")
    p.add_argument("-H", "--hour", type=int, default=12, help="出生小时(0-23)，默认12")
    p.add_argument("-g", "--gender", choices=["m", "f"], default="m", help="性别 m=男 f=女 (默认m)")
    p.add_argument("-l", "--lunar", action="store_true", help="输入的日期为农历")
    p.add_argument("--bazi", action="store_true", help="仅显示八字")
    p.add_argument("--ziwei", action="store_true", help="仅显示紫微斗数")
    p.add_argument("--demo", action="store_true", help="运行演示案例")
    return p.parse_args()


def interactive_mode():
    print("\n" + "=" * 50)
    print("           八字 + 紫微斗数 命理推算")
    print("=" * 50)
    print()
    mode = input("日历类型 [1]公历 [2]农历 (默认1): ").strip()
    lunar = (mode == "2")
    try:
        year = int(input("出生年份: ").strip())
        month = int(input("出生月份: ").strip())
        day = int(input("出生日期: ").strip())
        hour = int(input("出生小时(0-23): ").strip())
        g = input("性别 [m]男 [f]女 (默认m): ").strip().lower()
        gender = "female" if g == "f" else "male"
    except ValueError:
        print("输入错误，请使用数字。")
        sys.exit(1)

    print()
    print("请选择排盘类型：")
    print("  [1] 四柱八字")
    print("  [2] 紫微斗数")
    print("  [3] 两者都看")
    choice = input("请选择 (默认3): ").strip() or "3"

    gender_str = "female" if gender == "f" else "male"
    if choice == "1":
        display_bazi(year, month, day, hour, gender_str, lunar)
    elif choice == "2":
        display_ziwei(year, month, day, hour, gender_str, lunar)
    else:
        display_bazi(year, month, day, hour, gender_str, lunar)
        display_ziwei(year, month, day, hour, gender_str, lunar)


def main():
    args = parse_args()

    if args.demo:
        from fortune.demo import cases
        from fortune.bazi import Bazi
        from fortune.ziwei import Ziwei
        for title, y, m, d, h, g in cases:
            print(f"\n{'='*60}")
            print(f"  {title}")
            print(f"{'='*60}")
            b = Bazi(y, m, d, h, g)
            print(b.display())
            z = Ziwei(y, m, d, h, g)
            print(z.display_simple())
        return

    if args.year is None:
        interactive_mode()
        return

    gender = "female" if args.gender == "f" else "male"
    show_bazi = not args.ziwei or (args.bazi and args.ziwei)
    show_ziwei = not args.bazi or (args.bazi and args.ziwei)
    if not args.bazi and not args.ziwei:
        show_bazi = show_ziwei = True

    if show_bazi:
        display_bazi(args.year, args.month, args.day, args.hour, gender, args.lunar)
    if show_ziwei:
        display_ziwei(args.year, args.month, args.day, args.hour, gender, args.lunar)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""演示：快速展示八字+紫微斗数排盘结果。"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fortune.bazi import Bazi
from fortune.ziwei import Ziwei

cases = [
    ("示例1: 1984-02-04 08:00 男", 1984, 2, 4, 8, "male"),
    ("示例2: 1990-05-20 14:00 女", 1990, 5, 20, 14, "female"),
    ("示例3: 2000-01-01 12:00 男", 2000, 1, 1, 12, "male"),
]

for title, y, m, d, h, g in cases:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    b = Bazi(y, m, d, h, g)
    print(b.display())
    print()
    z = Ziwei(y, m, d, h, g)
    print(z.display_simple())
    print()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
K线图绘制示例 - 使用kline_chart_generator.py
"""

import json
from kline_chart_generator import KLineChart

# ========== 方法1: 从JSON文件加载数据 ==========
# 假设你的数据保存在 data.json 文件中
# with open('data.json', 'r') as f:
#     data = json.load(f)

# ========== 方法2: 直接使用Python列表 ==========
# 示例数据（你的实际数据应该包含1000条）
data = [
    {"time": 1775302860000, "open": 67091.81, "high": 67104.55, 
     "low": 67091.81, "close": 67104.54, "volume": 2.701762},
    {"time": 1775302800000, "open": 67078.99, "high": 67093.35, 
     "low": 67078.98, "close": 67091.81, "volume": 1.298196},
    # ... 更多数据
]

# ========== 创建图表 ==========
# 可选风格: 'binance' (绿涨红跌), 'traditional' (红涨绿跌), 'dark' (暗黑)
chart = KLineChart(figsize=(18, 10), style='binance')

# 加载数据
df = chart.load_data(data)

# ========== 绘制并保存 ==========
chart.plot(
    df,
    title="BTC/USDT K-Line Chart",
    show_volume=True,                    # 显示成交量
    save_path="my_kline_chart.png",      # 保存路径（不设置则直接显示）
    ma_periods=[5, 10, 20, 60]          # 显示MA5, MA10, MA20, MA60
)

print("图表已生成！")

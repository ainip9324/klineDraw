#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
K-Line Chart Generator
高性能K线图绘制工具，支持1000+数据点
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import json
import sys
from typing import List, Dict, Union

class KLineChart:
    def __init__(self, figsize=(16, 10), style='binance'):
        """
        初始化K线图绘制器

        Parameters:
        -----------
        figsize : tuple
            图表尺寸 (宽, 高)
        style : str
            颜色风格 ('binance', 'traditional', 'dark')
        """
        self.figsize = figsize
        self.style = style
        self.colors = self._get_colors(style)

    def _get_colors(self, style):
        """获取颜色配置"""
        colors = {
            'binance': {
                'up': '#26a69a',      # 绿色
                'down': '#ef5350',    # 红色
                'bg': 'white',
                'grid': '#f0f0f0',
                'text': 'black'
            },
            'traditional': {
                'up': '#d32f2f',      # 红色（国内传统）
                'down': '#388e3c',    # 绿色
                'bg': 'white',
                'grid': '#f0f0f0',
                'text': 'black'
            },
            'dark': {
                'up': '#00c853',
                'down': '#ff5252',
                'bg': '#1a1a1a',
                'grid': '#333333',
                'text': 'white'
            }
        }
        return colors.get(style, colors['binance'])

    def load_data(self, data: Union[List[Dict], str]) -> pd.DataFrame:
        """
        加载数据

        Parameters:
        -----------
        data : list or str
            数据列表或JSON文件路径
            数据格式: [{"time": 1775302860000, "open": 67091.81, "high": 67104.55, 
                      "low": 67091.81, "close": 67104.54, "volume": 2.701762}, ...]
        """
        if isinstance(data, str):
            with open(data, 'r', encoding='utf-8') as f:
                data = json.load(f)

        df = pd.DataFrame(data)
        df['datetime'] = pd.to_datetime(df['time'], unit='ms')
        df = df.sort_values('datetime').reset_index(drop=True)

        # 数据验证
        required_cols = ['time', 'open', 'high', 'low', 'close']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"缺少必要列: {col}")

        if 'volume' not in df.columns:
            df['volume'] = 0

        return df

    def plot(self, df: pd.DataFrame, title: str = None, 
             show_volume: bool = True, save_path: str = None,
             ma_periods: List[int] = None):
        """
        绘制K线图

        Parameters:
        -----------
        df : pd.DataFrame
            包含OHLCV数据的DataFrame
        title : str
            图表标题
        show_volume : bool
            是否显示成交量
        save_path : str
            保存路径（不指定则显示）
        ma_periods : list
            移动平均线周期，如 [5, 10, 20]
        """
        # 根据是否显示成交量调整布局
        if show_volume:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=self.figsize, 
                                           gridspec_kw={'height_ratios': [3, 1]}, 
                                           sharex=True)
        else:
            fig, ax1 = plt.subplots(1, 1, figsize=(self.figsize[0], self.figsize[1]*0.7))
            ax2 = None

        # 设置背景色
        if self.style == 'dark':
            fig.patch.set_facecolor(self.colors['bg'])
            ax1.set_facecolor(self.colors['bg'])
            if ax2:
                ax2.set_facecolor(self.colors['bg'])

        # 计算颜色
        colors = [self.colors['up'] if row['close'] >= row['open'] else self.colors['down'] 
                  for _, row in df.iterrows()]

        # 绘制K线 - 使用更高效的方式
        self._draw_candles(ax1, df, colors)

        # 绘制移动平均线
        if ma_periods:
            for period in ma_periods:
                if len(df) >= period:
                    ma = df['close'].rolling(window=period).mean()
                    ax1.plot(range(len(df)), ma, label=f'MA{period}', 
                            linewidth=1.5, alpha=0.8)
            ax1.legend(loc='upper left')

        # 设置价格轴
        ax1.set_ylabel('Price', fontsize=12, color=self.colors['text'])
        ax1.tick_params(colors=self.colors['text'])
        ax1.grid(True, alpha=0.3, linestyle='--', color=self.colors['grid'])

        # 设置标题
        if title:
            ax1.set_title(title, fontsize=14, fontweight='bold', 
                         color=self.colors['text'], pad=10)
        else:
            time_range = f"{df['datetime'].iloc[0].strftime('%Y-%m-%d %H:%M')} - {df['datetime'].iloc[-1].strftime('%H:%M')}"
            symbol = "K-Line Chart"
            ax1.set_title(f"{symbol}\n{time_range}", fontsize=14, 
                         fontweight='bold', color=self.colors['text'], pad=10)

        # 绘制成交量
        if show_volume and ax2:
            ax2.bar(range(len(df)), df['volume'], color=colors, 
                   width=0.8, alpha=0.8)
            ax2.set_ylabel('Volume', fontsize=12, color=self.colors['text'])
            ax2.set_xlabel('Time', fontsize=12, color=self.colors['text'])
            ax2.tick_params(colors=self.colors['text'])
            ax2.grid(True, alpha=0.3, linestyle='--', color=self.colors['grid'])

            # 设置x轴标签（优化：数据点多时减少标签数量）
            n = len(df)
            step = max(1, n // 10)  # 最多显示10个标签
            x_labels = [d.strftime('%H:%M') if n < 50 else 
                       (d.strftime('%m-%d %H:%M') if i % step == 0 else '') 
                       for i, d in enumerate(df['datetime'])]
            ax2.set_xticks(range(0, n, step))
            ax2.set_xticklabels([x_labels[i] for i in range(0, n, step)], 
                               rotation=45, ha='right')
        else:
            # 不显示成交量时设置x轴
            n = len(df)
            step = max(1, n // 10)
            x_labels = [d.strftime('%H:%M') for d in df['datetime']]
            ax1.set_xticks(range(0, n, step))
            ax1.set_xticklabels([x_labels[i] for i in range(0, n, step)], 
                               rotation=45, ha='right')

        # 添加统计信息
        self._add_stats(fig, df)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight', 
                       facecolor=self.colors['bg'], edgecolor='none')
            print(f"图表已保存至: {save_path}")
        else:
            plt.show()

    def _draw_candles(self, ax, df, colors):
        """绘制蜡烛图 - 优化版本"""
        n = len(df)

        # 对于大量数据，调整蜡烛宽度
        width = 0.8 if n < 100 else (0.6 if n < 500 else 0.4)

        for i, (idx, row) in enumerate(df.iterrows()):
            color = colors[i]

            # 实体
            height = abs(row['close'] - row['open'])
            bottom = min(row['close'], row['open'])

            # 如果开盘=收盘，画一条横线
            if height < 0.01:
                ax.plot([i-width/2, i+width/2], [row['close'], row['close']], 
                       color=color, linewidth=1)
            else:
                ax.bar(i, height, width, bottom=bottom, color=color, 
                      edgecolor=color, linewidth=0.5)

            # 影线
            ax.plot([i, i], [row['low'], row['high']], color=color, linewidth=0.8)

    def _add_stats(self, fig, df):
        """添加统计信息"""
        price_change = df['close'].iloc[-1] - df['open'].iloc[0]
        price_change_pct = (price_change / df['open'].iloc[0]) * 100
        high = df['high'].max()
        low = df['low'].min()
        total_vol = df['volume'].sum()

        stats = (f"Open: {df['open'].iloc[0]:.2f} | "
                f"Close: {df['close'].iloc[-1]:.2f} | "
                f"High: {high:.2f} | "
                f"Low: {low:.2f} | "
                f"Change: {price_change:+.2f} ({price_change_pct:+.3f}%) | "
                f"Vol: {total_vol:.2f}")

        fig.text(0.5, 0.01, stats, ha='center', fontsize=10, 
                color=self.colors['text'],
                bbox=dict(boxstyle='round', facecolor=self.colors['grid'], 
                         alpha=0.5, edgecolor='none'))


import json
import os


def main():
    """从JSON文件加载数据并绘图"""

    # 方法1：直接指定文件路径
    json_path = "data/kline.json"  # 相对路径，文件在项目根目录的data文件夹里

    # 方法2：让用户输入路径（更灵活）
    # json_path = input("请输入JSON文件路径: ")

    # 检查文件是否存在
    if not os.path.exists(json_path):
        print(f"错误：找不到文件 {json_path}")
        print("请确保文件路径正确，或使用绝对路径")
        return

    # 从文件加载数据
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"成功加载 {len(data)} 条数据")

    # 创建图表
    chart = KLineChart(figsize=(18, 10), style='binance')
    df = chart.load_data(data)

    # 绘制并保存
    chart.plot(df,
               title="K-Line Chart from JSON",
               show_volume=True,
               save_path="output_chart.png",
               ma_periods=[5, 10, 20])

    print("图表已保存至: output_chart.png")


if __name__ == "__main__":
    main()
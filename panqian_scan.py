#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
右侧交易体系 · 盘前扫描脚本
配合《同花顺操作方案》使用

用法：
    python scripts/panqian_scan.py
    
会自动输出：
    1. 大盘指数扫描
    2. 板块涨幅排名
    3. 右侧趋势股筛选（问财选股）
    4. 综合判断
"""

from thsdk import THS
import pandas as pd
from datetime import datetime

def scan_market():
    """每日盘前扫描"""
    with THS() as ths:
        print(f"===== {datetime.now().strftime('%Y-%m-%d')} 盘前扫描 =====\n")
        
        # 1. 大盘指数
        print("【大盘指数】")
        indices = {
            'USHI000001': '上证指数',
            'USZI399001': '深证成指',
            'USZI399006': '创业板指',
            'USHI000688': '科创50',
        }
        for code, name in indices.items():
            resp = ths.market_data_index(code)
            if resp and resp.df is not None and not resp.df.empty:
                d = resp.df.iloc[0]
                price = d.get('价格', 'N/A')
                change = d.get('涨跌', 'N/A')
                print(f"  {name}: {price}  涨跌: {change}")
        
        print()
        
        # 2. 右侧趋势股筛选
        print("【右侧趋势股（问财筛选）】")
        resp = ths.wencai_nlp('20日均线向上，60日均线向上，MACD红柱，换手率大于3%，流通市值大于50亿，非ST')
        if resp and hasattr(resp, 'df') and resp.df is not None and not resp.df.empty:
            df = resp.df.head(15)
            display_cols = [c for c in ['股票代码', '股票简称', '最新价', '涨跌幅', '换手率', '所属同花顺行业'] if c in df.columns]
            if display_cols:
                print(df[display_cols].to_string(index=False))
            else:
                print(df.head().to_string(index=False))
        
        print("\n===== 扫描完成 =====")

if __name__ == '__main__':
    scan_market()

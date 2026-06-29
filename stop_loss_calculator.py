#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
右侧交易 · 止损止盈计算器
输入买入信息，自动计算所有止损止盈价位、移动止损阶梯、条件单参数

使用方法：
    python3 stop_loss_calculator.py
    然后按提示输入股票代码、买入价、仓位、信号类型
"""

import sys


def calculate_stop_loss_profit(symbol, name, buy_price, position_pct, total_capital,
                                signal_type="一买突破", stop_loss_pct=5.0,
                                target_price=None, shares=None):
    """
    计算完整的止损止盈方案
    
    Args:
        symbol: 股票代码
        name: 股票名称
        buy_price: 买入价格
        position_pct: 仓位百分比（如15表示15%）
        total_capital: 总资金（万元）
        signal_type: 信号类型（一买突破/二买回踩/三买加仓）
        stop_loss_pct: 止损百分比
        target_price: 目标价格（可选，默认按15%盈利目标）
        shares: 持股数量（可选，默认按资金计算）
    """
    
    position_amount = total_capital * 10000 * (position_pct / 100)
    
    if shares is None:
        shares = int(position_amount / buy_price)
    
    # 计算止损价
    stop_loss_price = round(buy_price * (1 - stop_loss_pct / 100), 2)
    
    # 计算目标价（如果未提供，按默认盈利目标）
    if target_price is None:
        if signal_type == "一买突破":
            target_price = round(buy_price * 1.15, 2)  # 15%目标
        elif signal_type == "二买回踩":
            target_price = round(buy_price * 1.10, 2)  # 10%目标
        else:
            target_price = round(buy_price * 1.08, 2)  # 8%目标
    
    # 计算盈亏比
    expected_profit_pct = (target_price - buy_price) / buy_price * 100
    risk_reward_ratio = expected_profit_pct / stop_loss_pct
    
    # 计算各阶段止盈价
    profit_20_price = round(buy_price * 1.20, 2)
    profit_30_price = round(buy_price * 1.30, 2)
    profit_50_price = round(buy_price * 1.50, 2)
    
    # 计算各阶段减仓数量
    sell_20_shares = int(shares * 1/3)
    sell_30_shares = int(shares * 1/3)
    sell_50_shares = int(shares * 1/6)
    
    # 计算移动止损阶梯
    trail_10_price = round(buy_price * 1.00, 2)  # 浮盈10%时保本
    trail_20_price = round(buy_price * 1.05, 2)  # 浮盈20%时确保+5%
    trail_30_price = round(buy_price * 1.15, 2)  # 浮盈30%时确保+15%
    
    # 浮盈达到各阶段的股价
    price_at_10 = round(buy_price * 1.10, 2)
    price_at_20 = round(buy_price * 1.20, 2)
    price_at_30 = round(buy_price * 1.30, 2)
    
    # 时间止损
    if signal_type == "一买突破":
        time_stop_days = 10
    elif signal_type == "二买回踩":
        time_stop_days = 10
    else:
        time_stop_days = 10
    
    # 生成报告
    report = f"""
╔══════════════════════════════════════════════════════════╗
║          右侧交易 · 止损止盈计算器                      ║
╚══════════════════════════════════════════════════════════╝

【基础信息】
  股票代码：{symbol}  {name}
  买入价格：{buy_price:.2f} 元
  总资金：{total_capital:.0f} 万元
  仓位比例：{position_pct:.0f}%
  投入资金：{position_amount/10000:.1f} 万元
  买入数量：{shares} 股
  信号类型：{signal_type}

【止损配置】
  ├─ 固定止损幅度：-{stop_loss_pct:.0f}%
  ├─ 止损价格：{stop_loss_price:.2f} 元
  ├─ 最大亏损：{shares * (buy_price - stop_loss_price):.0f} 元
  ├─ 总资金亏损：{shares * (buy_price - stop_loss_price) / (total_capital * 10000) * 100:.2f}%
  └─ 条件单：股价跌破 {stop_loss_price:.2f} 元，卖出 {shares} 股

【止盈配置】
  ├─ 目标价格：{target_price:.2f} 元（+{expected_profit_pct:.1f}%）
  ├─ 盈亏比：{risk_reward_ratio:.1f}:1
  ├─ 盈亏比评估：{"✓ 可做" if risk_reward_ratio >= 2.0 else "✗ 建议放弃"}（要求≥2:1）
  │
  ├─ 20%止盈：{profit_20_price:.2f} 元 → 卖出 {sell_20_shares} 股（1/3仓位）
  ├─ 30%止盈：{profit_30_price:.2f} 元 → 卖出 {sell_30_shares} 股（1/3仓位）
  ├─ 50%止盈：{profit_50_price:.2f} 元 → 卖出 {sell_50_shares} 股（1/6仓位）
  └─ 剩余仓位：{shares - sell_20_shares - sell_30_shares - sell_50_shares} 股，用移动止损持有

【移动止损阶梯】
  ├─ 当前：止损价 {stop_loss_price:.2f} 元（-{stop_loss_pct:.0f}%）
  ├─ 股价达到 {price_at_10:.2f} 元（+10%）
  │   └─ 止损上移至 {trail_10_price:.2f} 元（保本）
  ├─ 股价达到 {price_at_20:.2f} 元（+20%）
  │   └─ 止损上移至 {trail_20_price:.2f} 元（+5%），同时减仓1/3
  ├─ 股价达到 {price_at_30:.2f} 元（+30%）
  │   └─ 止损上移至 {trail_30_price:.2f} 元（+15%），同时再减仓1/3
  └─ 浮盈>30%后：移动止损 = 最高价 × 0.92（从高点回落-8%清仓）

【时间止损】
  └─ 买入后 {time_stop_days} 个交易日未盈利，减仓1/2

【同花顺条件单参数】（可直接复制）
────────────────────────────────────
条件单1：止损单
  条件类型：价格条件
  监控标的：{symbol}
  触发条件：最新价 ≤ {stop_loss_price:.2f}元
  委托方向：卖出
  委托数量：{shares}股
  委托价格：市价（或{stop_loss_price:.2f}元限价）
  有效期：长期有效

条件单2：20%止盈单
  条件类型：价格条件
  监控标的：{symbol}
  触发条件：最新价 ≥ {profit_20_price:.2f}元
  委托方向：卖出
  委托数量：{sell_20_shares}股
  委托价格：限价{profit_20_price:.2f}元
  有效期：长期有效

条件单3：30%止盈单
  条件类型：价格条件
  监控标的：{symbol}
  触发条件：最新价 ≥ {profit_30_price:.2f}元
  委托方向：卖出
  委托数量：{sell_30_shares}股
  委托价格：限价{profit_30_price:.2f}元
  有效期：长期有效

注：移动止损条件单需手动更新，当达到新阶梯时修改触发价格
────────────────────────────────────

【盈亏场景模拟】
  盈利场景（到达目标价）：
    盈利 {shares * (target_price - buy_price):.0f} 元
    总资金贡献 +{shares * (target_price - buy_price) / (total_capital * 10000) * 100:.2f}%
  
  亏损场景（触发止损）：
    亏损 {shares * (buy_price - stop_loss_price):.0f} 元
    总资金亏损 -{shares * (buy_price - stop_loss_price) / (total_capital * 10000) * 100:.2f}%
  
  盈亏比：{risk_reward_ratio:.1f}:1
"""
    
    return report


def interactive_mode():
    """交互模式"""
    print("\n" + "="*60)
    print("  右侧交易 · 止损止盈计算器")
    print("="*60)
    
    try:
        symbol = input("\n股票代码（如600XXX）：").strip()
        name = input("股票名称：").strip()
        buy_price = float(input("买入价格（元）：").strip())
        position_pct = float(input("仓位比例（如15表示15%）：").strip())
        total_capital = float(input("总资金（万元，如100表示100万）：").strip())
        
        print("\n信号类型：")
        print("  1. 一买突破（短线-5%止损）")
        print("  2. 二买回踩（短线-5%止损）")
        print("  3. 三买加仓（短线-5%止损）")
        signal_choice = input("请选择（1/2/3，默认1）：").strip() or "1"
        
        signal_map = {"1": "一买突破", "2": "二买回踩", "3": "三买加仓"}
        signal_type = signal_map.get(signal_choice, "一买突破")
        
        stop_loss_pct = float(input(f"止损幅度（默认5%）：").strip() or "5")
        
        target_input = input("目标价格（可选，直接回车按默认）：").strip()
        target_price = float(target_input) if target_input else None
        
        report = calculate_stop_loss_profit(
            symbol=symbol,
            name=name,
            buy_price=buy_price,
            position_pct=position_pct,
            total_capital=total_capital,
            signal_type=signal_type,
            stop_loss_pct=stop_loss_pct,
            target_price=target_price
        )
        
        print(report)
        
        # 保存到文件
        save = input("\n是否保存结果到文件？（y/n，默认y）：").strip().lower() or "y"
        if save == "y":
            filename = f"/Users/zjy/WorkBuddy/2026-06-29-15-15-35/scripts/止损止盈_{symbol}_{buy_price:.2f}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"已保存到：{filename}")
        
    except ValueError as e:
        print(f"输入错误：{e}")
    except KeyboardInterrupt:
        print("\n已取消")


def quick_mode(symbol, name, buy_price, position_pct, total_capital, signal_type="一买突破"):
    """快速模式 - 直接打印结果"""
    report = calculate_stop_loss_profit(
        symbol=symbol,
        name=name,
        buy_price=buy_price,
        position_pct=position_pct,
        total_capital=total_capital,
        signal_type=signal_type
    )
    print(report)
    return report


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # 快速模式：python3 stop_loss_calculator.py --quick 600XXX 某股 20 15 100
        if len(sys.argv) >= 6:
            quick_mode(
                symbol=sys.argv[2],
                name=sys.argv[3],
                buy_price=float(sys.argv[4]),
                position_pct=float(sys.argv[5]),
                total_capital=float(sys.argv[6]),
                signal_type=sys.argv[7] if len(sys.argv) > 7 else "一买突破"
            )
        else:
            print("快速模式用法：python3 stop_loss_calculator.py --quick <代码> <名称> <买入价> <仓位%> <总资金万> [信号类型]")
    else:
        interactive_mode()

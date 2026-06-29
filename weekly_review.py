#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
右侧交易 · 周度交易复盘统计
输入本周交易记录，自动统计胜率、盈亏比、规则执行、改进建议

使用方法：
    python3 weekly_review.py
    按提示输入本周交易数据
"""

import datetime


def analyze_week(trades, total_capital=100):
    """
    分析一周交易数据
    
    Args:
        trades: list of dict, 每笔交易包含：
            - symbol: 股票代码
            - name: 股票名称
            - buy_price: 买入价
            - sell_price: 卖出价（未卖出则当前价）
            - shares: 数量
            - signal_type: 信号类型（一买/二买/三买）
            - stop_loss_price: 止损价
            - target_price: 目标价
            - reason: 卖出理由（止损/止盈/移动止损/时间止损/技术止盈/其他）
            - executed: 是否按计划执行（True/False）
            - planned: 是否计划内交易（True/False）
    """
    
    total_capital_yuan = total_capital * 10000
    
    # 基础统计
    total_trades = len(trades)
    profitable_trades = [t for t in trades if t["sell_price"] >= t["buy_price"]]
    losing_trades = [t for t in trades if t["sell_price"] < t["buy_price"]]
    
    win_count = len(profitable_trades)
    loss_count = len(losing_trades)
    win_rate = win_count / total_trades * 100 if total_trades > 0 else 0
    
    # 计算总盈亏
    total_profit = sum((t["sell_price"] - t["buy_price"]) * t["shares"] for t in profitable_trades)
    total_loss = sum((t["buy_price"] - t["sell_price"]) * t["shares"] for t in losing_trades)
    net_pnl = total_profit - total_loss
    net_pnl_pct = net_pnl / total_capital_yuan * 100
    
    # 盈亏比
    avg_profit = total_profit / win_count if win_count > 0 else 0
    avg_loss = total_loss / loss_count if loss_count > 0 else 1
    profit_loss_ratio = avg_profit / avg_loss if avg_loss > 0 else 0
    
    # 最大单笔
    max_profit_trade = max(profitable_trades, key=lambda t: (t["sell_price"] - t["buy_price"]) * t["shares"]) if profitable_trades else None
    max_loss_trade = max(losing_trades, key=lambda t: (t["buy_price"] - t["sell_price"]) * t["shares"]) if losing_trades else None
    
    max_profit_pct = 0
    if max_profit_trade:
        max_profit_pct = (max_profit_trade["sell_price"] - max_profit_trade["buy_price"]) / max_profit_trade["buy_price"] * 100
    
    max_loss_pct = 0
    if max_loss_trade:
        max_loss_pct = (max_loss_trade["buy_price"] - max_loss_trade["sell_price"]) / max_loss_trade["buy_price"] * 100
    
    # 规则执行检查
    stop_loss_trades = [t for t in trades if t.get("reason") == "止损"]
    profit_taking_trades = [t for t in trades if t.get("reason") in ["止盈", "移动止损", "技术止盈"]]
    planned_trades = [t for t in trades if t.get("planned", True)]
    unplanned_trades = [t for t in trades if not t.get("planned", True)]
    executed_trades = [t for t in trades if t.get("executed", True)]
    
    # 盈亏比检查
    good_ratio_trades = []
    bad_ratio_trades = []
    for t in trades:
        buy = t["buy_price"]
        stop = t.get("stop_loss_price", buy * 0.95)
        target = t.get("target_price", buy * 1.15)
        risk = (buy - stop) / buy * 100
        reward = (target - buy) / buy * 100
        ratio = reward / risk if risk > 0 else 0
        if ratio >= 2.0:
            good_ratio_trades.append(t)
        else:
            bad_ratio_trades.append(t)
    
    # 生成报告
    week_start = (datetime.datetime.now() - datetime.timedelta(days=datetime.datetime.now().weekday())).strftime("%Y.%m.%d")
    week_end = datetime.datetime.now().strftime("%Y.%m.%d")
    
    report = f"""
╔══════════════════════════════════════════════════════════════════╗
║              右侧交易 · 周度交易复盘统计                          ║
║              {week_start} - {week_end}                                  ║
╚══════════════════════════════════════════════════════════════════╝

【一、基础数据】
  交易次数：{total_trades} 次
  盈利次数：{win_count} 次  亏损次数：{loss_count} 次
  胜率：{win_rate:.1f}%  {"✓ 合格（≥50%）" if win_rate >= 50 else "✗ 需改进（<50%）"}
  
  总盈利：+{total_profit:,.0f} 元
  总亏损：-{total_loss:,.0f} 元
  净盈亏：{net_pnl:+.0f} 元（{net_pnl_pct:+.2f}%）
  
  盈亏比：{profit_loss_ratio:.1f}:1  {"✓ 合格（≥1.5）" if profit_loss_ratio >= 1.5 else "✗ 需改进（<1.5）"}
  平均盈利：+{avg_profit:,.0f} 元/笔
  平均亏损：-{avg_loss:,.0f} 元/笔

【二、最大单笔】
  最大单笔盈利：{max_profit_trade['symbol'] if max_profit_trade else 'N/A'}  
    {max_profit_pct:+.1f}%（{(max_profit_trade['sell_price'] - max_profit_trade['buy_price']) * max_profit_trade['shares'] if max_profit_trade else 0:,.0f}元）
  最大单笔亏损：{max_loss_trade['symbol'] if max_loss_trade else 'N/A'}
    {max_loss_pct:.1f}%（{(max_loss_trade['buy_price'] - max_loss_trade['sell_price']) * max_loss_trade['shares'] if max_loss_trade else 0:,.0f}元）

【三、规则执行检查】
  ├─ 止损交易：{len(stop_loss_trades)} 笔
  │   {"└─ 全部按计划执行 ✓" if all(t.get('executed', True) for t in stop_loss_trades) else "└─ 有未执行的交易 ✗"}
  │
  ├─ 止盈交易：{len(profit_taking_trades)} 笔
  │   {"└─ 全部按计划执行 ✓" if all(t.get('executed', True) for t in profit_taking_trades) else "└─ 有未执行的交易 ✗"}
  │
  ├─ 计划内交易：{len(planned_trades)} 笔
  ├─ 计划外交易：{len(unplanned_trades)} 笔
  │   {"└─ 无计划外交易 ✓" if len(unplanned_trades) == 0 else "└─ 有计划外交易，需警惕 ✗"}
  │
  └─ 已执行交易：{len(executed_trades)}/{total_trades} 笔
      {"└─ 执行率100% ✓" if len(executed_trades) == total_trades else "└─ 执行率不足，需改进 ✗"}

【四、盈亏比检查】
  盈亏比≥2:1的交易：{len(good_ratio_trades)} 笔（{len(good_ratio_trades)/total_trades*100 if total_trades>0 else 0:.0f}%）
  {"  ✓ 占比高，符合要求" if len(good_ratio_trades) >= total_trades * 0.7 else "  ✗ 占比低，需提高标准"}
  
  盈亏比<2:1的交易：{len(bad_ratio_trades)} 笔（{len(bad_ratio_trades)/total_trades*100 if total_trades>0 else 0:.0f}%）
  {"  ✓ 占比低，可接受" if len(bad_ratio_trades) <= total_trades * 0.3 else "  ✗ 占比高，需降低这部分交易"}

【五、信号类型分析】
"""
    
    # 按信号类型统计
    signal_types = {}
    for t in trades:
        st = t.get("signal_type", "其他")
        if st not in signal_types:
            signal_types[st] = {"count": 0, "profit": 0, "loss": 0, "pnl": 0}
        signal_types[st]["count"] += 1
        pnl = (t["sell_price"] - t["buy_price"]) * t["shares"]
        signal_types[st]["pnl"] += pnl
        if pnl > 0:
            signal_types[st]["profit"] += pnl
        else:
            signal_types[st]["loss"] += abs(pnl)
    
    for st, data in signal_types.items():
        win_rate_st = data["profit"] / (data["profit"] + data["loss"]) * 100 if (data["profit"] + data["loss"]) > 0 else 0
        report += f"  {st}：{data['count']}笔，净盈亏{data['pnl']:+.0f}元，胜率{win_rate_st:.0f}%\n"
    
    # 改进建议
    report += "\n【六、改进建议】\n"
    
    suggestions = []
    if win_rate < 50:
        suggestions.append("胜率低于50%，检查买入信号是否过于宽松，或是否逆势操作")
    if profit_loss_ratio < 1.5:
        suggestions.append("盈亏比偏低，检查是否止盈过早或止损过晚，严格按盈亏比≥2:1筛选")
    if len(unplanned_trades) > 0:
        suggestions.append(f"有{len(unplanned_trades)}笔计划外交易，杜绝盘中临时决策")
    if any(not t.get('executed', True) for t in stop_loss_trades):
        suggestions.append("止损执行不到位，这是致命的！下次触发必须无条件执行")
    if len(bad_ratio_trades) > total_trades * 0.3:
        suggestions.append("盈亏比<2:1的交易占比过高，提高买入标准，宁缺毋滥")
    if not suggestions:
        suggestions.append("本周表现良好，继续保持！")
    
    for i, s in enumerate(suggestions, 1):
        report += f"  {i}. {s}\n"
    
    report += f"""
【七、下周行动清单】
  □ 更新所有持仓的移动止损条件单
  □ 检查当前持仓的浮盈状态，是否到达新阶梯
  □ 更新股票池（问财筛选）
  □ 审视交易规则，是否需要调整（季度调整）
  □ 保持盈亏比≥2:1的标准，不降低要求
"""
    
    return report


def interactive_mode():
    """交互模式"""
    print("\n" + "="*60)
    print("  右侧交易 · 周度复盘统计")
    print("="*60)
    
    try:
        total_capital = float(input("\n总资金（万元，默认100）：").strip() or "100")
        
        trades = []
        while True:
            print(f"\n--- 输入第 {len(trades)+1} 笔交易（直接回车结束）---")
            symbol = input("股票代码（直接回车结束）：").strip()
            if not symbol:
                break
            
            name = input("股票名称：").strip()
            buy_price = float(input("买入价格：").strip())
            sell_price_input = input("卖出价格（未卖出输入当前价）：").strip()
            sell_price = float(sell_price_input) if sell_price_input else buy_price
            shares = int(input("持股数量：").strip())
            
            print("\n信号类型：")
            print("  1. 一买突破  2. 二买回踩  3. 三买加仓  4. 其他")
            signal_choice = input("请选择（1/2/3/4）：").strip() or "4"
            signal_map = {"1": "一买突破", "2": "二买回踩", "3": "三买加仓", "4": "其他"}
            signal_type = signal_map.get(signal_choice, "其他")
            
            stop_loss_price = float(input("止损价格（默认买入价-5%）：").strip() or str(buy_price * 0.95))
            target_price = float(input("目标价格（默认买入价+15%）：").strip() or str(buy_price * 1.15))
            
            print("\n卖出理由：")
            print("  1. 止损  2. 止盈  3. 移动止损  4. 技术止盈  5. 时间止损  6. 其他")
            reason_choice = input("请选择（1-6）：").strip() or "6"
            reason_map = {"1": "止损", "2": "止盈", "3": "移动止损", "4": "技术止盈", "5": "时间止损", "6": "其他"}
            reason = reason_map.get(reason_choice, "其他")
            
            executed = input("是否按计划执行？（y/n，默认y）：").strip().lower() or "y"
            planned = input("是否计划内交易？（y/n，默认y）：").strip().lower() or "y"
            
            trades.append({
                "symbol": symbol,
                "name": name,
                "buy_price": buy_price,
                "sell_price": sell_price,
                "shares": shares,
                "signal_type": signal_type,
                "stop_loss_price": stop_loss_price,
                "target_price": target_price,
                "reason": reason,
                "executed": executed == "y",
                "planned": planned == "y"
            })
        
        if trades:
            report = analyze_week(trades, total_capital)
            print(report)
            
            save = input("\n是否保存到文件？（y/n，默认y）：").strip().lower() or "y"
            if save == "y":
                filename = f"/Users/zjy/WorkBuddy/2026-06-29-15-15-35/scripts/周度复盘_{datetime.datetime.now().strftime('%Y%m%d')}.txt"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(report)
                print(f"已保存到：{filename}")
        else:
            print("未输入交易记录，退出")
            
    except ValueError as e:
        print(f"输入错误：{e}")
    except KeyboardInterrupt:
        print("\n已取消")


def demo_mode():
    """演示模式"""
    demo_trades = [
        {
            "symbol": "600XXX",
            "name": "示例A",
            "buy_price": 20.00,
            "sell_price": 24.00,
            "shares": 7500,
            "signal_type": "一买突破",
            "stop_loss_price": 19.00,
            "target_price": 23.00,
            "reason": "止盈",
            "executed": True,
            "planned": True
        },
        {
            "symbol": "002XXX",
            "name": "示例B",
            "buy_price": 15.00,
            "sell_price": 14.20,
            "shares": 10000,
            "signal_type": "二买回踩",
            "stop_loss_price": 14.25,
            "target_price": 16.50,
            "reason": "止损",
            "executed": True,
            "planned": True
        },
        {
            "symbol": "300XXX",
            "name": "示例C",
            "buy_price": 30.00,
            "sell_price": 32.00,
            "shares": 5000,
            "signal_type": "三买加仓",
            "stop_loss_price": 28.50,
            "target_price": 33.00,
            "reason": "移动止损",
            "executed": True,
            "planned": True
        },
        {
            "symbol": "600YYY",
            "name": "示例D",
            "buy_price": 25.00,
            "sell_price": 23.50,
            "shares": 6000,
            "signal_type": "一买突破",
            "stop_loss_price": 23.75,
            "target_price": 28.00,
            "reason": "止损",
            "executed": False,
            "planned": True
        }
    ]
    
    print("\n【演示模式】使用示例数据\n")
    report = analyze_week(demo_trades, 100)
    print(report)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_mode()
    else:
        interactive_mode()

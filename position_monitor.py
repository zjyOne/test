#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
右侧交易 · 持仓监控脚本
输入持仓列表，自动检查是否触发止损、止盈、移动止损、技术止盈、时间止损

使用方法：
    python3 position_monitor.py
    然后按提示输入持仓信息
"""

import datetime


def check_position(position, market_data=None):
    """
    检查单个持仓的状态
    
    Args:
        position: dict with keys:
            - symbol: 股票代码
            - name: 股票名称
            - buy_price: 买入价
            - current_price: 当前价
            - shares: 持股数量
            - buy_date: 买入日期 (YYYY-MM-DD)
            - position_pct: 仓位比例
            - stop_loss_price: 止损价
            - target_price: 目标价
            - highest_price: 最高价（用于移动止损）
            - total_capital: 总资金（万元）
    """
    
    results = []
    alerts = []
    
    symbol = position["symbol"]
    name = position["name"]
    buy_price = position["buy_price"]
    current_price = position["current_price"]
    shares = position["shares"]
    buy_date = position.get("buy_date", "")
    highest_price = position.get("highest_price", current_price)
    total_capital = position.get("total_capital", 100) * 10000
    
    # 计算浮盈
    float_profit = (current_price - buy_price) / buy_price * 100
    float_amount = shares * (current_price - buy_price)
    
    # 1. 检查固定止损
    stop_loss_price = position.get("stop_loss_price", buy_price * 0.95)
    if current_price <= stop_loss_price:
        results.append({
            "type": "🚨 固定止损触发",
            "detail": f"当前价{current_price:.2f} ≤ 止损价{stop_loss_price:.2f}",
            "action": "立即清仓",
            "severity": "high"
        })
        alerts.append(f"{symbol} {name}：触发固定止损！当前{current_price:.2f} ≤ 止损{stop_loss_price:.2f}")
    
    # 2. 检查总资金止损
    total_loss_pct = abs(float_amount) / total_capital * 100
    if float_amount < 0 and total_loss_pct >= 2.0:
        results.append({
            "type": "🚨 总资金止损触发",
            "detail": f"总资金亏损{total_loss_pct:.2f}% ≥ 2%",
            "action": "立即清仓",
            "severity": "high"
        })
        alerts.append(f"{symbol} {name}：触发总资金止损！总资金亏损{total_loss_pct:.2f}%")
    
    # 3. 检查固定比例止盈（20%、30%）
    profit_20_price = buy_price * 1.20
    profit_30_price = buy_price * 1.30
    
    if current_price >= profit_30_price:
        results.append({
            "type": "⚠️ 30%止盈触发",
            "detail": f"当前价{current_price:.2f} ≥ 30%止盈价{profit_30_price:.2f}",
            "action": "减仓1/3（卖出约{}股）".format(int(shares/3)),
            "severity": "medium"
        })
        alerts.append(f"{symbol} {name}：触发30%止盈！建议减仓1/3")
    elif current_price >= profit_20_price:
        results.append({
            "type": "⚠️ 20%止盈触发",
            "detail": f"当前价{current_price:.2f} ≥ 20%止盈价{profit_20_price:.2f}",
            "action": "减仓1/3（卖出约{}股）".format(int(shares/3)),
            "severity": "medium"
        })
        alerts.append(f"{symbol} {name}：触发20%止盈！建议减仓1/3")
    
    # 4. 检查移动止损（从最高点回落8%）
    if highest_price > buy_price * 1.10:  # 只有盈利超过10%才检查移动止损
        trail_stop_price = highest_price * 0.92
        if current_price <= trail_stop_price:
            results.append({
                "type": "🚨 移动止损触发",
                "detail": f"从最高价{highest_price:.2f}回落≥8%，当前{current_price:.2f}",
                "action": "清仓剩余仓位",
                "severity": "high"
            })
            alerts.append(f"{symbol} {name}：触发移动止损！从最高{highest_price:.2f}回落到{current_price:.2f}")
    
    # 5. 检查移动止损阶梯（根据浮盈状态）
    if float_profit >= 30:
        expected_trail = buy_price * 1.15
        if current_price <= expected_trail * 1.02:  # 接近触发
            results.append({
                "type": "ℹ️ 移动止损提醒（30%档）",
                "detail": f"浮盈{float_profit:.1f}%，移动止损应在{expected_trail:.2f}元",
                "action": "检查条件单是否已更新",
                "severity": "low"
            })
    elif float_profit >= 20:
        expected_trail = buy_price * 1.05
        results.append({
            "type": "ℹ️ 移动止损提醒（20%档）",
            "detail": f"浮盈{float_profit:.1f}%，移动止损应在{expected_trail:.2f}元",
            "action": "更新止损条件单至{:.2f}元".format(expected_trail),
            "severity": "low"
        })
    elif float_profit >= 10:
        expected_trail = buy_price * 1.00
        results.append({
            "type": "ℹ️ 移动止损提醒（10%档）",
            "detail": f"浮盈{float_profit:.1f}%，移动止损应上移至成本价{expected_trail:.2f}元",
            "action": "更新止损条件单至成本价",
            "severity": "low"
        })
    
    # 6. 检查时间止损
    if buy_date:
        try:
            buy_dt = datetime.datetime.strptime(buy_date, "%Y-%m-%d")
            today = datetime.datetime.now()
            hold_days = (today - buy_dt).days
            # 简单估算交易日（扣除周末）
            trade_days = hold_days * 5 // 7
            
            if trade_days >= 10 and float_profit <= 0:
                results.append({
                    "type": "⚠️ 时间止损触发",
                    "detail": f"持有约{trade_days}个交易日未盈利（浮盈{float_profit:.1f}%）",
                    "action": "减仓1/2",
                    "severity": "medium"
                })
                alerts.append(f"{symbol} {name}：触发时间止损！持有{trade_days}日未盈利")
        except:
            pass
    
    # 7. 检查技术止盈信号（简化版）
    # 放量滞涨：这里简化为价格微涨但当前价接近买入价*1.05
    if float_profit > 15 and float_profit < 25:
        # 假设高位震荡
        results.append({
            "type": "ℹ️ 技术提醒",
            "detail": f"浮盈{float_profit:.1f}%，接近20%止盈位，关注是否放量滞涨",
            "action": "密切观察，准备止盈",
            "severity": "low"
        })
    
    # 生成健康状态
    if not results:
        health = "✓ 健康"
    elif any(r["severity"] == "high" for r in results):
        health = "🚨 需立即处理"
    elif any(r["severity"] == "medium" for r in results):
        health = "⚠️ 需关注"
    else:
        health = "ℹ️ 有提醒"
    
    return {
        "symbol": symbol,
        "name": name,
        "health": health,
        "float_profit": float_profit,
        "float_amount": float_amount,
        "highest_price": highest_price,
        "results": results,
        "alerts": alerts
    }


def monitor_positions(positions):
    """监控多个持仓"""
    
    print("\n" + "="*70)
    print("  持仓监控报告")
    print(f"  生成时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    all_alerts = []
    need_action = []
    
    for pos in positions:
        result = check_position(pos)
        
        print(f"\n{'─'*70}")
        print(f"【{result['symbol']} {result['name']}】 状态：{result['health']}")
        print(f"  浮盈：{result['float_profit']:+.1f}%  ({result['float_amount']:+.0f}元)")
        print(f"  最高价记录：{result['highest_price']:.2f}元")
        
        if result["results"]:
            for r in result["results"]:
                emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(r["severity"], "⚪")
                print(f"  {emoji} {r['type']}")
                print(f"     详情：{r['detail']}")
                print(f"     建议：{r['action']}")
        else:
            print(f"  🟢 无异常，正常持有")
        
        all_alerts.extend(result["alerts"])
        
        if any(r["severity"] in ["high", "medium"] for r in result["results"]):
            need_action.append(result)
    
    # 汇总
    print(f"\n{'='*70}")
    print("【汇总】")
    print(f"  监控持仓：{len(positions)} 只")
    print(f"  需立即处理：{sum(1 for p in need_action if any(r['severity']=='high' for r in p['results']))} 只")
    print(f"  需关注：{sum(1 for p in need_action if any(r['severity']=='medium' for r in p['results']) and not any(r['severity']=='high' for r in p['results']))} 只")
    print(f"  正常持有：{len(positions) - len(need_action)} 只")
    
    if all_alerts:
        print(f"\n【关键提醒】")
        for alert in all_alerts:
            print(f"  ⚠️ {alert}")
    
    print(f"\n{'='*70}")
    
    return all_alerts


def interactive_mode():
    """交互模式"""
    print("\n" + "="*60)
    print("  右侧交易 · 持仓监控")
    print("="*60)
    
    positions = []
    
    try:
        total_capital = float(input("\n总资金（万元，默认100）：").strip() or "100")
        
        while True:
            print(f"\n--- 输入第 {len(positions)+1} 只持仓（直接回车结束）---")
            symbol = input("股票代码（直接回车结束）：").strip()
            if not symbol:
                break
            
            name = input("股票名称：").strip()
            buy_price = float(input("买入价格：").strip())
            current_price = float(input("当前价格：").strip())
            shares = int(input("持股数量：").strip())
            buy_date = input("买入日期（YYYY-MM-DD，可选）：").strip()
            highest_price = input(f"最高价（默认{current_price}）：").strip()
            highest_price = float(highest_price) if highest_price else current_price
            
            positions.append({
                "symbol": symbol,
                "name": name,
                "buy_price": buy_price,
                "current_price": current_price,
                "shares": shares,
                "buy_date": buy_date,
                "highest_price": highest_price,
                "total_capital": total_capital
            })
        
        if positions:
            monitor_positions(positions)
        else:
            print("未输入持仓，退出")
            
    except ValueError as e:
        print(f"输入错误：{e}")
    except KeyboardInterrupt:
        print("\n已取消")


def demo_mode():
    """演示模式 - 用示例数据展示"""
    demo_positions = [
        {
            "symbol": "600XXX",
            "name": "示例A股A",
            "buy_price": 20.00,
            "current_price": 24.50,
            "shares": 7500,
            "buy_date": "2026-06-15",
            "highest_price": 24.80,
            "total_capital": 100
        },
        {
            "symbol": "002XXX",
            "name": "示例A股B",
            "buy_price": 15.00,
            "current_price": 14.20,
            "shares": 10000,
            "buy_date": "2026-06-20",
            "highest_price": 15.50,
            "total_capital": 100
        },
        {
            "symbol": "300XXX",
            "name": "示例A股C",
            "buy_price": 30.00,
            "current_price": 31.50,
            "shares": 5000,
            "buy_date": "2026-06-25",
            "highest_price": 32.00,
            "total_capital": 100
        }
    ]
    
    print("\n【演示模式】使用示例数据展示监控功能\n")
    monitor_positions(demo_positions)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_mode()
    else:
        interactive_mode()

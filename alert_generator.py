#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
右侧交易 · 预警条件单生成器
根据买入信息，自动生成同花顺预警条件单的参数

使用方法：
    python3 alert_generator.py
    按提示输入买入信息，输出可直接复制到同花顺的预警参数
"""


def generate_alerts(symbol, name, buy_price, shares, signal_type="一买突破"):
    """
    生成完整的预警条件单参数
    """
    
    # 止损价
    stop_loss_price = round(buy_price * 0.95, 2)
    
    # 止盈价
    profit_20_price = round(buy_price * 1.20, 2)
    profit_30_price = round(buy_price * 1.30, 2)
    
    # 移动止损阶梯
    trail_10_price = round(buy_price * 1.00, 2)
    trail_20_price = round(buy_price * 1.05, 2)
    trail_30_price = round(buy_price * 1.15, 2)
    
    # 减仓数量
    sell_20_shares = int(shares * 1/3)
    sell_30_shares = int(shares * 1/3)
    
    # 技术止盈价（跌破5日均线，假设5日均线在买入价附近）
    ma5_price = round(buy_price * 0.98, 2)  # 简化估算
    ma20_price = round(buy_price * 0.95, 2)  # 简化估算
    
    report = f"""
╔══════════════════════════════════════════════════════════╗
║        同花顺预警条件单参数生成器                        ║
╚══════════════════════════════════════════════════════════╝

股票：{symbol} {name}
买入价：{buy_price:.2f}元
持股数：{shares}股
信号类型：{signal_type}

═══════════════════════════════════════════════════════════
【条件单1】固定止损单（最优先设置！）
═══════════════════════════════════════════════════════════
条件类型：价格条件
监控标的：{symbol}
触发条件：最新价 ≤ {stop_loss_price:.2f}元
委托方向：卖出
委托数量：{shares}股
委托价格：市价（或{stop_loss_price:.2f}元限价）
有效期：长期有效

说明：这是买入后必须立刻设置的条件单！无论什么情况，
      股价跌破{stop_loss_price:.2f}元就自动卖出，防止你犹豫。

═══════════════════════════════════════════════════════════
【条件单2】20%止盈单
═══════════════════════════════════════════════════════════
条件类型：价格条件
监控标的：{symbol}
触发条件：最新价 ≥ {profit_20_price:.2f}元
委托方向：卖出
委托数量：{sell_20_shares}股（1/3仓位）
委托价格：限价{profit_20_price:.2f}元（或市价）
有效期：长期有效

说明：浮盈20%时自动卖出1/3，锁定利润。不要贪心，
      先落袋为安，剩余仓位让利润奔跑。

═══════════════════════════════════════════════════════════
【条件单3】30%止盈单
═══════════════════════════════════════════════════════════
条件类型：价格条件
监控标的：{symbol}
触发条件：最新价 ≥ {profit_30_price:.2f}元
委托方向：卖出
委托数量：{sell_30_shares}股（1/3仓位）
委托价格：限价{profit_30_price:.2f}元（或市价）
有效期：长期有效

说明：浮盈30%时再卖出1/3。此时已锁定2/3利润，
      剩余1/3仓位用移动止损持有。

═══════════════════════════════════════════════════════════
【条件单4】移动止损-10%档（浮盈10%后更新）
═══════════════════════════════════════════════════════════
条件类型：价格条件
监控标的：{symbol}
触发条件：最新价 ≤ {trail_10_price:.2f}元
委托方向：卖出
委托数量：{shares}股（全部剩余仓位）
委托价格：市价
有效期：长期有效

说明：当浮盈达到10%（股价约{buy_price*1.10:.2f}元）时，
      将止损上移至成本价{trail_10_price:.2f}元，确保这笔交易不亏钱。
      ⚠️ 注意：此条件单需要手动更新！当浮盈达到10%时，
      修改触发价格为{trail_10_price:.2f}元。

═══════════════════════════════════════════════════════════
【条件单5】移动止损-20%档（浮盈20%后更新）
═══════════════════════════════════════════════════════════
条件类型：价格条件
监控标的：{symbol}
触发条件：最新价 ≤ {trail_20_price:.2f}元
委托方向：卖出
委托数量：{shares - sell_20_shares}股（剩余2/3仓位）
委托价格：市价
有效期：长期有效

说明：当浮盈达到20%（股价约{buy_price*1.20:.2f}元）时，
      将止损上移至{trail_20_price:.2f}元（确保至少赚5%），
      同时执行20%止盈减仓。
      ⚠️ 注意：此条件单需要手动更新！

═══════════════════════════════════════════════════════════
【条件单6】移动止损-30%档（浮盈30%后更新）
═══════════════════════════════════════════════════════════
条件类型：价格条件
监控标的：{symbol}
触发条件：最新价 ≤ {trail_30_price:.2f}元
委托方向：卖出
委托数量：{shares - sell_20_shares - sell_30_shares}股（剩余1/3仓位）
委托价格：市价
有效期：长期有效

说明：当浮盈达到30%（股价约{buy_price*1.30:.2f}元）时，
      将止损上移至{trail_30_price:.2f}元（确保至少赚15%），
      同时执行30%止盈减仓。
      ⚠️ 注意：此条件单需要手动更新！

═══════════════════════════════════════════════════════════
【条件单7】移动止损-30%以上档（跟踪最高价×0.92）
═══════════════════════════════════════════════════════════
条件类型：价格条件
监控标的：{symbol}
触发条件：最新价 ≤ 【最高价×0.92】（需手动计算更新）
委托方向：卖出
委托数量：【剩余仓位】股
委托价格：市价
有效期：长期有效

说明：当浮盈超过30%后，不再用固定价格，而是跟踪最高价。
      每天收盘后记录最高价，次日更新条件单触发价格。
      计算公式：最高价 × 0.92
      
      示例：
      如果最高价是28.00元，条件单触发价 = 28.00 × 0.92 = 25.76元
      如果次日股价涨到29.00元，更新条件单触发价 = 29.00 × 0.92 = 26.68元
      
      ⚠️ 此条件单需要每天手动更新！建议每天收盘后检查并更新。

═══════════════════════════════════════════════════════════
【同花顺设置步骤】
═══════════════════════════════════════════════════════════
1. 打开同花顺 → 交易 → 条件单
2. 点击"新建" → 选择"价格条件"
3. 按上述参数填写：监控标的、触发条件、委托方向、数量、价格
4. 提交后条件单在云端运行，电脑关机也生效
5. 每天收盘后检查条件单状态，更新移动止损条件单

═══════════════════════════════════════════════════════════
【设置优先级】
═══════════════════════════════════════════════════════════
⭐ 必须立即设置：条件单1（固定止损）
⭐ 建议立即设置：条件单2、3（固定止盈）
📌 浮盈达到后更新：条件单4、5、6（移动止损阶梯）
📌 每天手动更新：条件单7（跟踪最高价）

═══════════════════════════════════════════════════════════
【提醒】
═══════════════════════════════════════════════════════════
条件单只是辅助工具，不能完全替代人工判断。
但止损条件单必须设置！这是防止你犹豫、防止大亏的最后一道防线。

买入后5分钟内设置好止损条件单，这是你对自己的承诺。
"""
    
    return report


def generate_quick_alert(symbol, name, buy_price, shares, signal_type="一买突破"):
    """快速生成简化版预警参数"""
    
    stop_loss_price = round(buy_price * 0.95, 2)
    profit_20_price = round(buy_price * 1.20, 2)
    profit_30_price = round(buy_price * 1.30, 2)
    sell_20_shares = int(shares * 1/3)
    sell_30_shares = int(shares * 1/3)
    
    quick = f"""
【{symbol} {name} 快速条件单】

止损单：股价 ≤ {stop_loss_price:.2f}元，卖出{shares}股
20%止盈：股价 ≥ {profit_20_price:.2f}元，卖出{sell_20_shares}股
30%止盈：股价 ≥ {profit_30_price:.2f}元，卖出{sell_30_shares}股
移动止损：浮盈10%后上移至成本价，浮盈20%后上移至{buy_price*1.05:.2f}元
跟踪止损：浮盈>30%后，每天更新最高价×0.92

时间止损：买入后10个交易日未盈利，减仓1/2
"""
    return quick


def interactive_mode():
    """交互模式"""
    print("\n" + "="*60)
    print("  同花顺预警条件单生成器")
    print("="*60)
    
    try:
        symbol = input("\n股票代码（如600XXX）：").strip()
        name = input("股票名称：").strip()
        buy_price = float(input("买入价格（元）：").strip())
        shares = int(input("买入数量（股）：").strip())
        
        print("\n信号类型：")
        print("  1. 一买突破  2. 二买回踩  3. 三买加仓")
        signal_choice = input("请选择（1/2/3，默认1）：").strip() or "1"
        signal_map = {"1": "一买突破", "2": "二买回踩", "3": "三买加仓"}
        signal_type = signal_map.get(signal_choice, "一买突破")
        
        print("\n" + "="*60)
        print("  完整版条件单参数（可复制到同花顺）")
        print("="*60)
        
        report = generate_alerts(symbol, name, buy_price, shares, signal_type)
        print(report)
        
        print("\n" + "="*60)
        print("  快速版（简洁摘要）")
        print("="*60)
        quick = generate_quick_alert(symbol, name, buy_price, shares, signal_type)
        print(quick)
        
        save = input("\n是否保存完整版到文件？（y/n，默认y）：").strip().lower() or "y"
        if save == "y":
            filename = f"/Users/zjy/WorkBuddy/2026-06-29-15-15-35/scripts/条件单_{symbol}_{buy_price:.2f}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(report)
                f.write("\n" + "="*60 + "\n")
                f.write(quick)
            print(f"已保存到：{filename}")
        
    except ValueError as e:
        print(f"输入错误：{e}")
    except KeyboardInterrupt:
        print("\n已取消")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        if len(sys.argv) >= 5:
            symbol = sys.argv[2]
            name = sys.argv[3]
            buy_price = float(sys.argv[4])
            shares = int(sys.argv[5])
            signal_type = sys.argv[6] if len(sys.argv) > 6 else "一买突破"
            print(generate_quick_alert(symbol, name, buy_price, shares, signal_type))
        else:
            print("快速模式：python3 alert_generator.py --quick <代码> <名称> <买入价> <股数> [信号类型]")
    else:
        interactive_mode()

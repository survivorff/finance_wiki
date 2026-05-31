"""
外汇远期定价与套息（FX Forward Pricing & Carry）
对应知识库：
  forex/08-深水区/8.1-远期掉期定价.md
  forex/08-深水区/8.2-套息与风险分解.md

演示：
- 覆盖利率平价（CIP）：远期汇率由利率差锁定
- 远期点、掉期点
- 套息交易收益分解（利差 + 汇率变动）
- 套息的"赚小亏大"负偏态

纯 Python 标准库。运行：python3 forex_cip.py

⚠️ 教学用原理级实现，非生产代码。不构成投资建议。
"""

import math


def forward_rate(spot: float, r_quote: float, r_base: float, T: float) -> float:
    """覆盖利率平价（CIP）求远期汇率。
    货币对 base/quote（如 EUR/USD: base=EUR, quote=USD）
    spot: 即期汇率（1 base = spot quote）
    r_quote: 报价货币利率
    r_base: 基础货币利率
    T: 期限（年）
    F = S * (1 + r_quote*T) / (1 + r_base*T)
    """
    return spot * (1 + r_quote * T) / (1 + r_base * T)


def carry_pnl(notional: float, r_high: float, r_low: float,
              spot_change_pct: float, T: float = 1.0) -> dict:
    """套息交易收益分解。
    借低息货币、换高息货币：
      收益 ≈ 利差(carry) + 汇率变动
    notional: 名义本金（以高息货币计）
    r_high/r_low: 高息/低息货币利率
    spot_change_pct: 持有期内高息货币相对低息货币的涨跌幅（如 -0.1 = 高息货币贬值10%）
    """
    carry = notional * (r_high - r_low) * T
    fx_pnl = notional * spot_change_pct
    total = carry + fx_pnl
    return {"carry": carry, "fx_pnl": fx_pnl, "total": total}


def demo():
    print("=" * 60)
    print("外汇远期定价与套息演示")
    print("对应：外汇 8.1 远期掉期定价、8.2 套息风险分解")
    print("=" * 60)

    # ---- 1. CIP 远期定价（文章算例）----
    print("\n[1] 覆盖利率平价（CIP）求远期汇率")
    S = 1.10        # EUR/USD 即期
    r_usd = 0.05    # 报价货币 USD 利率
    r_eur = 0.03    # 基础货币 EUR 利率
    T = 1.0
    F = forward_rate(S, r_usd, r_eur, T)
    print(f"  EUR/USD 即期 S = {S}")
    print(f"  USD 利率 {r_usd*100:.0f}%, EUR 利率 {r_eur*100:.0f}%, 期限 {T} 年")
    print(f"  远期 F = {F:.4f}")
    print(f"  远期点 = (F-S) = {(F-S)*10000:.0f} 个点")
    print(f"  -> USD 利率更高 -> EUR 远期升水（F > S）✓")

    # ---- 2. 无套利验证 ----
    print("\n[2] 无套利验证（两条路径回报相等）")
    usd = 1.0
    path_a = usd * (1 + r_usd * T)                       # 直接存 USD
    eur = usd / S                                         # 换成 EUR
    eur_grown = eur * (1 + r_eur * T)                    # 存 EUR
    path_b = eur_grown * F                                # 用远期换回 USD
    print(f"  路径A（存USD）:           1 USD -> {path_a:.6f} USD")
    print(f"  路径B（换EUR存再远期换回）: 1 USD -> {path_b:.6f} USD")
    print(f"  两条路径相等（差 {abs(path_a-path_b):.2e}）-> 无套利 ✓")

    # ---- 3. 利率差决定远期升贴水 ----
    print("\n[3] 利率差决定远期升贴水")
    print("    USD利率  EUR利率   远期F     方向")
    for ru, re_ in [(0.05, 0.03), (0.03, 0.03), (0.02, 0.05)]:
        f = forward_rate(S, ru, re_, 1.0)
        direction = "EUR升水" if f > S else ("平" if abs(f-S) < 1e-9 else "EUR贴水")
        print(f"    {ru*100:>4.0f}%   {re_*100:>4.0f}%   {f:.4f}   {direction}")
    print("    -> 高息货币(报价)使基础货币远期升水；利率差锁定远期")

    # ---- 4. 套息收益分解 ----
    print("\n[4] 套息交易收益分解（借低息换高息，名义 10000）")
    notional = 10000
    r_high, r_low = 0.08, 0.01    # 高息8% vs 低息1%，利差7%
    print(f"  利差 = {(r_high-r_low)*100:.0f}%/年")
    print("    高息货币涨跌    利差收益   汇率盈亏    总收益")
    for chg in [0.05, 0.0, -0.05, -0.20]:
        r = carry_pnl(notional, r_high, r_low, chg)
        print(f"      {chg*100:>+5.0f}%       {r['carry']:>+7.0f}   {r['fx_pnl']:>+8.0f}   "
              f"{r['total']:>+8.0f}")
    print("    -> 平时赚利差(稳定小钱)，但高息货币暴跌时巨亏（赚小亏大）")

    # ---- 5. 赚小亏大的负偏态 ----
    print("\n[5] 套息的'赚小亏大'（负偏态，像卖保险/卖波动率）")
    print("  正常市场: 多数时间小赚利差")
    print("  危机(risk-off): 高息货币暴跌 + 套息平仓踩踏 -> 巨亏吞掉多年利差")
    # 模拟：10 年里 9 年正常赚利差，1 年危机暴跌
    years_normal = 9
    annual_carry = notional * (r_high - r_low)
    crisis_loss = carry_pnl(notional, r_high, r_low, -0.30)["total"]  # 危机年暴跌30%
    total_10y = years_normal * annual_carry + crisis_loss
    print(f"    9 个正常年: 共赚 {years_normal * annual_carry:+.0f}")
    print(f"    1 个危机年: {crisis_loss:+.0f}（一年亏掉好几年的利差）")
    print(f"    10 年合计:  {total_10y:+.0f}")
    print(f"    -> '在压路机前捡钢镚'：平时捡得欢，被压一次全没")

    print("\n演示结束。改改利率/汇率变动再跑，体会套息的风险收益结构。")


def _tests():
    # CIP：USD 利率高 -> EUR 远期升水
    F = forward_rate(1.10, 0.05, 0.03, 1.0)
    assert F > 1.10
    # 文章算例：1.10 * 1.05/1.03 ≈ 1.1214
    assert abs(F - 1.10 * 1.05 / 1.03) < 1e-9
    assert abs(F - 1.1214) < 1e-3

    # 利率相等 -> 远期=即期
    assert abs(forward_rate(1.10, 0.03, 0.03, 1.0) - 1.10) < 1e-12

    # 报价货币利率低 -> 基础货币远期贴水
    assert forward_rate(1.10, 0.02, 0.05, 1.0) < 1.10

    # 无套利：两条路径相等
    S, ru, re_, T = 1.10, 0.05, 0.03, 1.0
    F = forward_rate(S, ru, re_, T)
    path_a = 1 * (1 + ru * T)
    path_b = (1 / S) * (1 + re_ * T) * F
    assert abs(path_a - path_b) < 1e-9

    # 套息：平时赚利差为正
    r = carry_pnl(10000, 0.08, 0.01, 0.0)
    assert r["carry"] > 0 and abs(r["fx_pnl"]) < 1e-9 and r["total"] > 0
    # 高息货币暴跌 -> 总收益为负（亏损超过利差）
    r2 = carry_pnl(10000, 0.08, 0.01, -0.20)
    assert r2["total"] < 0

    # 负偏态：一个危机年能吞掉多年利差
    annual_carry = 10000 * (0.08 - 0.01)
    crisis = carry_pnl(10000, 0.08, 0.01, -0.30)["total"]
    assert crisis < -3 * annual_carry   # 危机一年亏损 > 3 年利差

    print("forex_cip.py: 全部自检通过 ✓")


if __name__ == "__main__":
    demo()
    print()
    _tests()

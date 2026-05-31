"""
债券定价与收益率（Bond Pricing & Yield）
对应知识库：bonds/08-深水区/8.1-债券定价与收益率.md

演示：
- 债券定价（现金流折现 DCF）
- YTM（到期收益率）数值求解（二分法）
- 麦考利久期、修正久期
- 凸性
- 价格与利率反向关系的验证

纯 Python 标准库。运行：python3 bond_pricing.py

⚠️ 教学用原理级实现，非生产代码。不构成投资建议。
"""


def bond_price(face: float, coupon_rate: float, ytm: float, n: int,
               freq: int = 1) -> float:
    """债券定价：未来现金流按 YTM 折现求和。

    face: 面值
    coupon_rate: 年票息率
    ytm: 年到期收益率
    n: 年数
    freq: 每年付息次数（1=年付, 2=半年付）
    """
    periods = n * freq
    c = face * coupon_rate / freq      # 每期票息
    y = ytm / freq                     # 每期收益率
    price = 0.0
    for t in range(1, periods + 1):
        cf = c + (face if t == periods else 0)   # 最后一期含本金
        price += cf / (1 + y) ** t
    return price


def solve_ytm(price: float, face: float, coupon_rate: float, n: int,
              freq: int = 1) -> float:
    """二分法求 YTM（价格<->收益率单调反向，稳定收敛）。"""
    lo, hi = -0.5, 2.0
    for _ in range(200):
        mid = (lo + hi) / 2
        pv = bond_price(face, coupon_rate, mid, n, freq)
        if pv > price:        # 算出的现值偏高 -> 收益率要调高
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def macaulay_duration(face: float, coupon_rate: float, ytm: float, n: int,
                      freq: int = 1) -> float:
    """麦考利久期 = 现金流现值按时间加权的平均（单位：年）。"""
    periods = n * freq
    c = face * coupon_rate / freq
    y = ytm / freq
    price = bond_price(face, coupon_rate, ytm, n, freq)
    weighted = 0.0
    for t in range(1, periods + 1):
        cf = c + (face if t == periods else 0)
        pv = cf / (1 + y) ** t
        weighted += (t / freq) * pv     # t/freq 换算成"年"
    return weighted / price


def modified_duration(face, coupon_rate, ytm, n, freq=1) -> float:
    """修正久期 = 麦考利久期 / (1 + y/freq)。价格敏感度。"""
    mac = macaulay_duration(face, coupon_rate, ytm, n, freq)
    return mac / (1 + ytm / freq)


def convexity(face, coupon_rate, ytm, n, freq=1) -> float:
    """凸性（久期的二阶修正）。"""
    periods = n * freq
    c = face * coupon_rate / freq
    y = ytm / freq
    price = bond_price(face, coupon_rate, ytm, n, freq)
    s = 0.0
    for t in range(1, periods + 1):
        cf = c + (face if t == periods else 0)
        s += cf * t * (t + 1) / (1 + y) ** (t + 2)
    return s / (price * freq ** 2)


def demo():
    print("=" * 60)
    print("债券定价与收益率演示")
    print("对应：债券 8.1 债券定价与收益率")
    print("=" * 60)

    # ---- 1. 定价（文章算例）----
    print("\n[1] 债券定价（DCF）")
    face, cr, ytm, n = 100, 0.03, 0.05, 3   # 面值100, 票息3%, YTM 5%, 3年
    p = bond_price(face, cr, ytm, n)
    print(f"  面值{face}, 票息率{cr*100:.0f}%, YTM {ytm*100:.0f}%, {n}年期")
    print(f"  价格 = {p:.2f}")
    print(f"  因为 YTM(5%) > 票息率(3%) -> 折价（价格 < 面值）✓")

    # ---- 2. 价格与利率反向 ----
    print("\n[2] 价格与利率反向（核心铁律）")
    print("    YTM      价格")
    for y in [0.01, 0.03, 0.05, 0.07, 0.10]:
        pr = bond_price(face, cr, y, n)
        tag = "（平价）" if abs(y - cr) < 1e-9 else ("（溢价）" if y < cr else "（折价）")
        print(f"    {y*100:>4.0f}%   {pr:7.2f}  {tag}")
    print("    -> 利率涨，价格跌（反向）；YTM=票息率时平价 ✓")

    # ---- 3. YTM 求解 ----
    print("\n[3] YTM 求解（已知价格反解收益率）")
    target_price = 94.55
    y_solved = solve_ytm(target_price, face, cr, n)
    print(f"  已知价格 {target_price} -> 求得 YTM = {y_solved*100:.4f}%")
    print(f"  验证：用该 YTM 定价 = {bond_price(face, cr, y_solved, n):.2f}（应≈{target_price}）")

    # ---- 4. 久期与凸性（文章算例：票息5%, 3年, YTM 6%）----
    print("\n[4] 久期与凸性（面值100, 票息5%, 3年, YTM 6%）")
    f2, cr2, y2, n2 = 100, 0.05, 0.06, 3
    p2 = bond_price(f2, cr2, y2, n2)
    mac = macaulay_duration(f2, cr2, y2, n2)
    mod = modified_duration(f2, cr2, y2, n2)
    conv = convexity(f2, cr2, y2, n2)
    print(f"  价格 = {p2:.2f}")
    print(f"  麦考利久期 = {mac:.4f} 年")
    print(f"  修正久期   = {mod:.4f}")
    print(f"  凸性       = {conv:.4f}")

    # ---- 5. 用久期+凸性估算价格变动 ----
    print("\n[5] 久期/凸性估算 vs 实际（利率上升 1%）")
    dy = 0.01
    # 一阶（久期）估算
    est_dur = -mod * dy
    # 二阶（久期+凸性）估算
    est_dur_conv = -mod * dy + 0.5 * conv * dy ** 2
    # 实际重新定价
    p_new = bond_price(f2, cr2, y2 + dy, n2)
    actual = p_new / p2 - 1
    print(f"  利率 +1%：")
    print(f"    久期估算:      ΔP/P ≈ {est_dur*100:+.4f}%")
    print(f"    久期+凸性估算: ΔP/P ≈ {est_dur_conv*100:+.4f}%")
    print(f"    实际重新定价:  ΔP/P  = {actual*100:+.4f}%")
    print(f"    -> 加凸性修正后更接近实际（正凸性使实际跌得比纯久期估算少）")

    # ---- 6. 久期：长期债更敏感 ----
    print("\n[6] 久期：期限越长，利率风险越大")
    print("    期限      修正久期   (利率+1%的价格变动)")
    for years in [2, 5, 10, 30]:
        md = modified_duration(100, 0.03, 0.03, years)
        print(f"    {years:>2}年      {md:6.2f}      约 {-md*1*1:.2f}%")
    print("    -> 长期债久期长，对利率剧烈敏感（解释 2022 长债大跌）")

    print("\n演示结束。改改票息/期限/利率再跑，观察价格、久期怎么变。")


def _tests():
    # 平价：YTM == 票息率 时，价格 == 面值
    assert abs(bond_price(100, 0.05, 0.05, 5) - 100) < 1e-6

    # 折价/溢价
    assert bond_price(100, 0.03, 0.05, 3) < 100   # YTM>票息 -> 折价
    assert bond_price(100, 0.05, 0.03, 3) > 100   # YTM<票息 -> 溢价

    # 价格与利率反向（单调递减）
    prices = [bond_price(100, 0.03, y, 5) for y in [0.01, 0.03, 0.05, 0.08]]
    assert prices[0] > prices[1] > prices[2] > prices[3]

    # YTM 求解：反解后再定价应一致
    p = bond_price(100, 0.04, 0.06, 7)
    y = solve_ytm(p, 100, 0.04, 7)
    assert abs(y - 0.06) < 1e-5

    # 久期为正且小于到期时间
    mac = macaulay_duration(100, 0.05, 0.06, 3)
    assert 0 < mac < 3
    # 修正久期 < 麦考利久期
    assert modified_duration(100, 0.05, 0.06, 3) < mac

    # 零息债（票息0）的麦考利久期 == 到期时间
    mac_zero = macaulay_duration(100, 0.0, 0.05, 5)
    assert abs(mac_zero - 5) < 1e-6

    # 久期+凸性估算比纯久期更接近实际
    f2, cr2, y2, n2 = 100, 0.05, 0.06, 3
    p2 = bond_price(f2, cr2, y2, n2)
    mod = modified_duration(f2, cr2, y2, n2)
    conv = convexity(f2, cr2, y2, n2)
    dy = 0.01
    actual = bond_price(f2, cr2, y2 + dy, n2) / p2 - 1
    err_dur = abs((-mod * dy) - actual)
    err_dc = abs((-mod * dy + 0.5 * conv * dy ** 2) - actual)
    assert err_dc < err_dur

    # 期限越长久期越长
    ds = [modified_duration(100, 0.03, 0.03, yr) for yr in [2, 5, 10, 30]]
    assert ds[0] < ds[1] < ds[2] < ds[3]

    print("bond_pricing.py: 全部自检通过 ✓")


if __name__ == "__main__":
    demo()
    print()
    _tests()

"""
AMM 定价与无常损失（AMM Pricing & Impermanent Loss）
对应知识库：
  crypto/dex/08-深水区/8.1-AMM数学全解.md
  crypto/dex/08-深水区/8.2-无常损失数学推导.md

演示：
- 恒定乘积 x*y=k 定价、swap 计算、滑点
- 添加流动性 / 移除流动性
- 无常损失公式 IL(r) = 2*sqrt(r)/(1+r) - 1 的推导与验证

纯 Python 标准库。运行：python3 amm_and_impermanent_loss.py

⚠️ 教学用原理级实现，非生产代码。不构成投资建议。
"""

import math


class ConstantProductPool:
    """恒定乘积 AMM 池：x * y = k

    x: token X 储备（如 ETH）
    y: token Y 储备（如 USDC）
    价格（以 Y 计 X）= y / x
    """

    def __init__(self, x: float, y: float, fee: float = 0.003):
        self.x = float(x)
        self.y = float(y)
        self.fee = fee          # 手续费率，如 0.3%
        self.total_lp = math.sqrt(x * y)   # 初始 LP 份额 = 几何平均（见 8.1）
        self.k0 = x * y

    def price(self) -> float:
        """即时价格（无穷小交易的价格）= y / x。"""
        return self.y / self.x

    def spot_value_in_y(self) -> float:
        """池子总价值（以 Y 计）。"""
        return self.x * self.price() + self.y

    # ---- swap：用 dx 个 X 换出 dy 个 Y（含手续费）----
    def swap_x_for_y(self, dx: float) -> dict:
        assert dx > 0
        price_before = self.price()
        dx_eff = dx * (1 - self.fee)              # 扣手续费后参与计算
        # 恒定乘积：(x + dx_eff)(y - dy) = x*y  =>  dy = y*dx_eff/(x+dx_eff)
        dy = self.y * dx_eff / (self.x + dx_eff)
        self.x += dx                               # 全额 dx 进池（含费），费留池里给 LP
        self.y -= dy
        price_after = self.price()
        avg_price = dx / dy                        # 有效成交均价（付出X/得到Y）
        # 滑点：有效均价 vs 即时价的偏离
        slippage = abs(avg_price - 1 / price_before) / (1 / price_before)
        return {
            "dx_in": dx, "dy_out": dy,
            "price_before": price_before, "price_after": price_after,
            "avg_price_X_in_Y": dy / dx,    # 1 个 X 实际换到多少 Y
            "slippage": slippage,
        }

    def swap_y_for_x(self, dy: float) -> dict:
        assert dy > 0
        dy_eff = dy * (1 - self.fee)
        dx = self.x * dy_eff / (self.y + dy_eff)
        self.y += dy
        self.x -= dx
        return {"dy_in": dy, "dx_out": dx, "price_after": self.price()}

    # ---- 流动性 ----
    def add_liquidity(self, dx: float, dy: float) -> float:
        """按比例添加流动性，返回新铸造的 LP 份额。"""
        lp_minted = min(dx / self.x, dy / self.y) * self.total_lp
        self.x += dx
        self.y += dy
        self.total_lp += lp_minted
        return lp_minted

    def remove_liquidity(self, lp: float) -> tuple[float, float]:
        share = lp / self.total_lp
        dx = self.x * share
        dy = self.y * share
        self.x -= dx
        self.y -= dy
        self.total_lp -= lp
        return dx, dy


def impermanent_loss(price_ratio: float) -> float:
    """无常损失公式（恒定乘积池，相对 HODL）。
    price_ratio r = 新价格 / 初始价格
    IL(r) = 2*sqrt(r)/(1+r) - 1   （恒 <= 0）
    见 DEX 8.2 推导。
    """
    r = price_ratio
    return 2 * math.sqrt(r) / (1 + r) - 1


def demo():
    print("=" * 60)
    print("AMM 定价与无常损失演示")
    print("对应：DEX 8.1 AMM数学、8.2 无常损失推导")
    print("=" * 60)

    # ---- 1. x*y=k 定价与滑点 ----
    print("\n[1] 恒定乘积 x*y=k 定价与滑点")
    pool = ConstantProductPool(x=10, y=20000, fee=0.0)  # 10 ETH, 20000 USDC，先不收费
    print(f"  初始池: {pool.x} ETH, {pool.y} USDC, 即时价 = {pool.price():.2f} USDC/ETH")
    print(f"  k = {pool.k0:.0f}")

    # 卖 1 ETH（用 1 ETH 换 USDC）—— 对应文章算例
    res = pool.swap_x_for_y(1)
    print(f"\n  卖出 1 ETH:")
    print(f"    换得 USDC = {res['dy_out']:.2f}（即时价 2000 的话理论上想要 2000）")
    print(f"    有效均价 = {res['avg_price_X_in_Y']:.2f} USDC/ETH（< 2000，这就是滑点）")
    print(f"    滑点 ≈ {res['slippage']*100:.2f}%")
    print(f"    价格从 {res['price_before']:.2f} 变到 {res['price_after']:.2f}")

    # ---- 2. 滑点 ≈ 交易量/池子深度 ----
    print("\n[2] 滑点 ≈ 交易量 / 池子深度（池子越大滑点越小）")
    for size in [0.1, 1, 5]:
        p = ConstantProductPool(x=10, y=20000, fee=0.0)
        r = p.swap_x_for_y(size)
        print(f"    卖 {size:>4} ETH（占池 {size/10*100:.0f}%）-> 滑点 {r['slippage']*100:5.2f}%")

    # ---- 3. 套利者校准价格 ----
    print("\n[3] 套利者把池价拉回外部市场价")
    p = ConstantProductPool(x=10, y=20000, fee=0.0)  # 池价 2000
    print(f"    外部市场 ETH = 2100，但池价 = {p.price():.2f}（偏低）")
    # 套利者来买便宜的 ETH（用 USDC 换 ETH），直到池价≈2100
    # 目标：y/x = 2100 且 x*y=k=200000 -> x=sqrt(k/2100), y=sqrt(k*2100)
    k = p.x * p.y
    target_x = math.sqrt(k / 2100)
    dy_needed = math.sqrt(k * 2100) - p.y
    p.swap_y_for_x(dy_needed)
    print(f"    套利者投入 {dy_needed:.2f} USDC 买 ETH 后，池价 = {p.price():.2f}（≈2100）")
    print(f"    -> 套利让池价校准到市场价（这也是无常损失的来源）")

    # ---- 4. 无常损失 ----
    print("\n[4] 无常损失 IL(r) = 2√r/(1+r) - 1（相对 HODL）")
    print("    价格变化倍数 r    无常损失")
    for r in [1.0, 1.25, 1.5, 2.0, 3.0, 4.0, 5.0, 0.5]:
        il = impermanent_loss(r)
        print(f"      r = {r:<5}      {il*100:7.2f}%")
    print("    -> 价格偏离越大，IL 越大；涨跌对称（r=2 和 r=0.5 相同）；永远≤0")

    # ---- 5. 数值验证：LP 价值 vs HODL ----
    print("\n[5] 数值验证：当 LP vs 直接 HODL（价格翻倍 r=2）")
    p = ConstantProductPool(x=10, y=20000, fee=0.0)  # 初始价 2000
    x0, y0, price0 = p.x, p.y, p.price()
    # 价格翻倍到 4000：套利者交易使池子达到新均衡
    new_price = 4000.0
    k = p.x * p.y
    p.x = math.sqrt(k / new_price)
    p.y = math.sqrt(k * new_price)
    lp_value = p.x * new_price + p.y           # LP 现在的价值（按新价计）
    hodl_value = x0 * new_price + y0           # 当初不动的价值
    il_actual = lp_value / hodl_value - 1
    il_formula = impermanent_loss(new_price / price0)
    print(f"    HODL 价值 = {hodl_value:.2f} USDC")
    print(f"    LP   价值 = {lp_value:.2f} USDC")
    print(f"    实测无常损失 = {il_actual*100:.4f}%")
    print(f"    公式无常损失 = {il_formula*100:.4f}%（应一致）")

    print("\n演示结束。改改池子大小/价格倍数再跑，观察滑点和无常损失。")


def _tests():
    # 恒定乘积 swap 正确性：(x+dx)(y-dy)=k（无手续费时）
    p = ConstantProductPool(x=10, y=20000, fee=0.0)
    k = p.x * p.y
    p.swap_x_for_y(1)
    assert abs(p.x * p.y - k) < 1e-6   # k 守恒

    # 文章算例：卖 1 ETH 得 20000/11 ≈ 1818.18
    p = ConstantProductPool(x=10, y=20000, fee=0.0)
    r = p.swap_x_for_y(1)
    assert abs(r["dy_out"] - 20000 / 11) < 1e-6

    # 无常损失：r=1 时 IL=0
    assert abs(impermanent_loss(1.0)) < 1e-12
    # r=2 时 IL ≈ -5.72%
    assert abs(impermanent_loss(2.0) - (-0.0572)) < 1e-3
    # 对称性：IL(r) == IL(1/r)
    assert abs(impermanent_loss(2.0) - impermanent_loss(0.5)) < 1e-12
    # 永远 <= 0
    for r in [0.1, 0.5, 1.0, 2.0, 10.0]:
        assert impermanent_loss(r) <= 1e-12

    # 实测无常损失 == 公式（价格翻倍）
    p = ConstantProductPool(x=10, y=20000, fee=0.0)
    x0, y0, price0 = p.x, p.y, p.price()
    new_price = 4000.0
    k = p.x * p.y
    p.x = math.sqrt(k / new_price); p.y = math.sqrt(k * new_price)
    lp_value = p.x * new_price + p.y
    hodl_value = x0 * new_price + y0
    assert abs((lp_value / hodl_value - 1) - impermanent_loss(new_price / price0)) < 1e-9

    # 滑点随交易量增大
    s = []
    for size in [0.1, 1, 5]:
        pp = ConstantProductPool(x=10, y=20000, fee=0.0)
        s.append(pp.swap_x_for_y(size)["slippage"])
    assert s[0] < s[1] < s[2]

    print("amm_and_impermanent_loss.py: 全部自检通过 ✓")


if __name__ == "__main__":
    demo()
    print()
    _tests()

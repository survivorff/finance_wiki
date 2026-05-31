"""
玩具撮合引擎（Toy Matching Engine）
对应知识库：crypto/cex/08-深水区/8.1-撮合引擎实现细节.md

演示：
- 价格-时间优先（price-time priority）的订单簿撮合
- 限价单 / 市价单
- 整数价格（避免浮点误差，金融系统铁律）
- 成交记录、盘口深度

纯 Python 标准库，无需任何依赖。运行：python3 matching_engine.py

⚠️ 教学用原理级实现，非生产代码（无并发/持久化/恢复/各种边界处理）。
"""

from collections import deque
from dataclasses import dataclass, field
from typing import Optional
import itertools


# ---- 数据结构 ----

# 价格、数量一律用整数（最小单位）表示，杜绝浮点误差（见文章铁律）。
# 例如价格以"分"为单位，数量以"最小交易单位"为单位。

@dataclass
class Order:
    id: int
    side: str          # "BUY" or "SELL"
    price: int         # 限价（整数，最小单位）。市价单此处为 None 之外的占位
    quantity: int      # 剩余数量
    timestamp: int     # 全局递增序号（时间优先）
    is_market: bool = False


@dataclass
class Trade:
    price: int
    quantity: int
    taker_id: int
    maker_id: int


class OrderBook:
    """价格-时间优先订单簿。

    bids: 价格 -> 该价位的订单队列（FIFO，时间优先）
    asks: 同上
    用普通 dict + 排序获取最优价（教学清晰；生产用价格档位数组/树，见文章）。
    """

    def __init__(self):
        self.bids: dict[int, deque[Order]] = {}
        self.asks: dict[int, deque[Order]] = {}
        self.order_map: dict[int, Order] = {}   # order_id -> Order（O(1) 撤单定位）
        self._seq = itertools.count(1)          # 全局递增序号（定序器，见文章）

    def _next_seq(self) -> int:
        return next(self._seq)

    def best_bid(self) -> Optional[int]:
        live = [p for p, q in self.bids.items() if q]
        return max(live) if live else None

    def best_ask(self) -> Optional[int]:
        live = [p for p, q in self.asks.items() if q]
        return min(live) if live else None

    # ---- 核心撮合逻辑（限价单为例，市价单通过去掉价格约束实现）----

    def submit(self, side: str, price: Optional[int], quantity: int,
               is_market: bool = False) -> tuple[list[Trade], Optional[int]]:
        """提交一个订单，返回 (成交列表, 剩余挂单的 order_id 或 None)。"""
        assert side in ("BUY", "SELL")
        assert quantity > 0
        order = Order(
            id=self._next_seq(),
            side=side,
            price=price if price is not None else (10**18 if side == "BUY" else 0),
            quantity=quantity,
            timestamp=self._next_seq(),
            is_market=is_market,
        )
        trades: list[Trade] = []

        if side == "BUY":
            book = self.asks
            # 只要还有量，且对手盘最优卖价 <= 我的限价（市价单则无价格约束）
            while order.quantity > 0:
                best = self.best_ask()
                if best is None:
                    break
                if (not is_market) and best > order.price:
                    break
                self._match_at_level(book, best, order, trades, taker_is_buy=True)
        else:  # SELL
            book = self.bids
            while order.quantity > 0:
                best = self.best_bid()
                if best is None:
                    break
                if (not is_market) and best < order.price:
                    break
                self._match_at_level(book, best, order, trades, taker_is_buy=False)

        # 剩余量挂入盘口（市价单不挂单，直接放弃剩余）
        resting_id = None
        if order.quantity > 0 and not is_market:
            level = (self.bids if side == "BUY" else self.asks).setdefault(order.price, deque())
            level.append(order)
            self.order_map[order.id] = order
            resting_id = order.id
        return trades, resting_id

    def _match_at_level(self, book, price, taker, trades, taker_is_buy):
        """在某个价位的队列里按时间优先逐个撮合。"""
        queue = book[price]
        while queue and taker.quantity > 0:
            maker = queue[0]
            fill = min(taker.quantity, maker.quantity)
            # 成交价 = maker（挂单方）的价格（价格优先的体现，见文章）
            trades.append(Trade(
                price=price,
                quantity=fill,
                taker_id=taker.id,
                maker_id=maker.id,
            ))
            taker.quantity -= fill
            maker.quantity -= fill
            if maker.quantity == 0:
                queue.popleft()
                self.order_map.pop(maker.id, None)
        if not queue:
            del book[price]

    def cancel(self, order_id: int) -> bool:
        """O(1) 定位 + 撤单。"""
        order = self.order_map.get(order_id)
        if order is None:
            return False
        book = self.bids if order.side == "BUY" else self.asks
        level = book.get(order.price)
        if level and order in level:
            level.remove(order)
            if not level:
                del book[order.price]
        self.order_map.pop(order_id, None)
        return True

    def depth(self):
        """返回盘口深度快照（用于展示）。"""
        bids = sorted(((p, sum(o.quantity for o in q)) for p, q in self.bids.items()),
                      reverse=True)
        asks = sorted((p, sum(o.quantity for o in q)) for p, q in self.asks.items())
        return bids, asks


# ---- 演示 ----

def demo():
    print("=" * 60)
    print("玩具撮合引擎演示（价格-时间优先订单簿）")
    print("对应：CEX 8.1 撮合引擎实现细节")
    print("=" * 60)

    book = OrderBook()

    # 挂入一批卖单（asks）和买单（bids），构建盘口
    # 价格用整数（如以分为单位：10001 = 100.01 元）
    print("\n[1] 挂入限价单构建盘口：")
    book.submit("SELL", 10050, 15)   # 卖 15 @ 100.50
    book.submit("SELL", 10030, 10)   # 卖 10 @ 100.30
    book.submit("SELL", 10010, 20)   # 卖 20 @ 100.10
    book.submit("BUY", 9990, 20)     # 买 20 @ 99.90
    book.submit("BUY", 9970, 10)     # 买 10 @ 99.70

    bids, asks = book.depth()
    print(f"  卖盘 asks(低->高): {asks}")
    print(f"  买盘 bids(高->低): {bids}")
    print(f"  最优买价={book.best_bid()}  最优卖价={book.best_ask()}  "
          f"价差={book.best_ask() - book.best_bid()}")

    # 一个限价买单吃单：买 25 @ 100.30 -> 应吃掉 100.10 的 20 + 100.30 的 5
    print("\n[2] 提交限价买单：买 25 @ 100.30（应吃掉 100.10×20 + 100.30×5）")
    trades, resting = book.submit("BUY", 10030, 25)
    for t in trades:
        print(f"  成交：数量 {t.quantity} @ {t.price/100:.2f}  "
              f"(taker={t.taker_id}, maker={t.maker_id})")
    total = sum(t.quantity for t in trades)
    print(f"  共成交 {total}（剩余挂单 id={resting}）")

    bids, asks = book.depth()
    print(f"  撮合后卖盘: {asks}")
    print(f"  撮合后买盘: {bids}")

    # 市价卖单：卖 30，按盘口最优买价逐档吃
    print("\n[3] 提交市价卖单：卖 30（按最优买价逐档吃）")
    trades, _ = book.submit("SELL", None, 30, is_market=True)
    for t in trades:
        print(f"  成交：数量 {t.quantity} @ {t.price/100:.2f}")
    print(f"  共成交 {sum(t.quantity for t in trades)}")

    print("\n演示结束。改改价格/数量再跑，观察撮合怎么变。")


# ---- 自检（断言）----

def _tests():
    # 测试1：基本撮合，成交价取 maker 价
    b = OrderBook()
    b.submit("SELL", 100, 10)            # maker 卖 10 @ 100
    trades, _ = b.submit("BUY", 105, 4)  # taker 买 4，限价 105
    assert len(trades) == 1
    assert trades[0].price == 100        # 成交价 = maker 的 100，不是 taker 的 105
    assert trades[0].quantity == 4

    # 测试2：价格优先 + 时间优先
    b = OrderBook()
    b.submit("SELL", 101, 5)             # 较差价
    b.submit("SELL", 100, 5)             # 最优价，先到
    b.submit("SELL", 100, 5)             # 最优价，后到
    trades, _ = b.submit("BUY", 101, 8)  # 吃 8
    # 应先吃 100（价格优先），同价位先吃先到的（时间优先）
    assert trades[0].price == 100 and trades[0].quantity == 5
    assert trades[1].price == 100 and trades[1].quantity == 3
    # 100 这档还剩 2（后到的那笔），所以最优卖价仍是 100
    assert b.best_ask() == 100
    bids_ignore, asks = b.depth()
    assert asks == [(100, 2), (101, 5)]  # 100 剩 2，101 没动

    # 测试3：限价不满足则挂单，不成交
    b = OrderBook()
    b.submit("SELL", 100, 5)
    trades, resting = b.submit("BUY", 99, 5)  # 出价 99 < 卖价 100，不成交
    assert trades == []
    assert resting is not None
    assert b.best_bid() == 99 and b.best_ask() == 100

    # 测试4：撤单
    b = OrderBook()
    _, rid = b.submit("BUY", 99, 5)
    assert b.best_bid() == 99
    assert b.cancel(rid) is True
    assert b.best_bid() is None

    # 测试5：市价单扫多档
    b = OrderBook()
    b.submit("SELL", 100, 5)
    b.submit("SELL", 101, 5)
    trades, _ = b.submit("BUY", None, 8, is_market=True)
    assert sum(t.quantity for t in trades) == 8
    assert trades[0].price == 100 and trades[1].price == 101

    print("matching_engine.py: 全部自检通过 ✓")


if __name__ == "__main__":
    demo()
    print()
    _tests()

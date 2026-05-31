# 可运行代码示例（Runnable Code）

> 把知识库深水区的原理，变成**能跑起来的代码**。
> 纯 Python 标准库实现，无需安装任何依赖，直接运行即可看到结果。

每个脚本对应知识库某篇深水区文章，是「从理解到能造」的桥梁。

## 运行方式

```bash
# 需要 Python 3.8+（无需 pip install 任何东西）
python3 code/matching_engine.py
python3 code/amm_and_impermanent_loss.py
python3 code/bond_pricing.py
python3 code/forex_cip.py

# 运行自带的自检测试
python3 code/run_all_tests.py
```

## 脚本清单

| 脚本 | 对应文章 | 演示什么 |
| --- | --- | --- |
| [`matching_engine.py`](./matching_engine.py) | [CEX 8.1 撮合引擎](../crypto/cex/08-深水区/8.1-撮合引擎实现细节.md) | 一个能跑的玩具撮合引擎（价格-时间优先订单簿） |
| [`amm_and_impermanent_loss.py`](./amm_and_impermanent_loss.py) | [DEX 8.1 AMM 数学](../crypto/dex/08-深水区/8.1-AMM数学全解.md)、[8.2 无常损失](../crypto/dex/08-深水区/8.2-无常损失数学推导.md) | x*y=k 定价、滑点、无常损失计算 |
| [`bond_pricing.py`](./bond_pricing.py) | [债券 8.1 定价与收益率](../bonds/08-深水区/8.1-债券定价与收益率.md) | 债券定价、YTM 求解、久期、凸性 |
| [`forex_cip.py`](./forex_cip.py) | [外汇 8.1 远期掉期定价](../forex/08-深水区/8.1-远期掉期定价.md) | 覆盖利率平价、远期汇率、套息收益 |
| [`run_all_tests.py`](./run_all_tests.py) | — | 运行所有脚本的自检断言 |

## 重要说明 ⚠️

> 这些代码是**教学用的"原理级"实现**，目标是让你**亲手验证深水区的数学**，
> 看到"输入→输出"，建立对机制的直觉。
> **绝不是生产级代码**（缺少并发、持久化、安全、边界处理、性能优化等）。
> 真实系统的每个子系统都是团队的多年工程。**不构成任何投资建议。**

## 设计原则

- **零依赖**：纯 Python 标准库，clone 下来就能跑。
- **自带断言**：每个脚本末尾有 `assert` 自检，验证结果正确。
- **可读优先**：代码注释详尽，对照知识库文章阅读。
- **可玩**：改改参数（价格、利率、池子大小），看结果怎么变。

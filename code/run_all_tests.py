"""
运行所有代码示例的自检测试。
运行：python3 code/run_all_tests.py   （或在 code/ 目录下 python3 run_all_tests.py）

每个脚本末尾都有 _tests() 自检函数，这里统一调用。
全部通过则打印总结。
"""

import sys
import os

# 确保能 import 同目录的模块（无论从哪运行）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matching_engine
import amm_and_impermanent_loss
import bond_pricing
import forex_cip


def main():
    print("=" * 60)
    print("运行所有代码示例的自检测试")
    print("=" * 60)
    print()

    modules = [
        ("撮合引擎 (CEX 8.1)", matching_engine),
        ("AMM & 无常损失 (DEX 8.1/8.2)", amm_and_impermanent_loss),
        ("债券定价 (债券 8.1)", bond_pricing),
        ("外汇 CIP & 套息 (外汇 8.1/8.2)", forex_cip),
    ]

    passed = 0
    for name, mod in modules:
        try:
            mod._tests()
            passed += 1
        except AssertionError as e:
            print(f"❌ {name}: 自检失败！{e}")
        except Exception as e:
            print(f"❌ {name}: 出错 {type(e).__name__}: {e}")

    print()
    print("=" * 60)
    if passed == len(modules):
        print(f"✓ 全部 {len(modules)} 个模块自检通过！")
    else:
        print(f"⚠️  {passed}/{len(modules)} 个模块通过")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()

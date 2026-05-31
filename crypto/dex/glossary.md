# DEX 术语表（Glossary）

> 按主题分组的 DEX/DeFi 常用术语。带 ⭐ 的是最核心、最高频的。
> 通用加密术语（KYC、稳定币等）见 [CEX 术语表](../cex/glossary.md)。

## 基础概念
- **DEX（Decentralized Exchange）** ⭐：去中心化交易所，链上合约自动执行，用户自托管。
- **DeFi（Decentralized Finance）** ⭐：去中心化金融，用智能合约重建金融功能。
- **自托管 / Non-custodial** ⭐：用户自己掌握私钥，资产不交给中介。
- **智能合约 / Smart Contract** ⭐：部署在链上、自动执行、（通常）不可篡改的代码。
- **可组合性 / Composability** ⭐：协议像乐高一样自由拼接（货币乐高）。
- **TVL（Total Value Locked）** ⭐：锁定在协议里的总资产，衡量规模。
- **协议 vs 前端**：链上合约（去中心化）vs 网页（中心化，可被封）。

## AMM 与流动性
- **AMM（自动做市商）** ⭐：用公式+资金池定价，替代订单簿。
- **恒定乘积 / x*y=k** ⭐：最经典的 AMM 公式。
- **流动性池 / Liquidity Pool** ⭐：存两种币供交易的资金池。
- **LP（流动性提供者）** ⭐：把币存入池子赚手续费的人（人人版做市商）。
- **LP Token**：代表 LP 在池子中份额的凭证。
- **滑点 / Slippage** ⭐：交易量/池深决定的价格偏差。
- **无常损失 / Impermanent Loss (IL)** ⭐：当 LP 相比 HODL 少赚的部分。
- **LVR（Loss-Versus-Rebalancing）**：LP 相比主动做市少赚的更精确度量。
- **集中流动性 / Concentrated Liquidity** ⭐：V3 让 LP 在价格区间内做市，提升资本效率。
- **StableSwap**：Curve 用于等价资产的低滑点曲线。
- **tick**：V3 把价格离散化的刻度。
- **流动性挖矿 / Liquidity Mining** ⭐：用代币激励 LP，冷启动流动性。

## 交易与聚合
- **聚合器 / Aggregator** ⭐：路由订单到多个 DEX 找最优价（1inch、Jupiter）。
- **智能路由 / Smart Order Routing**：拆单跨池找最优执行。
- **意图 / Intent** ⭐：用户表达「想要的结果」，求解器竞争实现。
- **求解器 / Solver**：替用户找最优执行方案的专业方。
- **CoW（Coincidence of Wants）**：需求巧合，批量撮合 P2P 订单。
- **询价 / RFQ**：做市商响应报价请求的模式。

## MEV
- **MEV（Maximal Extractable Value）** ⭐：利用区块内交易排序提取的价值。
- **抢跑 / Front-running** ⭐：抢在别人交易前下单获利。
- **夹击 / 三明治攻击 / Sandwich** ⭐：前后夹住受害者交易抽利。
- **回填 / Backrun**：只在目标交易后跟随套利（不伤用户）。
- **搜索者 / Searcher**：寻找 MEV 机会、组装 bundle 的角色。
- **构建者 / Builder**：组装价值最大化区块的角色。
- **PBS（Proposer-Builder Separation）** ⭐：提议者-构建者分离，管理 MEV。
- **Flashbots**：MEV 基础设施（私有通道、MEV-Boost）。
- **私有交易通道**：交易不进公开内存池，防夹击。

## 衍生品
- **衍生品 DEX**：链上永续/期权（Hyperliquid、GMX、dYdX）。
- **预言机型永续**：用预言机喂价 + LP 池对手盘（GMX 型）。
- **vAMM（虚拟 AMM）**：用 AMM 曲线定永续价格（早期方案）。
- **清算人 / Liquidator**：监控并执行链上清算赚奖励的机器人。
- （资金费率/保证金/强平/标记价见 [CEX 术语表](../cex/glossary.md)）

## 技术与基础设施
- **EVM**：以太坊虚拟机，运行智能合约。
- **Gas** ⭐：执行链上交易的燃料费，用原生币付。
- **内存池 / Mempool** ⭐：待打包交易的公开等待区（MEV 的土壤）。
- **预言机 / Oracle** ⭐：把链外数据（价格）喂上链。
- **TWAP**：时间加权平均价，抗操纵的预言机方案。
- **Chainlink / Pyth**：主流预言机网络。
- **闪电贷 / Flash Loan** ⭐：同一交易内无抵押借还，否则回滚。
- **跨链桥 / Bridge** ⭐：在链之间转移资产（被黑重灾区）。
- **RPC 节点**：钱包/DApp 连接链的入口（Infura/Alchemy）。
- **索引器 / Indexer**：整理链上数据供查询（The Graph）。
- **链抽象 / Chain Abstraction**：对用户隐藏多链复杂性。

## 钱包与安全
- **私钥 / 助记词 / Seed Phrase** ⭐：资产控制权，丢失/泄露不可恢复。
- **授权 / Approve** ⭐：允许合约动用你代币的权限（盗币高发口）。
- **无限授权 / Unlimited Approval** ⚠️：授权极大额度，高危。
- **Permit / Permit2**：链下签名授权（钓鱼常利用）。
- **账户抽象 / AA（ERC-4337）** ⭐：可编程智能合约钱包（社交恢复、Gas 代付等）。
- **社交恢复**：靠亲友/多设备恢复钱包。
- **硬件钱包**：私钥离线的钱包（Ledger/Trezor）。
- **重入攻击 / Reentrancy** ⭐：经典合约漏洞（The DAO）。

## 骗局
- **貔貅盘 / Honeypot** ⭐：能买不能卖的骗局币。
- **Rug Pull** ⭐：撤池/砸盘卷款跑路。
- **钓鱼 / Phishing** ⭐：假网站/假空投/假客服骗签名或私钥。
- **女巫攻击 / Sybil**：一人多钱包骗空投。
- **拉高出货 / Pump & Dump**：拉盘后砸给散户。
- **流动性锁定 / Locked Liquidity**：锁住流动性防 Rug 的措施。

## 治理与代币
- **治理代币 / Governance Token** ⭐：代表协议治理权（UNI/CRV）。
- **DAO** ⭐：去中心化自治组织，代币持有者投票治理。
- **ve 模型 / vote-escrowed** ⭐：锁仓换更大投票权和收益。
- **空投 / Airdrop** ⭐：免费发代币（获客+去中心化分发）。
- **积分 / Points**：空投的可控升级版。
- **流动性战争 / Liquidity Wars**：争夺流动性激励分配权（Curve 战争）。
- **贿选 / Bribes**：花钱买治理投票（公开市场化）。
- **吸血鬼攻击 / Vampire Attack**：复制对手+代币激励抢流动性（Sushi vs Uniswap）。
- **费用开关 / Fee Switch**：是否把协议手续费分给代币持有者。
- **真实收益 / Real Yield**：用真实手续费而非通胀代币分给 LP。

## 代表项目
- **Uniswap**：AMM 鼻祖与龙头。**Curve**：稳定币 AMM 之王。
- **PancakeSwap**：BSC 龙头。**Hyperliquid**：链上订单簿永续黑马。
- **dYdX**：老牌衍生品 DEX。**GMX**：预言机型永续。
- **Jupiter**：Solana 聚合器入口。**1inch / CoW**：以太坊聚合器。

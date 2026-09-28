# Project Charter — 8/10 A股量化平台

## 成功定义

### 量化学习 8/10

项目拥有从数据、因子、组合、回测、风险到执行的清晰边界；关键公式和交易规则有文档、测试和可复现实例。维护者能解释信号时间、可成交时间、PIT 数据、费用、benchmark、alpha/beta、IC、walk-forward、OMS 和 reconciliation。

### 策略研究 8/10

- point-in-time 数据和历史股票池
- 确定性回测
- 成本、滑点、成交约束
- benchmark 和风险归因
- 因子 IC/RankIC/ICIR、分层、衰减、换手
- 样本外 / walk-forward
- 可复现实验清单
- 参数稳定性与多重试验记录

### 直接实盘工程能力 8/10

- broker-agnostic OMS
- 幂等下单和完整状态机
- 持久化、重启恢复和事件重放
- pre/post-trade 风控
- broker 对账
- stale-data / disconnect / duplicate event 处理
- shadow、paper、manual-approval、kill-switch
- 结构化日志、监控、报警、runbook
- 受控小资金发布门槛

## 非目标

V1.0 不追求：

- 高频、tick 级、微秒低延迟
- 融资融券、做空、期权、期货
- 自动资金划转
- 无监督的全自动真钱交易
- 依赖单一“AI模型”保证收益
- 机构级多账户与百亿容量

## 版本路线

- V0.1：foundation + domain
- V0.2：data + deterministic backtest
- V0.3：A股规则 + metrics + baseline strategies
- V0.4：factor lab + portfolio/risk
- V0.5：ML/Qlib + walk-forward
- V0.6：OMS + paper
- V0.8：live gateway + broker adapter + observability
- V1.0：独立审计和受控发布

## 发布原则

每个 Phase 一个 branch/PR。实施会话和 review 会话分开。只有 reviewer 给出 GO、当前阶段没有未解决的 P0/P1 finding 且关键验收无 BLOCKED，才能进入下一阶段。已登记的旧代码风险仅可按质量门槛的隔离与递延规则处理；Phase 14 发布前不得留有未解决的 P0/P1 风险。

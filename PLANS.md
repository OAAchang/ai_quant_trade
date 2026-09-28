# Project Plans

本文件是 `OAAchang/ai_quant_trade` 从上游学习型仓库迁移为个人 A 股量化研究与受控交易平台的路线索引。项目范围、默认安全边界和成功定义分别见 `docs/PROJECT_CONTEXT.md` 与 `docs/PROJECT_CHARTER.md`。

## Delivery policy

- 每个 Phase 使用独立分支、计划、状态报告和 acceptance matrix。
- 实施与首轮 Review 使用独立会话；首轮 Review 只读，不顺手修改。
- 当前阶段未解决的 P0/P1 review finding、该阶段关键验收 BLOCKED、未运行的必需验证或缺失证据均阻止进入下一阶段。已登记的旧代码/后续阶段风险仅在触发路径与新核心、CI、实盘隔离且有责任阶段和控制门槛时递延；当前改动一旦暴露该风险即成为阻断项，Phase 14 发布前不得留有未解决 P0/P1。
- `live` 始终默认关闭；没有正式券商文档、授权 sandbox、人工批准和发布门槛时不得实现或调用真实下单。
- 旧目录是 upstream/reference。新核心逐步进入 `src/ai_quant_trade/`，不得通过一次性重写替换旧仓库。

## Phase roadmap

| Phase | Scope | Status | Gate |
|---|---|---|---|
| 00 | Fork、现状审计与治理基线 | COMPLETE; PR #1 user-merged into Main | GO obtained and merge verified |
| 01 | 新工程骨架、依赖与 CI | Independent Review GO and hosted CI PASS; PR #2 awaits user merge | User PR merge and Main tree verification |
| 02 | 领域模型、账户账本与不变量 | NOT STARTED | Phase 01 GO, user merge of PR #2, verified Main tree |
| 03 | 市场数据、PIT 与历史股票池 | NOT STARTED | Phase 02 GO |
| 04 | 确定性事件驱动回测 | NOT STARTED | Phase 03 GO |
| 05 | A 股规则、费用、滑点与成交 | NOT STARTED | Phase 04 GO |
| 06 | 指标、Benchmark、报告与基线策略 | NOT STARTED | Phase 05 GO |
| 07 | 因子研究实验室 | NOT STARTED | Phase 06 GO |
| 08 | 组合构建与三层风控 | NOT STARTED | Phase 07 GO |
| 09 | Walk-forward、ML 与 Qlib adapter | NOT STARTED | Phase 08 GO |
| 10 | OMS、持久化、恢复与 Paper | NOT STARTED | Phase 09 GO |
| 11 | Broker-agnostic gateway 与 Shadow | NOT STARTED | Phase 10 GO |
| 12 | 指定券商 adapter 与 sandbox | BLOCKED — broker/docs/sandbox undecided | Official docs and authorized sandbox |
| 13 | 可观测性、安全、部署与运维 | NOT STARTED | Phase 12 GO |
| 14 | 独立端到端审计与受控发布 | NOT STARTED | Phase 13 GO and paper evidence |

## Current execution

- Branch: `phase-01-foundation-ci`
- Plan: `docs/plans/PHASE_01_PLAN.md`
- Status: `docs/status/PHASE_01.md`
- Required next action: user reviews and merges Phase 01 PR #2 into the personal Fork's `Main`; verify its merged tree before any Phase 02 work.

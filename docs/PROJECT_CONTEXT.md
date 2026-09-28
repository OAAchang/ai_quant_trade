# Project Context

在开始 Phase 00 前填写；后续所有 Codex 会话都先读取本文件。

```yaml
project_name: ai_quant_trade
python_package: ai_quant_trade
repository: OAAchang/ai_quant_trade
base_branch: Main
upstream_repository: charliedream1/ai_quant_trade
target_market: CN_A
primary_timezone: Asia/Shanghai
base_currency: CNY

development:
  operating_system: macOS 26.5.2
  python_version: "3.11"
  package_manager: uv
  database_dev: sqlite
  database_live: postgresql
  container_runtime: docker

data:
  primary_provider: UNDECIDED
  backup_provider: UNDECIDED
  benchmark_provider: UNDECIDED
  local_research_store: parquet_duckdb

broker:
  name: UNDECIDED
  official_api_docs_location: UNDECIDED
  sandbox_available: false
  live_account_enabled: false

trading_scope:
  frequency: daily
  asset_scope: cash_equities
  direction: long_only
  leverage: false
  short_selling: false
  margin_financing: false
  derivatives: false

risk_defaults:
  live_trading_default: disabled
  manual_approval_required: true
  max_single_name_weight: 0.10
  max_industry_weight: 0.30
  max_gross_exposure: 0.90
  minimum_cash_buffer: 0.10
```

## 固定决策

- 原仓库只作为 upstream/reference；新核心放入独立 package。
- 初始范围是 A 股现金股票、日频/低频、只做多、不加杠杆。
- 先通过 backtest 和 paper，再允许 broker-specific live adapter。
- 没有正式券商 API 文档和授权测试环境时，不实现猜测式真实适配器。
- 所有实盘功能默认关闭。

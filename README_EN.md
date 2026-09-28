# AI Quantitative Trading Bot  
[**ENGLISH VERSION**](https://github.com/charliedream1/ai_quant_trade/blob/master/README_EN.md)

> **Fork status (Phase 01):** The new Python package is an installable engineering skeleton with settings, logging, and CLI help only; it has no strategy, backtest, or trading capability. This repository retains upstream learning material and historical examples that have not passed the data, trading-rule, risk, OMS, ledger, or broker-reconciliation gates required for live trading. Do not connect these examples to a real account or treat backtest returns as investment advice or a profit guarantee. Live mode is rejected in the new package. See [Phase 01 status](docs/status/PHASE_01.md), [development setup](docs/development/SETUP.md), and [quality gates](docs/acceptance/QUALITY_GATES.md).

[![License](https://img.shields.io/badge/License-Apache%202.0-brightgreen.svg)](https://opensource.org/licenses/Apache-2.0)
[![Target-Python](https://img.shields.io/badge/Target%20Python-3.11-blue)](docs/development/SETUP.md)

## New package quick start

From this personal fork, run `uv python install 3.11.14`, `uv sync --frozen --group dev`, `make all`, and `uv run --frozen --offline ai-quant-trade --help`. The old root `requirements.txt` and example directories are reference material, not part of this install or CI gate.

## Feature
ai_quant_trade aims to integrate stock trading knowledge, strategies and tools. Features of vanilla strategies, 
machine learning, deep learning, reinforcement learning and graph neural network, C++ deployment will all be included.

## 1. [**Local Quantitative Platform**](https://github.com/charliedream1/ai_quant_trade/tree/master/egs_local_strategies)
Egs provided to build local quantitative platform, please check: egs_local_strategies

Strategies List
- Double Moving Average Line


## Discussion
Welcome to start a discussion at [Github Discussions](https://github.com/charliedream1/ai_quant_trade/discussions)


## Technic Support
Welcome to submit a question at [Github Issues](https://github.com/charliedream1/ai_quant_trade/issues)


## Reference

``` bibtex
@misc{ai_quant_trade,
  author={Charlie Lee},
  title={ai_quant_trade},
  year={2022},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/charliedream1/ai_quant_trade}},
}

```

# TradingAgents — Project CLAUDE.md

## Overview
Fork of TauricResearch/TradingAgents (v0.2.3). Multi-agent LLM trading framework with analyst, researcher, trader, and risk management teams.

## Current Work
Adding a **media export pipeline** that transforms raw analysis output into polished formats:
- Blog posts (Gemini API)
- PowerPoint decks (Gemini + python-pptx)
- PDF reports (Gemini + ReportLab)
- Social media posts (Gemini structured output)
- Audio summaries (NotebookLM Enterprise primary, Gemini TTS fallback)

## Stack
- Python 3.13, conda env: `tradingagents`
- LangGraph + LangChain for agent orchestration
- OpenRouter as primary LLM provider (with multi-provider support)
- Alpha Vantage + yfinance for market data
- Google Gemini API for export generation
- NotebookLM Enterprise API for audio overviews

## Key Architecture
- `tradingagents/graph/trading_graph.py` — Main graph, `propagate()` returns `(final_state, decision)`
- `tradingagents/agents/` — All agent definitions (analysts, researchers, trader, risk mgmt)
- `tradingagents/export/` — NEW: Media export pipeline (being built)
- `cli/main.py` — Interactive CLI with Rich UI
- `tradingagents/default_config.py` — Central config dict

## API Keys
- Stored in `~/TradingAgents/.env` (OpenRouter + Alpha Vantage)
- Google API key available in Obsidian vault / macOS Keychain

## Conventions
- Follow existing code patterns (LangGraph node functions, config dict pattern)
- Use immutable config copies (never mutate DEFAULT_CONFIG)
- Keep files < 400 lines; extract utilities when needed

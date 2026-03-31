"""TradingAgents media export pipeline.

Usage:
    from tradingagents.export import export_report

    exports = export_report(
        final_state=final_state,
        ticker="SLF",
        formats=["blog", "pptx", "pdf", "social", "audio"],
        config=config,
    )
"""

from .pipeline import export_report

__all__ = ["export_report"]

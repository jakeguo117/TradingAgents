"""Export pipeline orchestrator."""

import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional

from .schemas import ExportResult


def _build_report_text(final_state: dict, ticker: str) -> str:
    """Build a consolidated report string from the final agent state."""
    sections = []
    header = f"# Trading Analysis Report: {ticker}\n"
    header += f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    sections.append(header)

    if final_state.get("market_report"):
        sections.append(f"## Technical Analysis\n{final_state['market_report']}")
    if final_state.get("sentiment_report"):
        sections.append(f"## Sentiment Analysis\n{final_state['sentiment_report']}")
    if final_state.get("news_report"):
        sections.append(f"## News Analysis\n{final_state['news_report']}")
    if final_state.get("fundamentals_report"):
        sections.append(f"## Fundamentals Analysis\n{final_state['fundamentals_report']}")

    debate = final_state.get("investment_debate_state", {})
    if debate.get("bull_history"):
        sections.append(f"## Bull Case\n{debate['bull_history']}")
    if debate.get("bear_history"):
        sections.append(f"## Bear Case\n{debate['bear_history']}")
    if debate.get("judge_decision"):
        sections.append(f"## Research Manager Decision\n{debate['judge_decision']}")

    if final_state.get("trader_investment_plan"):
        sections.append(f"## Trader Plan\n{final_state['trader_investment_plan']}")

    risk = final_state.get("risk_debate_state", {})
    if risk.get("judge_decision"):
        sections.append(f"## Portfolio Manager Decision\n{risk['judge_decision']}")

    if final_state.get("final_trade_decision"):
        sections.append(f"## Final Decision\n{final_state['final_trade_decision']}")

    return "\n\n".join(sections)


def export_report(
    final_state: dict,
    ticker: str,
    formats: list[str],
    config: Optional[dict] = None,
    output_dir: Optional[Path] = None,
) -> ExportResult:
    """Export a trading analysis to multiple media formats.

    Args:
        final_state: The complete agent state from propagate().
        ticker: Stock ticker symbol.
        formats: List of formats to generate. Options: "blog", "pptx", "pdf", "social", "audio".
        config: Optional config dict with export settings.
        output_dir: Override output directory. Defaults to config["export_dir"]/{ticker}/{date}.

    Returns:
        ExportResult dict with paths/data for each generated format.
    """
    config = config or {}
    model = config.get("export_llm_model", "gemini-2.5-flash")
    tts_model = config.get("export_tts_model", "gemini-2.5-flash-preview-tts")
    audio_provider = config.get("export_audio_provider", "notebooklm")
    language = config.get("export_language", "en")

    if output_dir is None:
        base = config.get("export_dir", "./exports")
        date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        output_dir = Path(base) / ticker / date_str

    output_dir.mkdir(parents=True, exist_ok=True)

    # Build consolidated report text from agent state
    report_text = _build_report_text(final_state, ticker)

    # Prepend language instruction if non-English
    from .prompts import get_language_instruction
    lang_prefix = get_language_instruction(language)
    if lang_prefix:
        report_text = lang_prefix + report_text

    # Save the source report
    (output_dir / "source_report.md").write_text(report_text)

    results: ExportResult = {}
    errors: dict[str, str] = {}

    # Map format names to generator functions (lazy imports to avoid overhead)
    def _run_blog():
        from .blog import generate_blog
        return "blog", generate_blog(report_text, output_dir / "blog", model)

    def _run_social():
        from .social import generate_social
        posts, path = generate_social(report_text, output_dir / "social", model)
        return "social", posts, path

    def _run_pptx():
        from .pptx_gen import generate_pptx
        return "pptx", generate_pptx(report_text, output_dir / "pptx", model)

    def _run_pdf():
        from .pdf_gen import generate_pdf
        return "pdf", generate_pdf(report_text, output_dir / "pdf", model)

    def _run_audio():
        from .audio import generate_audio
        return "audio", generate_audio(
            report_text, output_dir / "audio", audio_provider, model, tts_model
        )

    format_runners = {
        "blog": _run_blog,
        "social": _run_social,
        "pptx": _run_pptx,
        "pdf": _run_pdf,
        "audio": _run_audio,
    }

    # Run non-audio formats in parallel, audio sequentially (it's slower)
    parallel_formats = [f for f in formats if f != "audio" and f in format_runners]
    sequential_formats = [f for f in formats if f == "audio" and f in format_runners]

    # Parallel execution
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(format_runners[fmt]): fmt
            for fmt in parallel_formats
        }
        for future in as_completed(futures):
            fmt = futures[future]
            try:
                result = future.result()
                if fmt == "social":
                    _, posts, path = result
                    results["social"] = posts
                    results["social_json"] = path
                else:
                    _, path = result
                    results[fmt] = path
            except Exception as e:
                errors[fmt] = str(e)
                print(f"Export '{fmt}' failed: {e}")

    # Sequential execution (audio)
    for fmt in sequential_formats:
        try:
            result = format_runners[fmt]()
            _, path = result
            results[fmt] = path
        except Exception as e:
            errors[fmt] = str(e)
            print(f"Export '{fmt}' failed: {e}")

    # Save summary
    summary_lines = ["# Export Summary\n"]
    for fmt in formats:
        if fmt in results:
            value = results[fmt]
            if isinstance(value, Path):
                summary_lines.append(f"- **{fmt}**: {value}")
            else:
                summary_lines.append(f"- **{fmt}**: Generated (see social_posts.json)")
        elif fmt in errors:
            summary_lines.append(f"- **{fmt}**: FAILED — {errors[fmt]}")
    (output_dir / "export_summary.md").write_text("\n".join(summary_lines))

    return results

from __future__ import annotations

import argparse
import html
import json
import sys
import shutil
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
  sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai.update_readme_test_status import resolve_report_path, summarize_report


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file_handle:
        return json.load(file_handle)


def maybe_load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return load_json(path)


def render_list(items: list[str], empty_message: str) -> str:
    if not items:
        return f"<li>{html.escape(empty_message)}</li>"
    return "\n".join(f"<li>{html.escape(item)}</li>" for item in items)


def render_failures(failures: list[dict[str, Any]]) -> str:
    if not failures:
        return "<li>No failed tests in this run.</li>"

    rendered = []
    for failure in failures[:8]:
        title = html.escape(str(failure.get("title", "Unknown test")))
        project = html.escape(str(failure.get("project", "unknown")))
        cause = html.escape(str(failure.get("probable_cause", "No probable cause provided")))
        fix = html.escape(str(failure.get("suggested_fix", "No suggested fix provided")))
        rendered.append(
            f"<li><strong>{title}</strong> [{project}]<br><span>{cause}</span><br><em>{fix}</em></li>"
        )
    return "\n".join(rendered)


def build_index(report_summary: dict[str, int], llm_payload: dict[str, Any] | None) -> str:
    llm_summary = (llm_payload or {}).get("summary", {}) if llm_payload else {}
    llm_context = (llm_payload or {}).get("context", {}) if llm_payload else {}
    headline = html.escape(str(llm_summary.get("headline", "LLM summary unavailable.")))
    executive_summary = html.escape(str(llm_summary.get("executive_summary", "")))
    provider_status = html.escape(str(llm_summary.get("provider_status", "unavailable")))
    model = html.escape(str(llm_summary.get("model", "not set")))

    top_risks = [str(item) for item in llm_summary.get("top_risks", [])]
    next_actions = [str(item) for item in llm_summary.get("next_actions", [])]
    notable_failures = llm_summary.get("notable_failures", [])
    failures = notable_failures if isinstance(notable_failures, list) else []

    total = report_summary.get("total", 0)
    passed = report_summary.get("passed", 0)
    failed = report_summary.get("failed", 0)
    flaky = report_summary.get("flaky", 0)
    timed_out = report_summary.get("timedOut", 0)
    interrupted = report_summary.get("interrupted", 0)
    status = "Passing" if failed == 0 and timed_out == 0 and interrupted == 0 else "Failing"

    actionable_findings = llm_context.get("actionable_findings", []) if isinstance(llm_context, dict) else []
    findings_list = []
    for finding in actionable_findings[:8]:
        title = html.escape(str(finding.get("title", "Unknown test")))
        error_type = html.escape(str(finding.get("error_type", "Unknown error")))
        suggestion = html.escape(str(finding.get("suggestion", "No suggestion")))
        findings_list.append(f"<li><strong>{title}</strong> [{error_type}]<br><span>{suggestion}</span></li>")

    return f"""<!DOCTYPE html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>QA Automation Report</title>
    <style>
      :root {{
        color-scheme: light;
        --bg: #f4efe7;
        --panel: #fffaf2;
        --ink: #18222f;
        --muted: #5d6b7a;
        --accent: #1f7a8c;
        --accent-2: #bf6c32;
        --line: #e6d8c5;
      }}
      * {{ box-sizing: border-box; }}
      body {{ margin: 0; font-family: Georgia, "Times New Roman", serif; background: radial-gradient(circle at top, #fff7ea 0%, var(--bg) 55%, #eadfce 100%); color: var(--ink); }}
      main {{ max-width: 1080px; margin: 0 auto; padding: 40px 20px 72px; }}
      h1, h2 {{ line-height: 1.1; margin: 0; }}
      p {{ color: var(--muted); line-height: 1.6; }}
      a {{ color: var(--accent); text-decoration: none; }}
      a:hover {{ text-decoration: underline; }}
      .hero {{ background: linear-gradient(135deg, rgba(31,122,140,0.12), rgba(191,108,50,0.12)); border: 1px solid var(--line); border-radius: 28px; padding: 28px; box-shadow: 0 18px 40px rgba(24,34,47,0.08); }}
      .hero p {{ max-width: 72ch; }}
      .badge {{ display: inline-block; margin-top: 12px; padding: 8px 14px; border-radius: 999px; background: #ffffffb3; border: 1px solid var(--line); color: var(--accent-2); font-size: 14px; letter-spacing: 0.04em; text-transform: uppercase; }}
      .grid {{ display: grid; gap: 18px; margin-top: 24px; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); }}
      .card, .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 22px; padding: 20px; box-shadow: 0 12px 30px rgba(24,34,47,0.05); }}
      .metric {{ font-size: 34px; margin: 8px 0 0; }}
      .label {{ color: var(--muted); font-size: 14px; text-transform: uppercase; letter-spacing: 0.08em; }}
      .panels {{ display: grid; gap: 18px; margin-top: 24px; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }}
      ul {{ margin: 16px 0 0; padding-left: 20px; color: var(--muted); }}
      li {{ margin: 0 0 12px; line-height: 1.5; }}
      .cta {{ display: flex; flex-wrap: wrap; gap: 12px; margin-top: 22px; }}
      .button {{ display: inline-flex; align-items: center; justify-content: center; padding: 12px 18px; border-radius: 999px; border: 1px solid var(--accent); background: var(--accent); color: white; font-weight: 600; }}
      .button.secondary {{ background: transparent; color: var(--accent); }}
    </style>
  </head>
  <body>
    <main>
      <section class=\"hero\">
        <h1>QA Automation Report</h1>
        <p>{headline}</p>
        <p>{executive_summary}</p>
        <span class=\"badge\">Pipeline status: {html.escape(status)} | LLM: {provider_status}</span>
        <div class=\"cta\">
          <a class=\"button\" href=\"./playwright-report/index.html\">Open Playwright HTML Report</a>
          <a class=\"button secondary\" href=\"./llm-summary.json\">Open LLM JSON</a>
        </div>
      </section>

      <section class=\"grid\">
        <article class=\"card\"><div class=\"label\">Total Runs</div><div class=\"metric\">{total}</div></article>
        <article class=\"card\"><div class=\"label\">Passed</div><div class=\"metric\">{passed}</div></article>
        <article class=\"card\"><div class=\"label\">Failed</div><div class=\"metric\">{failed}</div></article>
        <article class=\"card\"><div class=\"label\">Flaky</div><div class=\"metric\">{flaky}</div></article>
        <article class=\"card\"><div class=\"label\">Timed Out</div><div class=\"metric\">{timed_out}</div></article>
        <article class=\"card\"><div class=\"label\">Model</div><div class=\"metric\" style=\"font-size:20px\">{model}</div></article>
      </section>

      <section class=\"panels\">
        <article class=\"panel\">
          <h2>Top Risks</h2>
          <ul>{render_list(top_risks, 'No major risks reported.')}</ul>
        </article>
        <article class=\"panel\">
          <h2>Next Actions</h2>
          <ul>{render_list(next_actions, 'No follow-up actions suggested.')}</ul>
        </article>
        <article class=\"panel\">
          <h2>Notable Failures</h2>
          <ul>{render_failures(failures)}</ul>
        </article>
        <article class=\"panel\">
          <h2>Actionable Findings</h2>
          <ul>{''.join(findings_list) if findings_list else '<li>No analyzer findings captured for this run.</li>'}</ul>
        </article>
      </section>
    </main>
  </body>
</html>
"""


def build_site(report_path: Path, llm_summary_path: Path, html_report_dir: Path, output_dir: Path) -> None:
    resolved_report_path = resolve_report_path(report_path)
    report = load_json(resolved_report_path)
    report_summary = summarize_report(report)
    llm_payload = maybe_load_json(llm_summary_path)

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    playwright_output = output_dir / "playwright-report"
    shutil.copytree(html_report_dir, playwright_output)

    if llm_summary_path.exists():
        shutil.copy2(llm_summary_path, output_dir / "llm-summary.json")

    markdown_summary = llm_summary_path.with_suffix(".md")
    if markdown_summary.exists():
        shutil.copy2(markdown_summary, output_dir / "llm-summary.md")

    index_html = build_index(report_summary, llm_payload)
    (output_dir / "index.html").write_text(index_html, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a static GitHub Pages site for the QA report.")
    parser.add_argument("--report", default="reports/report.json", help="Path to Playwright JSON report")
    parser.add_argument("--llm-summary", default="reports/llm-summary.json", help="Path to generated LLM summary JSON")
    parser.add_argument("--html-report-dir", default="reports/html", help="Path to Playwright HTML report directory")
    parser.add_argument("--output-dir", default="site", help="Output directory for Pages artifact")
    args = parser.parse_args()

    build_site(
        report_path=Path(args.report),
        llm_summary_path=Path(args.llm_summary),
        html_report_dir=Path(args.html_report_dir),
        output_dir=Path(args.output_dir),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
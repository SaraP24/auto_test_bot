from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ai.healing import report_analyzer
from ai.update_readme_test_status import resolve_report_path, summarize_report


README_START_MARKER = "<!-- LLM-TEST-SUMMARY:START -->"
README_END_MARKER = "<!-- LLM-TEST-SUMMARY:END -->"
DEFAULT_API_URL = "https://api.openai.com/v1/chat/completions"
DEFAULT_MODEL = "gpt-4.1-mini"


def iter_suites(suites: list[dict[str, Any]]) -> list[dict[str, Any]]:
    flattened: list[dict[str, Any]] = []
    for suite in suites or []:
        flattened.append(suite)
        flattened.extend(iter_suites(suite.get("suites", [])))
    return flattened


def collect_test_runs(report: dict[str, Any]) -> list[dict[str, Any]]:
    runs: list[dict[str, Any]] = []
    for suite in iter_suites(report.get("suites", [])):
        suite_title = suite.get("title") or "suite"
        for spec in suite.get("specs", []):
            spec_title = spec.get("title") or "unknown"
            for test_case in spec.get("tests", []):
                run = {
                    "suite": suite_title,
                    "title": spec_title,
                    "project": test_case.get("projectName") or test_case.get("projectId") or "unknown",
                    "status": test_case.get("status") or test_case.get("outcome") or "unknown",
                    "expected_status": test_case.get("expectedStatus") or "unknown",
                    "results": [],
                }
                for result in test_case.get("results", []):
                    run["results"].append(
                        {
                            "status": result.get("status", "unknown"),
                            "duration": result.get("duration", 0),
                            "errors": result.get("errors", []),
                        }
                    )
                runs.append(run)
    return runs


def normalize_status(status: str) -> str:
    mapping = {
        "expected": "passed",
        "unexpected": "failed",
    }
    return mapping.get(status, status)


def build_context(report: dict[str, Any]) -> dict[str, Any]:
    summary = summarize_report(report)
    suggestions = report_analyzer.analyze_report(report=report, dedupe=True, return_details=True)
    test_runs = collect_test_runs(report)

    failures: list[dict[str, Any]] = []
    for run in test_runs:
        normalized = normalize_status(str(run["status"]))
        if normalized not in {"failed", "timedOut", "interrupted"}:
            continue

        errors: list[str] = []
        durations: list[int] = []
        for result in run["results"]:
            durations.append(int(result.get("duration") or 0))
            for error in result.get("errors", []):
                if isinstance(error, dict):
                    errors.append(str(error.get("message") or ""))
                else:
                    errors.append(str(error))

        failures.append(
            {
                "suite": run["suite"],
                "title": run["title"],
                "project": run["project"],
                "status": normalized,
                "duration_ms": max(durations) if durations else 0,
                "errors": [msg for msg in errors if msg][:3],
            }
        )

    flaky_tests = [
        {
            "suite": run["suite"],
            "title": run["title"],
            "project": run["project"],
            "result_statuses": [result.get("status", "unknown") for result in run["results"]],
        }
        for run in test_runs
        if any(result.get("status") == "failed" for result in run["results"])
        and any(result.get("status") == "passed" for result in run["results"])
    ]

    actionable_findings = []
    for title, error_type, suggestion, details in suggestions[:8]:
        actionable_findings.append(
            {
                "title": title,
                "error_type": error_type,
                "suggestion": suggestion,
                "trace_suggestion": details.get("trace_suggestion") if isinstance(details, dict) else None,
                "location": (details or {}).get("parsed_location") if isinstance(details, dict) else None,
            }
        )

    return {
        "summary": summary,
        "failures": failures,
        "flaky_tests": flaky_tests,
        "actionable_findings": actionable_findings,
    }


def build_prompt(context: dict[str, Any]) -> str:
    return textwrap.dedent(
        f"""
        You are analyzing Playwright CI results for a QA automation project.
        Produce a concise JSON object with these exact keys:
        headline, executive_summary, top_risks, next_actions, notable_failures.

        Rules:
        - headline: short single sentence.
        - executive_summary: 2 to 4 sentences.
        - top_risks: array of up to 3 short strings.
        - next_actions: array of up to 4 concrete actions.
        - notable_failures: array of objects with keys title, project, probable_cause, suggested_fix.
        - If all tests passed, say that clearly and focus on residual risks like flakiness.
        - Use only information present in the context below.
        - Return valid JSON only, with no markdown fences.

        Context:
        {json.dumps(context, ensure_ascii=False, indent=2)}
        """
    ).strip()


def strip_code_fences(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if len(lines) >= 3:
            return "\n".join(lines[1:-1]).strip()
    return stripped


def call_llm(prompt: str) -> dict[str, Any]:
    api_key = os.getenv("LLM_API_KEY", "").strip() or os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return {
            "provider_status": "disabled",
            "headline": "LLM summary disabled.",
            "executive_summary": "Set OPENAI_API_KEY in CI secrets to enable AI-generated failure summaries.",
            "top_risks": ["No LLM provider configured in the environment."],
            "next_actions": ["Add OPENAI_API_KEY and optionally OPENAI_MODEL or OPENAI_API_URL to CI."],
            "notable_failures": [],
        }

    model = os.getenv("LLM_MODEL", "").strip() or os.getenv("OPENAI_MODEL", "").strip() or DEFAULT_MODEL
    api_url = os.getenv("LLM_API_URL", "").strip() or os.getenv("OPENAI_API_URL", "").strip() or DEFAULT_API_URL
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You summarize QA automation results accurately and conservatively.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }

    request = urllib.request.Request(
        api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"LLM request failed with HTTP {error.code}: {details}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"LLM request failed: {error.reason}") from error

    content = response_payload["choices"][0]["message"]["content"]
    parsed = json.loads(strip_code_fences(content))
    parsed["provider_status"] = "enabled"
    parsed["model"] = model
    return parsed


def render_markdown(llm_summary: dict[str, Any], context: dict[str, Any]) -> str:
    lines = [
        "# LLM Test Summary",
        "",
        llm_summary.get("headline", "LLM summary unavailable."),
        "",
        llm_summary.get("executive_summary", ""),
        "",
        "## Snapshot",
        "",
        f"- Total test runs: {context['summary']['total']}",
        f"- Passed: {context['summary']['passed']}",
        f"- Failed: {context['summary']['failed']}",
        f"- Timed out: {context['summary']['timedOut']}",
        f"- Flaky: {context['summary']['flaky']}",
        "",
        "## Top Risks",
        "",
    ]

    for risk in llm_summary.get("top_risks", []) or ["No major risks reported."]:
        lines.append(f"- {risk}")

    lines.extend(["", "## Next Actions", ""])
    for action in llm_summary.get("next_actions", []) or ["No follow-up actions suggested."]:
        lines.append(f"- {action}")

    notable_failures = llm_summary.get("notable_failures", [])
    if notable_failures:
        lines.extend(["", "## Notable Failures", ""])
        for failure in notable_failures:
            title = failure.get("title", "Unknown test")
            project = failure.get("project", "unknown")
            probable_cause = failure.get("probable_cause", "Not provided")
            suggested_fix = failure.get("suggested_fix", "Not provided")
            lines.append(f"- {title} [{project}]: {probable_cause}. Suggested fix: {suggested_fix}")

    lines.extend(["", f"Provider status: {llm_summary.get('provider_status', 'unknown')}"])
    if llm_summary.get("model"):
        lines.append(f"Model: {llm_summary['model']}")
    return "\n".join(lines).strip() + "\n"


def render_readme_block(llm_summary: dict[str, Any]) -> str:
    lines = [
        README_START_MARKER,
        "## LLM Test Summary",
        "",
        llm_summary.get("headline", "LLM summary unavailable."),
        "",
        llm_summary.get("executive_summary", ""),
        "",
    ]

    risks = llm_summary.get("top_risks", [])
    if risks:
        lines.append("Top risks:")
        for risk in risks[:3]:
            lines.append(f"- {risk}")
        lines.append("")

    actions = llm_summary.get("next_actions", [])
    if actions:
        lines.append("Suggested next actions:")
        for action in actions[:4]:
            lines.append(f"- {action}")
        lines.append("")

    lines.append(README_END_MARKER)
    return "\n".join(lines)


def update_readme(readme_path: Path, llm_summary: dict[str, Any]) -> None:
    original = readme_path.read_text(encoding="utf-8")
    block = render_readme_block(llm_summary)

    if README_START_MARKER in original and README_END_MARKER in original:
        start = original.index(README_START_MARKER)
        end = original.index(README_END_MARKER) + len(README_END_MARKER)
        updated = original[:start] + block + original[end:]
    else:
        anchor = "## 🧠 Detalles del Módulo de Self-Healing"
        if anchor in original:
            updated = original.replace(anchor, block + "\n\n" + anchor, 1)
        else:
            updated = original.rstrip() + "\n\n" + block + "\n"

    readme_path.write_text(updated, encoding="utf-8")


def write_output(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an LLM-based summary for Playwright test results.")
    parser.add_argument("--report", default="reports/report.json", help="Path to the Playwright JSON report")
    parser.add_argument("--readme", default="", help="Optional README path to update with the LLM summary")
    parser.add_argument("--markdown-out", default="reports/llm-summary.md", help="Path to write the markdown summary")
    parser.add_argument("--json-out", default="reports/llm-summary.json", help="Path to write the structured summary")
    args = parser.parse_args()

    report_path = resolve_report_path(Path(args.report))
    report = json.loads(report_path.read_text(encoding="utf-8"))
    context = build_context(report)
    llm_summary = call_llm(build_prompt(context))

    markdown_output = render_markdown(llm_summary, context)
    json_output = json.dumps(
        {
            "context": context,
            "summary": llm_summary,
        },
        ensure_ascii=False,
        indent=2,
    )

    write_output(Path(args.markdown_out), markdown_output)
    write_output(Path(args.json_out), json_output)

    if args.readme and llm_summary.get("provider_status") == "enabled":
        update_readme(Path(args.readme), llm_summary)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
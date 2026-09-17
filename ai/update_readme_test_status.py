from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


START_MARKER = "<!-- TEST-STATUS:START -->"
END_MARKER = "<!-- TEST-STATUS:END -->"


def resolve_report_path(report_path: Path) -> Path:
    if report_path.is_file():
        return report_path

    candidates = [
        report_path,
        report_path / "report.json",
        report_path / "reports" / "report.json",
        report_path.parent / "report.json",
        report_path.parent / "reports" / "report.json",
    ]

    for candidate in candidates:
        if candidate.is_file():
            return candidate

    raise FileNotFoundError(f"Could not find report.json near '{report_path}'")


def load_report(report_path: Path) -> dict[str, Any]:
    resolved_path = resolve_report_path(report_path)
    with resolved_path.open("r", encoding="utf-8") as file_handle:
        return json.load(file_handle)


def iter_suites(suites: list[dict[str, Any]]) -> list[dict[str, Any]]:
    flattened: list[dict[str, Any]] = []
    for suite in suites or []:
        flattened.append(suite)
        flattened.extend(iter_suites(suite.get("suites", [])))
    return flattened


def resolve_test_status(test_case: dict[str, Any]) -> str:
    explicit = test_case.get("status") or test_case.get("outcome")
    if explicit:
        normalized = str(explicit)
        if normalized == "expected":
            return "passed"
        if normalized == "unexpected":
            return "failed"
        return normalized

    results = test_case.get("results", [])
    if not results:
        return "unknown"

    statuses = [str(result.get("status", "unknown")) for result in results]
    if "failed" in statuses:
        return "failed"
    if "timedOut" in statuses:
        return "timedOut"
    if "interrupted" in statuses:
        return "interrupted"
    if "skipped" in statuses:
        return "skipped"
    if "passed" in statuses:
        return "passed"
    return statuses[-1]


def summarize_report(report: dict[str, Any]) -> dict[str, int]:
    summary = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "flaky": 0,
        "timedOut": 0,
        "interrupted": 0,
        "unknown": 0,
    }

    for suite in iter_suites(report.get("suites", [])):
        for spec in suite.get("specs", []):
            for test_case in spec.get("tests", []):
                status = resolve_test_status(test_case)
                summary["total"] += 1
                if status in summary:
                    summary[status] += 1
                else:
                    summary["unknown"] += 1

    return summary


def render_status_block(summary: dict[str, int]) -> str:
    overall = "Passing" if summary["failed"] == 0 and summary["timedOut"] == 0 and summary["interrupted"] == 0 else "Failing"
    lines = [
        START_MARKER,
        "## CI Test Status",
        "",
        f"Current status: **{overall}**.",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Total test runs | {summary['total']} |",
        f"| Passed | {summary['passed']} |",
        f"| Failed | {summary['failed']} |",
        f"| Timed out | {summary['timedOut']} |",
        f"| Interrupted | {summary['interrupted']} |",
        f"| Skipped | {summary['skipped']} |",
        f"| Flaky | {summary['flaky']} |",
        "",
        "This section is maintained automatically by the GitHub Actions pipeline from `reports/report.json`.",
        END_MARKER,
    ]
    return "\n".join(lines)


def update_readme(readme_path: Path, status_block: str) -> None:
    original = readme_path.read_text(encoding="utf-8")

    if START_MARKER in original and END_MARKER in original:
        start = original.index(START_MARKER)
        end = original.index(END_MARKER) + len(END_MARKER)
        updated = original[:start] + status_block + original[end:]
    else:
        anchor = "## 🧠 Etapas de Desarrollo del Proyecto"
        if anchor in original:
            updated = original.replace(anchor, status_block + "\n\n" + anchor, 1)
        else:
            updated = original.rstrip() + "\n\n" + status_block + "\n"

    readme_path.write_text(updated, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Update README with Playwright report status.")
    parser.add_argument("--report", default="reports/report.json", help="Path to the Playwright JSON report")
    parser.add_argument("--readme", default="README.md", help="Path to the README file")
    args = parser.parse_args()

    report_path = Path(args.report)
    readme_path = Path(args.readme)

    report = load_report(report_path)
    summary = summarize_report(report)
    status_block = render_status_block(summary)
    update_readme(readme_path, status_block)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
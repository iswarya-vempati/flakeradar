import argparse
from pathlib import Path
from collections import Counter

from app.detector import VERDICT_ORDER, Finding, analyze_all
from app.db import connect, init_db

ATTENTION = {"flaky", "suspicious"}


def format_report(
    findings: list[Finding], top: int = 10, show_all: bool = False
) -> str:
    if not findings:
        return "No test results in the database yet. Load some reports first."

    counts = Counter(finding.verdict for finding in findings)
    summary = ", ".join(
        f"{verdict} {counts[verdict]}" for verdict in VERDICT_ORDER if counts[verdict]
    )

    if show_all:
        candidates = findings
        heading = "All tests"
    else:
        candidates = [f for f in findings if f.verdict in ATTENTION]
        heading = "Tests that need attention"

    lines = [
        "FlakeRadar report",
        f"Tests analyzed: {len(findings)}",
        f"Verdicts: {summary}",
        "",
        heading,
    ]
    if not candidates:
        lines.append("  None. No flaky or suspicious tests found.")
    for number, finding in enumerate(candidates[:top], start=1):
        lines.append(f"{number}. [{finding.verdict.upper()}] {finding.test_id}")
        lines.append(
            f"   Failed {finding.failures} of {finding.runs} runs; "
            f"result changed {finding.transitions} time(s)."
        )
        lines.append(f"   Evidence: {finding.evidence}")

    hidden = len(candidates) - top
    if hidden > 0:
        lines.append(f"... and {hidden} more. Use --top or --all to see more.")
    lines.append("")
    lines.append("These verdicts are evidence-based hints, not proof.")
    return "\n".join(lines)


def main() -> None:
    cli = argparse.ArgumentParser(description="Show which tests look flaky")
    cli.add_argument("--db", default="flakeradar.db", help="database file")
    cli.add_argument("--top", type=int, default=10, help="how many tests to show")
    cli.add_argument(
        "--all", action="store_true", help="show every test, not only flaky ones"
    )
    args = cli.parse_args()

    if not Path(args.db).exists():
        print(f"Database file not found: {args.db}")
        return

    conn = connect(args.db)
    init_db(conn)
    print(format_report(analyze_all(conn), top=args.top, show_all=args.all))


if __name__ == "__main__":
    main()
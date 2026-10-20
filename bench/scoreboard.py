from __future__ import annotations

import json
import platform
from datetime import date, timezone, datetime
from pathlib import Path
from typing import Any


def hardware() -> dict[str, Any]:
    cores = None
    try:
        import os

        cores = os.cpu_count()
    except Exception:
        pass
    return {
        "os": platform.platform(),
        "python": platform.python_version(),
        "cpu": platform.processor() or platform.machine(),
        "logical_cores": cores,
        "measured_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ"),
    }


def grouping_table(rows: list[dict[str, Any]]) -> str:
    def cell(v):
        return f"{v:.3f}" if isinstance(v, (int, float)) else "-"

    out = ["| System | GT templates | OSS LogLens | Drain3 | lensd |",
           "|---|---:|---:|---:|---:|"]
    sums = {"oss": [], "drain3": [], "lensd": []}
    for r in rows:
        out.append(
            f"| {r['system']} | {r.get('gt_templates','-')} | "
            f"{cell(r.get('oss'))} | {cell(r.get('drain3'))} | {cell(r.get('lensd'))} |"
        )
        for k in sums:
            if isinstance(r.get(k), (int, float)):
                sums[k].append(r[k])
    avg = {k: (sum(v) / len(v) if v else None) for k, v in sums.items()}
    out.append(
        f"| **Average** | | **{cell(avg['oss'])}** | **{cell(avg['drain3'])}** | "
        f"**{cell(avg['lensd'])}** |"
    )
    return "\n".join(out)


def detection_table(rows: list[dict[str, Any]]) -> str:
    out = ["| Dataset | Metric | OSS LogLens | Severity rule | Source |",
           "|---|---|---:|---:|---|"]
    for r in rows:
        out.append(
            f"| {r['dataset']} | {r['metric']} | {r.get('oss','-')} | "
            f"{r.get('severity','-')} | {r.get('source','')} |"
        )
    return "\n".join(out)


def render_markdown(report: dict[str, Any]) -> str:
    hw = report["hardware"]
    md = [
        "# LogLens Bench - Scoreboard",
        "",
        f"_Generated {hw['measured_utc']} on {hw['os']}, "
        f"Python {hw['python']}, {hw.get('logical_cores','?')} logical cores._",
        "",
        "We publish every number, including where we lose. `measured` = produced by "
        "`python -m bench.run` on the machine above. `external` = from the baseline "
        "benchmark of the public repo (2026-10-03); reproduce commands in that report. "
        "`target` = a goal still to be proven.",
        "",
        "## 1. Template grouping accuracy (Loghub-2k, measured)",
        "",
        "Higher is better. Grouping Accuracy uses the logpai definition (a message "
        "scores only if its predicted group equals its ground-truth group exactly).",
        "",
        grouping_table(report["grouping"]),
        "",
        "> **lensd** here is the byte-scan masker (`lensd mask`), the M0 template stage. "
        "It fixes the OSS catastrophe on HDFS (block ids) and leads on Zookeeper, but "
        "v0 still trails on datasets with compound variables (BGL, Proxifier) where "
        "LensTree merge/split refinement (roadmap) is required. GA >= 0.90 average is a "
        "stated target, not yet claimed.",
        "",
        "## 2. Anomaly detection (external benchmark, to re-run with lensd)",
        "",
        detection_table(report["detection"]),
        "",
        "> The premium engine must beat the severity rule on BGL window-F1 (>= 0.90 "
        "target) and lift HDFS block-F1 from 0.06 toward 0.90 with calibrated sequence "
        "detection. Those detectors land in M2 (post-DevFest).",
        "",
        "## Reproduce",
        "",
        "```bash",
        "bash scripts/fetch_datasets.sh      # Loghub-2k (small); BGL/HDFS full are separate",
        "python -m bench.run --data data/loghub2k --out results/latest.json --markdown",
        "```",
        "",
    ]
    return "\n".join(md)


def write_report(report: dict[str, Any], json_path: str | Path, md_path: str | Path | None = None):
    Path(json_path).parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    if md_path:
        Path(md_path).write_text(render_markdown(report), encoding="utf-8")
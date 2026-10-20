from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bench.datasets import discover_systems, load_loghub2k
from bench.metrics import grouping_accuracy
from bench.scoreboard import hardware, write_report, render_markdown

DETECTION_ROWS = [
    {"dataset": "BGL (full)", "metric": "window-F1", "oss": "0.707", "severity": "0.867", "source": "external"},
    {"dataset": "BGL (full)", "metric": "line-F1", "oss": "0.265", "severity": "0.440", "source": "external"},
    {"dataset": "HDFS (500k)", "metric": "block-F1", "oss": "0.06", "severity": "0.061", "source": "external"},
]


def _lensd_grouper(binary: str | None):
    if binary and shutil.which(binary):
        from bench.engines.grouping import group_lensd

        return "lensd", (lambda msgs: group_lensd(msgs, binary=binary))
    try:
        from bench.engines.lensd_ref import group_lensd_ref

        return "lensd", group_lensd_ref  # reference port (binary not found)
    except Exception:
        return None, None


def _oss_grouper():
    try:
        from bench.engines.grouping import group_loglens_oss

        group_loglens_oss(["probe 1"])  # import-time check
        return group_loglens_oss
    except Exception:
        return None


def _drain3_grouper():
    try:
        from bench.engines.grouping import group_drain3

        group_drain3(["probe 1"])
        return group_drain3
    except Exception:
        return None


def main(argv=None):
    ap = argparse.ArgumentParser(description="Produce the LogLens Bench scoreboard.")
    ap.add_argument("--data", default="data/loghub2k", help="dir with *_2k.log_structured.csv")
    ap.add_argument("--out", default="results/latest.json", help="results JSON path")
    ap.add_argument("--markdown", action="store_true", help="also write SCOREBOARD.md next to --out")
    ap.add_argument("--lensd-bin", default="lensd", help="lensd binary name/path (default: lensd)")
    args = ap.parse_args(argv)

    systems = discover_systems(args.data)
    if not systems:
        print(f"no Loghub-2k structured CSVs under {args.data!r}; run scripts/fetch_datasets.sh", file=sys.stderr)
        return 2

    oss = _oss_grouper()
    drain3 = _drain3_grouper()
    lensd_name, lensd = _lensd_grouper(args.lensd_bin)
    lensd_is_binary = bool(shutil.which(args.lensd_bin))

    print(f"engines: drain3={'y' if drain3 else '-'} oss={'y' if oss else '-'} "
          f"lensd={'binary' if lensd_is_binary else ('ref-port' if lensd else '-')}")

    rows = []
    for csv in systems:
        ds = load_loghub2k(csv)
        row = {"system": ds.system, "gt_templates": len(set(ds.event_ids))}
        if oss:
            row["oss"] = round(grouping_accuracy(ds.event_ids, oss(ds.contents)), 4)
        if drain3:
            row["drain3"] = round(grouping_accuracy(ds.event_ids, drain3(ds.contents)), 4)
        if lensd:
            row["lensd"] = round(grouping_accuracy(ds.event_ids, lensd(ds.contents)), 4)
        rows.append(row)
        print(f"  {ds.system:<12} oss={row.get('oss','-')} drain3={row.get('drain3','-')} lensd={row.get('lensd','-')}")

    report = {
        "schema": "loglens.bench.scoreboard.v1",
        "hardware": hardware(),
        "lensd_source": "binary" if lensd_is_binary else "reference-port",
        "grouping": rows,
        "detection": DETECTION_ROWS,
    }
    md_path = str(Path(args.out).with_name("SCOREBOARD.md")) if args.markdown else None
    write_report(report, args.out, md_path)
    print(f"\nwrote {args.out}" + (f" and {md_path}" if md_path else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
# loglens-bench - the public LogLens scoreboard

- **Scope:** Reproducible accuracy benchmarks for LogLens. Dataset fetchers, baselines (Drain3, severity rule), scorers, published results, scoreboard rendering. Every engine is treated as a black box.
- **Not in scope:** Engine code.
- **Owner:** @ParasRajput810 (founder).
- **Consumes:** released engines under test (OSS LogLens via PyPI, Drain3, the `lensd` binary).
- **Produces:** `results/*.json`, `SCOREBOARD.md`, CI regression verdicts.

## Honesty rules (plan 12)
- Labels are used **only** for scoring, never for training or tuning.
- Hardware is disclosed with every number; `measured` vs `external` vs `target` is always explicit.
- One command reproduces the table. **We publish where we lose, not just where we win.**

## Quick start
```bash
python3 -m venv .venv && source .venv/bin/activate   # Debian/WSL: avoid externally-managed-environment
pip install loglensai                                # OSS engine column
pip install "setuptools<81" wheel && pip install drain3   # Drain3 column (Py 3.12+ needs the pin)
bash scripts/fetch_datasets.sh                       # Loghub-2k (small)
python3 -m bench.run --data data/loghub2k --out results/latest.json --markdown
cat results/SCOREBOARD.md
```
Put the `lensd` binary on your PATH to score the premium engine's real masker; otherwise
the harness falls back to a documented reference port (`bench/engines/lensd_ref.py`) and
labels the result accordingly. Engines that are not installed are skipped (shown as `-`),
never faked.

## What it measures
1. **Template grouping accuracy** (Loghub-2k, logpai definition) - OSS LogLens vs Drain3 vs lensd.
2. **Anomaly detection** (BGL window-F1, HDFS block-F1) - seeded from the external baseline
   benchmark; re-run with the full labelled datasets + lensd as those detectors land (M2).

## Layout
```
bench/metrics.py            GA, P/R/F1, window-F1, block-F1 (pure stdlib, tested)
bench/datasets.py           Loghub-2k loader
bench/engines/grouping.py   drain3, loglens_oss, lensd (binary) adapters
bench/engines/lensd_ref.py  Python reference of the lensd masker (binary is authoritative)
bench/baselines/severity.py severity-keyword rule
bench/scoreboard.py         Markdown + JSON renderer
bench/run.py                one command to produce the scoreboard
results/                    committed results (JSON + SCOREBOARD.md)
tests/test_metrics.py       metric correctness tests
```

## Validation
The harness reproduces the published baseline numbers exactly, e.g. HDFS grouping
accuracy OSS **0.001** vs Drain3 **0.998**, BGL **0.836** vs **0.969** - so new numbers
are directly comparable.
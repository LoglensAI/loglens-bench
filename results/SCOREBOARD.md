# LogLens Bench - Scoreboard

_Generated 2026-10-06 11:37:58Z on Linux-6.18.33.1-microsoft-standard-WSL2-x86_64-with-glibc2.39, Python 3.12.3, 12 logical cores._

We publish every number, including where we lose. `measured` = produced by `python -m bench.run` on the machine above. `external` = from the baseline benchmark of the public repo (2026-10-03); reproduce commands in that report. `target` = a goal still to be proven.

## 1. Template grouping accuracy (Loghub-2k, measured)

Higher is better. Grouping Accuracy uses the logpai definition (a message scores only if its predicted group equals its ground-truth group exactly).

| System | GT templates | OSS LogLens | Drain3 | lensd |
|---|---:|---:|---:|---:|
| Android | 166 | 0.678 | 0.605 | 0.782 |
| Apache | 6 | 1.000 | 1.000 | 1.000 |
| BGL | 120 | 0.836 | 0.969 | 0.476 |
| HDFS | 14 | 0.001 | 0.998 | 0.958 |
| HPC | 46 | 0.932 | 0.741 | 0.899 |
| Hadoop | 114 | 0.957 | 0.954 | 0.427 |
| HealthApp | 75 | 0.992 | 0.576 | 0.618 |
| Linux | 118 | 0.189 | 0.684 | 0.189 |
| Mac | 341 | 0.836 | 0.715 | 0.700 |
| OpenSSH | 27 | 0.336 | 0.718 | 0.126 |
| OpenStack | 43 | 0.491 | 0.309 | 0.516 |
| Proxifier | 8 | 0.001 | 0.025 | 0.001 |
| Spark | 36 | 0.737 | 0.922 | 0.730 |
| Thunderbird | 149 | 0.660 | 0.955 | 0.230 |
| Windows | 50 | 0.990 | 0.571 | 0.405 |
| Zookeeper | 50 | 0.849 | 0.967 | 0.975 |
| **Average** | | **0.655** | **0.732** | **0.564** |

> **lensd** here is the byte-scan masker (`lensd mask`), the M0 template stage. It fixes the OSS catastrophe on HDFS (block ids) and leads on Zookeeper, but v0 still trails on datasets with compound variables (BGL, Proxifier) where LensTree merge/split refinement (roadmap) is required. GA >= 0.90 average is a stated target, not yet claimed.

## 2. Anomaly detection (external benchmark, to re-run with lensd)

| Dataset | Metric | OSS LogLens | Severity rule | Source |
|---|---|---:|---:|---|
| BGL (full) | window-F1 | 0.707 | 0.867 | external |
| BGL (full) | line-F1 | 0.265 | 0.440 | external |
| HDFS (500k) | block-F1 | 0.06 | 0.061 | external |

> The premium engine must beat the severity rule on BGL window-F1 (>= 0.90 target) and lift HDFS block-F1 from 0.06 toward 0.90 with calibrated sequence detection. Those detectors land in M2 (post-DevFest).

## Reproduce

```bash
bash scripts/fetch_datasets.sh      # Loghub-2k (small); BGL/HDFS full are separate
python -m bench.run --data data/loghub2k --out results/latest.json --markdown
```

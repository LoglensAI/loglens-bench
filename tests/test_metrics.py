from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bench.metrics import block_prf, grouping_accuracy, line_prf, prf, window_prf


def test_ga_perfect():
    truth = ["A", "A", "B", "B", "C"]
    pred = ["x", "x", "y", "y", "z"]  # same partition, different names
    assert grouping_accuracy(truth, pred) == 1.0


def test_ga_all_wrong_one_big_cluster():
    truth = ["A", "A", "B", "C"]
    pred = ["x", "x", "x", "x"]
    assert grouping_accuracy(truth, pred) == 0.0


def test_ga_oversplit():
    truth = ["A", "A", "A", "A"]
    pred = ["1", "2", "3", "4"]
    assert grouping_accuracy(truth, pred) == 0.0


def test_ga_partial():
    truth = ["A", "A", "A", "B", "B"]
    pred = ["x", "x", "x", "y", "z"]  # A group perfect (3), B split (2 wrong)
    assert abs(grouping_accuracy(truth, pred) - 3 / 5) < 1e-9


def test_ga_empty():
    assert grouping_accuracy([], []) == 0.0


def test_prf_basic():
    p, r, f = prf(tp=8, fp=2, fn=0)
    assert abs(p - 0.8) < 1e-9 and r == 1.0


def test_line_prf():
    truth = [True, True, False, False]
    pred = [True, False, True, False]
    p, r, f = line_prf(truth, pred)
    assert abs(p - 0.5) < 1e-9 and abs(r - 0.5) < 1e-9


def test_window_prf_groups_lines():
    truth = [True, False, False, False]  # w0 positive
    pred = [False, True, False, False]  # w0 positive (same window)
    p, r, f = window_prf(truth, pred, window=2)
    assert p == 1.0 and r == 1.0 and f == 1.0


def test_block_prf():
    blocks = ["b1", "b1", "b2", "b3"]
    pred = [True, False, False, True]  # b1 flagged, b3 flagged
    anomalous = {"b1", "b2"}
    p, r, f = block_prf(blocks, pred, anomalous)
    assert abs(p - 0.5) < 1e-9 and abs(r - 0.5) < 1e-9


if __name__ == "__main__":
    import traceback

    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except Exception:
            failed += 1
            print(f"FAIL {fn.__name__}")
            traceback.print_exc()
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)
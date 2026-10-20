from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Sequence


def grouping_accuracy(truth: Sequence[str], pred: Sequence[str]) -> float:
    if len(truth) != len(pred):
        raise ValueError(f"length mismatch: {len(truth)} truth vs {len(pred)} pred")
    n = len(truth)
    if n == 0:
        return 0.0

    truth_counts = Counter(truth)
    pred_to_indices: dict[str, list[int]] = defaultdict(list)
    for i, p in enumerate(pred):
        pred_to_indices[p].append(i)

    accurate = 0
    for _p, idxs in pred_to_indices.items():
        gt_labels = {truth[i] for i in idxs}
        if len(gt_labels) == 1:
            gt = next(iter(gt_labels))
            if len(idxs) == truth_counts[gt]:
                accurate += len(idxs)
    return accurate / n


def prf(tp: int, fp: int, fn: int) -> tuple[float, float, float]:
    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    f = 2 * p * r / (p + r) if (p + r) else 0.0
    return p, r, f


def line_prf(truth_flags: Sequence[bool], pred_flags: Sequence[bool]) -> tuple[float, float, float]:
    if len(truth_flags) != len(pred_flags):
        raise ValueError("length mismatch")
    tp = sum(1 for t, p in zip(truth_flags, pred_flags, strict=True) if t and p)
    fp = sum(1 for t, p in zip(truth_flags, pred_flags, strict=True) if p and not t)
    fn = sum(1 for t, p in zip(truth_flags, pred_flags, strict=True) if t and not p)
    return prf(tp, fp, fn)


def window_prf(
    truth_flags: Sequence[bool],
    pred_flags: Sequence[bool],
    window: int,
) -> tuple[float, float, float]:
    
    if len(truth_flags) != len(pred_flags):
        raise ValueError("length mismatch")
    if window < 1:
        raise ValueError("window must be >= 1")
    n = len(truth_flags)
    tw: set[int] = set()
    pw: set[int] = set()
    for i in range(n):
        w = i // window
        if truth_flags[i]:
            tw.add(w)
        if pred_flags[i]:
            pw.add(w)
    tp = len(tw & pw)
    fp = len(pw - tw)
    fn = len(tw - pw)
    return prf(tp, fp, fn)


def block_prf(
    block_of_line: Sequence[str],
    pred_flags: Sequence[bool],
    anomalous_blocks: set[str],
) -> tuple[float, float, float]:
    if len(block_of_line) != len(pred_flags):
        raise ValueError("length mismatch")
    pred_blocks: set[str] = set()
    all_blocks: set[str] = set()
    for b, f in zip(block_of_line, pred_flags, strict=True):
        if b:
            all_blocks.add(b)
            if f:
                pred_blocks.add(b)
    truth_blocks = anomalous_blocks & all_blocks
    tp = len(pred_blocks & truth_blocks)
    fp = len(pred_blocks - truth_blocks)
    fn = len(truth_blocks - pred_blocks)
    return prf(tp, fp, fn)
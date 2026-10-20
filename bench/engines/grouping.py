from __future__ import annotations

import subprocess
from collections.abc import Sequence


def group_drain3(messages: Sequence[str]) -> list[str]:
    from drain3 import TemplateMiner
    from drain3.template_miner_config import TemplateMinerConfig

    cfg = TemplateMinerConfig()
    cfg.profiling_enabled = False
    miner = TemplateMiner(config=cfg)
    labels: list[str] = []
    for m in messages:
        res = miner.add_log_message(m)
        labels.append(str(res["cluster_id"]))
    return labels


def group_loglens_oss(messages: Sequence[str]) -> list[str]:
    from loglens.detection.templates import template_key

    return [template_key(m) for m in messages]


def group_lensd(messages: Sequence[str], binary: str = "lensd") -> list[str]:
    import os
    import tempfile

    with tempfile.NamedTemporaryFile("w", suffix=".log", delete=False, encoding="utf-8") as tf:
        for m in messages:
            tf.write(m.replace("\n", " ") + "\n")
        tmp = tf.name
    try:
        out = subprocess.run(
            [binary, "mask", tmp],
            capture_output=True,
            text=True,
            check=True,
        )
    finally:
        os.unlink(tmp)
    labels = out.stdout.splitlines()
    if len(labels) != len(messages):
        raise RuntimeError(
            f"lensd returned {len(labels)} lines for {len(messages)} messages"
        )
    return labels


ENGINES = {
    "drain3": group_drain3,
    "loglens_oss": group_loglens_oss,
    "lensd": group_lensd,
}
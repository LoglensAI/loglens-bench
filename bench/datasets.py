from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Loghub2k:
    system: str
    contents: list[str]
    event_ids: list[str]  # ground-truth template id per line

    def __len__(self) -> int:
        return len(self.contents)


def load_loghub2k(structured_csv: str | Path) -> Loghub2k:
    path = Path(structured_csv)
    system = path.name.split("_2k")[0]
    contents: list[str] = []
    event_ids: list[str] = []
    with open(path, newline="", encoding="utf-8", errors="replace") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            contents.append(row.get("Content", ""))
            event_ids.append(row.get("EventId", ""))
    return Loghub2k(system=system, contents=contents, event_ids=event_ids)


def discover_systems(data_dir: str | Path) -> list[Path]:
    d = Path(data_dir)
    return sorted(d.glob("*_2k.log_structured.csv"))

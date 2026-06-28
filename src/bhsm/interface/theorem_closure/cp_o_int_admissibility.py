"""Gauge and sector admissibility model for standalone CP O_int."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class CPOIntGaugeAdmissibility:
    gauge_representation: str
    allowed_sectors: tuple[str, ...]
    forbidden_sectors: tuple[str, ...]
    status: str
    source: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["allowed_sectors"] = list(self.allowed_sectors)
        payload["forbidden_sectors"] = list(self.forbidden_sectors)
        return payload


def gauge_admissibility_from_candidate(candidate: Mapping[str, Any] | None) -> CPOIntGaugeAdmissibility:
    raw = candidate.get("gauge_admissibility") if candidate else None
    if not raw:
        return CPOIntGaugeAdmissibility("", (), (), "OPEN_MISSING_GAUGE_ADMISSIBILITY", "not present in local theorem artifacts")
    if isinstance(raw, Mapping):
        return CPOIntGaugeAdmissibility(
            str(raw.get("gauge_representation", "author supplied")),
            tuple(str(value) for value in raw.get("allowed_sectors", ())),
            tuple(str(value) for value in raw.get("forbidden_sectors", ())),
            "AUTHOR_AXIOM_CONDITIONAL",
            "author-supplied candidate template",
        )
    return CPOIntGaugeAdmissibility(str(raw), (), (), "AUTHOR_AXIOM_CONDITIONAL", "author-supplied candidate template")

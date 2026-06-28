"""Typed standalone CP O_int operator components."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


class _Serializable:
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CPOIntDomain(_Serializable):
    description: str
    status: str
    source: str


@dataclass(frozen=True)
class CPOIntCodomain(_Serializable):
    description: str
    status: str
    source: str


@dataclass(frozen=True)
class CPOIntFieldRepresentation(_Serializable):
    field_content: str
    representation: str
    status: str
    source: str


@dataclass(frozen=True)
class CPOIntLorentzStructure(_Serializable):
    expression: str
    index_structure: str
    status: str
    source: str


@dataclass(frozen=True)
class CPOIntCouplingNormalization(_Serializable):
    coupling_symbol: str
    normalization: str
    mass_dimension: str
    status: str
    source: str

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class TypeSignature(ABC):
    pass


@dataclass(frozen=True)
class TypeSignaturePrimitive(TypeSignature):
    name: str


@dataclass(frozen=True)
class TypeSignatureFunction(TypeSignature):
    params: List[TypeSignature]
    return_type: TypeSignature

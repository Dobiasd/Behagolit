from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import List


@dataclass
class TypeSignature(ABC):
    pass


@dataclass(unsafe_hash=True)
class TypeSignaturePrimitive(TypeSignature):
    name: str


@dataclass
class TypeSignatureFunction(TypeSignature):
    params: List[TypeSignature]
    return_type: TypeSignature


@dataclass
class StructField(TypeSignature):
    name: str
    type_sig: TypeSignature


@dataclass
class Struct(TypeSignature):
    fields: List[StructField]


@dataclass
class SumType(TypeSignature):
    options: List[TypeSignature]

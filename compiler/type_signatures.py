from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from enum import auto, StrEnum
from typing import List, Union


@dataclass(frozen=True)
class TypeSignature(ABC):
    pass


class BuiltInPrimitiveType(StrEnum):
    STRING = auto()
    INTEGER = auto()
    BOOLEAN = auto()
    NONE = auto()


@dataclass(frozen=True)
class CustomPrimitiveType(TypeSignature):
    name: str


@dataclass(frozen=True)
class TypeSignaturePrimitive(TypeSignature):
    name: Union[BuiltInPrimitiveType, CustomPrimitiveType]


@dataclass(frozen=True)
class TypeSignatureFunction(TypeSignature):
    params: List[TypeSignature]
    return_type: TypeSignature

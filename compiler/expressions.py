from __future__ import annotations
from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import List, Callable
from typing import Sequence, Dict, Union

from .type_signatures import TypeSignature, TypeSignatureFunction


@dataclass(frozen=True)
class Definition(ABC):
    pass


@dataclass(frozen=True)
class Constant(Definition):
    expression: Expression
    type_sig: TypeSignature


@dataclass(frozen=True)
class CompoundFunction(Definition):
    type_sig: TypeSignatureFunction
    parameters: List[str]
    body: Expression


@dataclass(frozen=True)
class PrimitiveFunction(Definition):
    type_sig: TypeSignatureFunction
    parameters: List[str]
    impl: Callable[..., PrimitiveExpression]


@dataclass(frozen=True)
class Expression(ABC):
    pass


@dataclass(frozen=True)
class PrimitiveExpression(Expression):
    value: Union[None, str, bool, float, dict[str, PrimitiveExpression]]


@dataclass(frozen=True)
class Call(Expression):
    operator: Expression
    operands: Sequence[Expression]


@dataclass(frozen=True)
class Variable(Expression):
    name: str


@dataclass(frozen=True)
class CompoundClosure(Expression):
    parameters: List[str]
    environment: Dict[str, Expression]
    body: Expression


@dataclass(frozen=True)
class PrimitiveClosure(Expression):
    parameters: List[str]
    environment: Dict[str, Expression]
    impl: Callable[..., PrimitiveExpression]

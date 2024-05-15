from __future__ import annotations
from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import List, Callable
from typing import Sequence, Dict, Union

from .type_signatures import TypeSignature, TypeSignatureFunction


@dataclass
class Definition(ABC):
    pass


@dataclass
class Constant(Definition):
    expression: Expression
    type_sig: TypeSignature


# todo: mark as abstract if possible
@dataclass
class Function(Definition):
    type_sig: TypeSignatureFunction
    parameters: List[str]


@dataclass
class CompoundFunction(Function):
    body: Expression


@dataclass
class PrimitiveFunction(Function):
    impl: Callable[..., PrimitiveExpression]


@dataclass
class Expression(ABC):
    pass


@dataclass
class PrimitiveExpression(Expression):
    value: Union[None, str, bool, float, dict[str, PrimitiveExpression]]


@dataclass
class Call(Expression):
    operator: Expression
    operands: Sequence[Expression]


@dataclass
class Variable(Expression):
    name: str


@dataclass
class Closure(Expression):
    parameters: List[str]
    environment: Dict[str, Expression]


@dataclass
class CompoundClosure(Closure):
    body: Expression


@dataclass
class PrimitiveClosure(Closure):
    impl: Callable[..., PrimitiveExpression]

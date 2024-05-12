from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import List, Sequence, Dict, Union, Callable


@dataclass
class Parameter:
    name: str


@dataclass
class Expression(ABC):
    pass


@dataclass
class PrimitiveExpression(Expression):
    value: Union[str, bool, float, dict[str, PrimitiveExpression]]


@dataclass
class Variable(Expression):
    name: str


@dataclass
class Call(Expression):
    operator: Expression
    operands: Sequence[Expression]


@dataclass
class Function(Expression):
    parameters: List[Parameter]
    body: Expression


@dataclass
class Closure(Expression):
    parameters: List[Parameter]
    environment: Dict[str, Expression]


@dataclass
class CompoundClosure(Closure):
    body: Expression


@dataclass
class PrimitiveClosure(Closure):
    impl: Callable[..., PrimitiveExpression]

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import List, Sequence, Dict, Union, Callable


@dataclass
class TypeSignature(ABC):
    pass


@dataclass
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


@dataclass
class Expression(ABC):
    pass


@dataclass
class PrimitiveExpression(Expression):
    value: Union[None, str, bool, float, dict[str, PrimitiveExpression]]


@dataclass
class Constant(Expression):
    expression: Expression
    type_sig: TypeSignature


@dataclass
class Variable(Expression):
    name: str


@dataclass
class Call(Expression):
    operator: Expression
    operands: Sequence[Expression]


@dataclass
class Function(Expression):
    type_sig: TypeSignatureFunction
    parameters: List[str]


@dataclass
class CompoundFunction(Function):
    body: Expression


@dataclass
class PrimitiveFunction(Function):
    impl: Callable[..., PrimitiveExpression]


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

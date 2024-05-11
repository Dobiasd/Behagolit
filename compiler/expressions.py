from abc import ABC
from dataclasses import dataclass
from typing import Any, List, Sequence, Dict


@dataclass
class Parameter:
    name: str


@dataclass
class Expression(ABC):
    pass


@dataclass
class PlainExpression(Expression):
    # type_sig: TypeSignaturePlain
    value: Any



@dataclass
class Variable(Expression):
    name: str


@dataclass
class Application(Expression):
    operator: Expression
    operands: Sequence[Expression]

@dataclass
class Function(Expression):
    parameters: List[Parameter]
    body: Application


@dataclass
class Procedure(Expression):
    parameters: List[Parameter]
    env: Dict[str, Expression]


@dataclass
class CompoundProcedure(Procedure):
    body: Application


@dataclass
class PrimitiveProcedure(Procedure):
    impl: Any  # Callable something

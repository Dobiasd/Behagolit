from abc import ABC
from dataclasses import dataclass
from typing import List, Optional, Any

from lexer import Token, Name, Assignment, Semicolon, StringConstant, IntegerConstant


@dataclass
class Expression(ABC):
    pass


@dataclass
class Variable(Expression):
    name: str


@dataclass
class ConstantStringExpression(Expression):
    value: str


@dataclass
class ConstantIntegerExpression(Expression):
    value: int


@dataclass
class Call(Expression):
    function: str
    args: List[Expression]


@dataclass
class Definition:
    name: str
    expression: Expression


def get_definition(definitions: List[Definition], name: str) -> Definition:
    for definition in definitions:
        if definition.name == name:
            return definition
    raise RuntimeError(f'Definition {name} not found')


def evaluate(expression: Expression) -> Any:
    if isinstance(expression, (ConstantIntegerExpression | ConstantStringExpression)):
        return expression.value
    raise RuntimeError(f"Can not evaluate expression: {expression}")


def parser(tokens: List[Token]) -> List[Definition]:
    definitions: List[Definition] = []

    def done() -> bool:
        return len(tokens) == 0

    def current() -> Optional[Token]:
        return tokens[0]

    def progress() -> Token:
        return tokens.pop(0)

    while not done():
        while isinstance(current(), Semicolon):
            progress()

        curr = current()
        assert isinstance(curr, Name)
        defined = curr
        assert defined.value not in set(map(lambda d: d.name, definitions))
        progress()

        assert isinstance(current(), Assignment)
        progress()

        curr = current()
        if isinstance(curr, Name):
            func = curr
            progress()

            args: List[Name | StringConstant | IntegerConstant] = []
            while not isinstance(current(), Semicolon):
                curr = current()
                assert isinstance(curr, (Name, StringConstant, IntegerConstant))
                args.append(curr)
                progress()
            definitions.append(
                Definition(defined.value, Call(func.value, args)))

        elif isinstance(curr, StringConstant):
            definitions.append(Definition(defined.value, ConstantStringExpression(curr.value)))
        elif isinstance(curr, IntegerConstant):
            definitions.append(Definition(defined.value, ConstantIntegerExpression(curr.value)))
        progress()

    return definitions

from abc import ABC
from dataclasses import dataclass
from typing import List, Optional, Type, Sequence
from typing import TypeVar, Generic, Any

from lexer import Token, Name, Assignment, StringConstant, IntegerConstant, Semicolon

T = TypeVar('T')


# https://stackoverflow.com/a/66941316/1866775
class MyTypeChecker(Generic[T]):
    def is_right_type(self, x: Any) -> bool:
        return isinstance(x, self.__orig_class__.__args__[0])  # type: ignore


@dataclass
class Expression(ABC):
    pass


@dataclass
class Variable(Expression):
    name: str


@dataclass
class ConstantExpression(Expression):
    value: int | str


@dataclass
class ConstantStringExpression(ConstantExpression):
    value: str


@dataclass
class ConstantIntegerExpression(ConstantExpression):
    value: int


@dataclass
class Call(Expression):
    function: str
    args: Sequence[Expression]


@dataclass
class Definition:
    name: str
    expression: Expression


def get_definition(definitions: List[Definition], name: str) -> Optional[Definition]:
    for definition in definitions:
        if definition.name == name:
            return definition
    return None


def parser(tokens: List[Token]) -> List[Definition]:
    definitions: List[Definition] = []

    def done() -> bool:
        return len(tokens) == 0

    def current() -> Optional[Token]:
        if len(tokens) == 0:
            return None
        return tokens[0]

    def current_and_progress(cls: Type[T]) -> T:
        current_token = current()
        assert MyTypeChecker[cls]().is_right_type(current_token)  # type: ignore
        progress()
        return current_token  # type: ignore

    def progress() -> Token:
        return tokens.pop(0)

    while not done():
        if isinstance(current(), Semicolon):
            progress()
            continue

        curr = current_and_progress(Name)
        assert get_definition(definitions, curr.value) is None
        defined = curr

        current_and_progress(Assignment)

        func = current_and_progress(Name)

        args: List[Variable | ConstantStringExpression | ConstantIntegerExpression] = []
        while not isinstance(current(), Semicolon):
            current_arg = current()
            if isinstance(current_arg, Name):
                args.append(Variable(current_arg.value))
            if isinstance(current_arg, StringConstant):
                args.append(ConstantStringExpression(current_arg.value))
            if isinstance(current_arg, IntegerConstant):
                args.append(ConstantIntegerExpression(current_arg.value))
            progress()
        definitions.append(Definition(defined.value, Call(func.value, args)))

    return definitions

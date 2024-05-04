from abc import ABC
from dataclasses import dataclass
from typing import List, Optional, Type, Sequence
from typing import TypeVar, Generic, Any

from lexer import Token, Name, Assignment, StringConstant, IntegerConstant, Semicolon, Arrow

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
class Parameter(Token):
    name: str


@dataclass
class Call(Expression):
    function: str
    args: Sequence[Expression]


@dataclass
class Definition:
    name: str
    params: List[Parameter]
    expression: Expression


def get_definition(definitions: List[Definition], name: str) -> Optional[Definition]:
    for definition in definitions:
        if definition.name == name:
            return definition
    return None


def done(tokens: List[Token]) -> bool:
    return len(tokens) == 0


def current(tokens: List[Token]) -> Optional[Token]:
    if len(tokens) == 0:
        return None
    return tokens[0]


def current_and_progress(cls: Type[T], tokens: List[Token]) -> T:
    current_token = current(tokens)
    assert MyTypeChecker[cls]().is_right_type(current_token)  # type: ignore
    progress(tokens)
    return current_token  # type: ignore


def progress(tokens: List[Token]) -> Token:
    return tokens.pop(0)


def expression_parser(tokens: List[Token]) -> Expression:
    curr = current(tokens)
    if isinstance(curr, StringConstant):
        return ConstantStringExpression(curr.value)
    elif isinstance(curr, IntegerConstant):
        return ConstantIntegerExpression(curr.value)
    elif isinstance(curr, Name):
        func = current_and_progress(Name, tokens)
        args: List[Variable | ConstantStringExpression | ConstantIntegerExpression] = []
        while current(tokens) is not None and not isinstance(current(tokens), Semicolon):
            current_arg = current(tokens)
            if isinstance(current_arg, Name):
                args.append(Variable(current_arg.value))
            if isinstance(current_arg, StringConstant):
                args.append(ConstantStringExpression(current_arg.value))
            if isinstance(current_arg, IntegerConstant):
                args.append(ConstantIntegerExpression(current_arg.value))
            progress(tokens)
        return Call(func.value, args)
    else:
        raise RuntimeError("Wat")


def parser(tokens: List[Token]) -> List[Definition]:
    definitions: List[Definition] = []

    while not done(tokens):
        if isinstance(current(tokens), Semicolon):
            progress(tokens)
            continue

        curr = current_and_progress(Name, tokens)
        assert get_definition(definitions, curr.value) is None
        defined = curr

        current_and_progress(Assignment, tokens)

        acc_tokens = []
        while not isinstance(current(tokens), Semicolon):
            acc_tokens.append(current(tokens))
            progress(tokens)
        arrow_splits = [[]]
        for t in acc_tokens:
            if isinstance(t, Arrow):
                arrow_splits.append([])
            else:
                arrow_splits[-1].append(t)
        assert len(arrow_splits) in [1, 2]

        params: List[Parameter] = []
        if len(arrow_splits) == 2:
            for t in arrow_splits[0]:
                assert isinstance(t, Name)
                params.append(Parameter(t.value))

        exp = expression_parser(arrow_splits[-1])
        definitions.append(Definition(defined.value, params, exp))

    return definitions

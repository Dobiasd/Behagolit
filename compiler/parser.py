from abc import ABC
from dataclasses import dataclass
from typing import List, Optional, Type, Sequence, Dict
from typing import TypeVar, Generic, Any

from lexer import Token, Name, Assignment, StringConstant, IntegerConstant, Semicolon, ScopeOpen, ScopeClose, \
    BoolConstant

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
class ConstantBoolExpression(ConstantExpression):
    value: bool


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
    params: List[Parameter]
    expression: Expression


def parser(tokens: List[Token]) -> Dict[str, Definition]:
    definitions: Dict[str, Definition] = {}

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

    def add_definition(def_scope: List[str], name: str, definition: Definition) -> None:
        definitions[".".join(def_scope + [name])] = definition

    last_defined_name: Optional[str] = None
    scope: List[str] = []

    while not done():
        if isinstance(current(), ScopeOpen):
            assert last_defined_name is not None
            scope.append(last_defined_name)
            progress()
            continue

        if isinstance(current(), ScopeClose):
            assert last_defined_name is not None
            scope.pop(-1)
            if len(scope) == 0:
                last_defined_name = None
            progress()
            continue

        if isinstance(current(), Semicolon):
            progress()
            continue

        curr_name = current_and_progress(Name)
        assert curr_name.value not in definitions
        defined = curr_name
        last_defined_name = defined.value

        params: List[Parameter] = []
        while not isinstance(current(), Assignment):
            params.append(Parameter(current_and_progress(Name).value))

        current_and_progress(Assignment)

        curr = current()
        if isinstance(curr, StringConstant):
            add_definition(scope, defined.value, Definition(params, ConstantStringExpression(curr.value)))
        if isinstance(curr, BoolConstant):
            add_definition(scope, defined.value, Definition(params, ConstantBoolExpression(curr.value)))
        elif isinstance(curr, IntegerConstant):
            add_definition(scope, defined.value, Definition(params, ConstantIntegerExpression(curr.value)))
        elif isinstance(curr, Name):
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
                if isinstance(current_arg, BoolConstant):
                    args.append(ConstantBoolExpression(current_arg.value))
                progress()
            add_definition(scope, defined.value, Definition(params, Call(func.value, args)))
        else:
            raise RuntimeError("Wat")
        progress()

    return definitions

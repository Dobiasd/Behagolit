from abc import ABC
from dataclasses import dataclass
from typing import List, Sequence, Dict, Tuple
from typing import TypeVar, Generic, Any

from .lexer import Token, Name, Assignment, StringConstant, IntegerConstant, Semicolon, BoolConstant, LeftParenthesis, \
    RightParenthesis, Colon, Arrow, Comma

T = TypeVar('T')


# https://stackoverflow.com/a/66941316/1866775
class MyTypeChecker(Generic[T]):
    def is_right_type(self, x: Any) -> bool:
        return isinstance(x, self.__orig_class__.__args__[0])  # type: ignore


@dataclass
class TypeSignature(ABC):
    pass


@dataclass
class TypeSignaturePlain(TypeSignature):
    name: str


@dataclass
class TypeSignatureFunction(TypeSignature):
    params: List[TypeSignature]
    return_type: TypeSignature


@dataclass
class StructField:
    field_name: str
    field_type: TypeSignature


@dataclass
class Struct(TypeSignature):
    fields: List[StructField]


@dataclass
class Union(TypeSignature):
    options: List[TypeSignature]


def parse_type(tokens: List[Token]) -> Tuple[TypeSignature, int]:
    idx = 0
    curr = tokens[idx]
    idx += 1
    if isinstance(curr, Name):
        return TypeSignaturePlain(curr.value), idx
    if isinstance(curr, LeftParenthesis):
        param_types = []
        new_type, progress = parse_type(tokens[idx:])
        param_types.append(new_type)
        idx += progress
        while isinstance(tokens[idx], Comma):
            idx += 1
            new_type, progress = parse_type(tokens[idx:])
            param_types.append(new_type)
            idx += progress
        assert isinstance(tokens[idx], Arrow)
        idx += 1
        return_type, progress = parse_type(tokens[idx:])
        idx += progress
        assert isinstance(tokens[idx], RightParenthesis)
        idx += 1
        return TypeSignatureFunction(param_types, return_type), idx
    assert False


@dataclass
class Parameter(Token):
    name: str
    type_sig: TypeSignature


@dataclass
class Expression(ABC):
    pass


@dataclass
class PlainExpression(Expression):
    type_sig: TypeSignaturePlain
    value: Any


@dataclass
class Call(Expression):
    function_name: str
    args: Sequence[Expression]


def get_const_int(exp: PlainExpression) -> int:
    assert exp.type_sig == TypeSignaturePlain("Integer")
    assert isinstance(exp.value, int)
    return exp.value


def get_const_str(exp: PlainExpression) -> str:
    assert exp.type_sig == TypeSignaturePlain("String")
    assert isinstance(exp.value, str)
    return exp.value


def get_const_bool(exp: PlainExpression) -> bool:
    assert exp.type_sig == TypeSignaturePlain("Boolean")
    assert isinstance(exp.value, bool)
    return exp.value


@dataclass
class Definition:
    def_type: TypeSignature
    params: List[Parameter]
    expression: Expression


def parse_expression(tokens: List[Token], allow_eat_args_right: bool = True) -> Tuple[Expression, int]:
    idx = 0
    curr = tokens[idx]
    if isinstance(curr, StringConstant):
        idx += 1
        return PlainExpression(TypeSignaturePlain("String"), curr.value), idx
    if isinstance(curr, IntegerConstant):
        idx += 1
        return PlainExpression(TypeSignaturePlain("Integer"), curr.value), idx
    if isinstance(curr, BoolConstant):
        idx += 1
        return PlainExpression(TypeSignaturePlain("Boolean"), curr.value), idx
    if isinstance(curr, LeftParenthesis):
        idx += 1
        exp, progress = parse_expression(tokens[idx:])
        idx += progress
        assert isinstance(tokens[idx], RightParenthesis)
        idx += 1
        return exp, idx
    if isinstance(curr, Name):
        assert isinstance(curr, Name)
        func_name = curr.value
        idx += 1
        args = []
        if not allow_eat_args_right:
            return Call(func_name, args), idx
        while not isinstance(tokens[idx], Semicolon) and not isinstance(tokens[idx], RightParenthesis):
            if isinstance(tokens[idx], LeftParenthesis):
                arg, progress = parse_expression(tokens[idx:])
            else:
                arg, progress = parse_expression(tokens[idx:], allow_eat_args_right=False)
            idx += progress
            args.append(arg)
        return Call(func_name, args), idx
    assert False


def parse_typed_name(tokens: List[Token]) -> Tuple[str, TypeSignature, int]:
    idx = 0
    curr = tokens[idx]
    if not isinstance(curr, Name):
        pass
    assert isinstance(curr, Name)
    def_name = curr.value
    idx += 1
    assert isinstance(tokens[idx], Colon)
    idx += 1
    def_type, progress = parse_type(tokens[idx:])
    idx += progress
    return def_name, def_type, idx


def parse_definition(tokens: List[Token]) -> Tuple[str, Definition, int]:
    idx = 0
    def_name, def_type, progress = parse_typed_name(tokens[idx:])
    idx += progress
    params = []
    while not isinstance(tokens[idx], Assignment):
        param_name, param_type, progress = parse_typed_name(tokens[idx:])
        params.append(Parameter(param_name, param_type))
        idx += progress

    assert isinstance(tokens[idx], Assignment)
    idx += 1
    expression, progress = parse_expression(tokens[idx:])
    idx += progress
    return def_name, Definition(def_type, params, expression), idx


def parser(tokens: List[Token]) \
        -> Tuple[Dict[str, Definition], Dict[str, Struct], Dict[str, Any], Dict[str, List[TypeSignature]]]:
    definitions: Dict[str, Definition] = {}
    custom_struct_types: Dict[str, Struct] = {}
    getters: Dict[str, Any] = {}
    unions: Dict[str, List[TypeSignature]] = {}

    idx = 0
    while isinstance(tokens[idx], Semicolon):
        idx += 1

    while idx < len(tokens):
        def_name, definition, progress = parse_definition(tokens[idx:])
        idx += progress
        definitions[def_name] = definition
        while idx < len(tokens) and isinstance(tokens[idx], Semicolon):
            idx += 1
    return definitions, custom_struct_types, getters, unions

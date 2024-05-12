from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from functools import partial
from typing import List, Dict, Tuple
from typing import TypeVar, Generic, Any

from .expressions import Expression, PrimitiveExpression, Variable, Parameter, Call, Function, PrimitiveClosure
from .lexing import Token, Name, Assignment, StringConstant, IntegerConstant, Semicolon, BoolConstant, LeftParenthesis, \
    RightParenthesis, Colon, Arrow, Comma, ColonEqual

T = TypeVar('T')


# https://stackoverflow.com/a/66941316/1866775
class MyTypeChecker(Generic[T]):
    def is_right_type(self, x: Any) -> bool:
        return isinstance(x, self.__orig_class__.__args__[0])  # type: ignore


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
class Struct(TypeSignature):
    fields: List[str]  # no type attached yet


@dataclass
class Union(TypeSignature):
    options: List[TypeSignature]


def parse_type(tokens: List[Token]) -> Tuple[TypeSignature, int]:
    idx = 0
    curr = tokens[idx]
    idx += 1
    if isinstance(curr, Name):
        return TypeSignaturePrimitive(curr.value), idx
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


def parse_expression(tokens: List[Token], allow_eat_args_right: bool = True) -> Tuple[Expression, int]:
    idx = 0
    curr = tokens[idx]
    if isinstance(curr, StringConstant):
        idx += 1
        return PrimitiveExpression(curr.value), idx
    if isinstance(curr, IntegerConstant):
        idx += 1
        return PrimitiveExpression(curr.value), idx
    if isinstance(curr, BoolConstant):
        idx += 1
        return PrimitiveExpression(curr.value), idx
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
        expressions: List[Expression] = [Variable(func_name)]
        if not allow_eat_args_right:
            return Variable(func_name), idx
        while not isinstance(tokens[idx], Semicolon) and not isinstance(tokens[idx], RightParenthesis):
            if isinstance(tokens[idx], LeftParenthesis):
                exp, progress = parse_expression(tokens[idx:])
            else:
                exp, progress = parse_expression(tokens[idx:], allow_eat_args_right=False)
            idx += progress
            expressions.append(exp)
        if len(expressions) == 1:
            return Variable(func_name), idx
        else:
            return Call(expressions[0], expressions[1:]), idx
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


def parse_definition(tokens: List[Token]) -> Tuple[str, Expression, int]:
    idx = 0
    def_name, def_type, progress = parse_typed_name(tokens[idx:])
    idx += progress
    params = []
    while not isinstance(tokens[idx], Assignment):
        param_name, param_type, progress = parse_typed_name(tokens[idx:])
        params.append(Parameter(param_name))
        idx += progress
    assert isinstance(tokens[idx], Assignment)
    idx += 1
    expression, progress = parse_expression(tokens[idx:])
    idx += progress
    if len(params) == 0:
        return def_name, expression, idx
    else:
        return def_name, Function(params, expression), idx


def parse_struct_definition(tokens: List[Token]) -> Tuple[str, Struct, int]:
    idx = 0
    curr = tokens[idx]
    assert isinstance(curr, Name)
    struct_name = curr.value
    idx += 1
    assert tokens[idx] == ColonEqual()
    idx += 1
    assert tokens[idx] == Name("struct")
    idx += 1
    fields: List[str] = []
    while idx < len(tokens) and not isinstance(tokens[idx], Semicolon):
        field_name, field_type, progress = parse_typed_name(tokens[idx:])
        idx += progress
        fields.append(field_name)
    return struct_name, Struct(fields), idx


def parse_union_definition(tokens: List[Token]) -> Tuple[str, Union, int]:
    idx = 0
    curr = tokens[idx]
    assert isinstance(curr, Name)
    union_namme = curr.value
    idx += 1
    assert tokens[idx] == ColonEqual()
    idx += 1
    assert tokens[idx] == Name("union")
    idx += 1
    options: List[TypeSignature] = []
    while idx < len(tokens) and not isinstance(tokens[idx], Semicolon):
        option = tokens[idx]
        assert isinstance(option, Name)
        idx += 1
        options.append(TypeSignaturePrimitive(option.value))
    return union_namme, Union(options), idx


def parse(tokens: List[Token]) \
        -> Tuple[Dict[str, Expression], Dict[str, Struct], Dict[str, Union]]:
    definitions: Dict[str, Expression] = {}
    structs: Dict[str, Struct] = {}
    unions: Dict[str, Union] = {}

    idx = 0
    while isinstance(tokens[idx], Semicolon):
        idx += 1

    while idx < len(tokens):
        if tokens[idx + 1] == ColonEqual():
            if tokens[idx + 2] == Name("union"):
                union_name, union, progress = parse_union_definition(tokens[idx:])
                idx += progress
                unions[union_name] = union
            elif tokens[idx + 2] == Name("struct"):
                struct_name, struct, progress = parse_struct_definition(tokens[idx:])
                idx += progress
                structs[struct_name] = struct
            else:
                assert False
        else:
            def_name, definition, progress = parse_definition(tokens[idx:])
            idx += progress
            definitions[def_name] = definition
        while idx < len(tokens) and isinstance(tokens[idx], Semicolon):
            idx += 1
    for name, struct in structs.items():
        definitions[name] = PrimitiveClosure(list(map(lambda f: Parameter(f), struct.fields)), {},
                                             partial(create_struct, struct.fields))
        for field in struct.fields:
            definitions[name + "." + field] = PrimitiveClosure([Parameter("s")], {}, partial(get_struct_field, field))
    return definitions, structs, unions


def get_struct_field(field_name: str, struct: PrimitiveExpression) -> PrimitiveExpression:
    assert isinstance(struct.value, dict)
    ret = struct.value[field_name]
    assert isinstance(ret, PrimitiveExpression)
    return ret


def create_struct(field_names: List[str], *args: Expression) -> PrimitiveExpression:
    return PrimitiveExpression(dict(zip(field_names, list(args))))

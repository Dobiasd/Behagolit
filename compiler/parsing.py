from __future__ import annotations

from collections import defaultdict
from functools import partial
from typing import List, Dict, Tuple, Set

from .expressions import Expression, PrimitiveExpression, Variable, Call, CompoundFunction, PrimitiveFunction, Constant, \
    Definition
from .lexing import Token, Name, Assignment, StringConstant, IntegerConstant, Semicolon, BoolConstant, LeftParenthesis, \
    RightParenthesis, Colon, Arrow, Comma, ColonEqual, NoneConstant, VerticalBar
from .type_signatures import TypeSignaturePrimitive, TypeSignature, Struct, SumType, TypeSignatureFunction, StructField


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
    if isinstance(curr, NoneConstant):
        idx += 1
        return PrimitiveExpression(None), idx
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
    param_types = []
    while not isinstance(tokens[idx], Assignment):
        param_name, param_type, progress = parse_typed_name(tokens[idx:])
        params.append(param_name)
        param_types.append(param_type)
        idx += progress
    assert isinstance(tokens[idx], Assignment)
    idx += 1
    expression, progress = parse_expression(tokens[idx:])
    idx += progress

    if len(params) == 0:
        return def_name, Constant(expression, def_type), idx
    else:
        return def_name, CompoundFunction(TypeSignatureFunction(param_types, def_type), params, expression), idx


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
    fields: List[StructField] = []
    while idx < len(tokens) and not isinstance(tokens[idx], Semicolon):
        field_name, field_type, progress = parse_typed_name(tokens[idx:])
        idx += progress
        fields.append(StructField(field_name, field_type))
    return struct_name, Struct(fields), idx


def parse_union_definition(tokens: List[Token]) -> Tuple[str, SumType, int]:
    idx = 0
    curr = tokens[idx]
    assert isinstance(curr, Name)
    union_name = curr.value
    idx += 1
    assert tokens[idx] == ColonEqual()
    idx += 1
    assert tokens[idx] == Name("union")
    idx += 1
    options: List[TypeSignature] = []
    while idx < len(tokens) and not isinstance(tokens[idx], Semicolon):
        if len(options) > 0:
            assert isinstance(tokens[idx], VerticalBar)
            idx += 1
        option = tokens[idx]
        assert isinstance(option, Name)
        idx += 1
        options.append(TypeSignaturePrimitive(option.value))
    return union_name, SumType(options), idx


def parse(tokens: List[Token]) -> Tuple[Dict[str, Definition], Dict[str, Set[str]]]:
    definitions: Dict[str, Definition] = {}
    structs: Dict[str, Struct] = {}
    unions: Dict[str, SumType] = {}

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
        field_names = list(map(lambda f: f.name, struct.fields))
        field_types = list(map(lambda f: f.type_sig, struct.fields))
        definitions[name] = PrimitiveFunction(
            TypeSignatureFunction(field_types, TypeSignaturePrimitive(name)),
            field_names, partial(create_struct, field_names))
        for field in struct.fields:
            definitions[name + "." + field.name] = PrimitiveFunction(
                TypeSignatureFunction([TypeSignaturePrimitive(name)], field.type_sig),
                ["the_struct"],
                partial(get_struct_field, field.name))
    type_aliases: Dict[str, Set[str]] = defaultdict(set)
    for name, union in unions.items():
        for option in union.options:
            assert isinstance(option, TypeSignaturePrimitive)
            type_aliases[name].add(option.name)
    return definitions, type_aliases


def get_struct_field(field_name: str, struct: PrimitiveExpression) -> PrimitiveExpression:
    assert isinstance(struct.value, dict)
    ret = struct.value[field_name]
    assert isinstance(ret, PrimitiveExpression)
    return ret


def create_struct(field_names: List[str], *args: PrimitiveExpression) -> PrimitiveExpression:
    return PrimitiveExpression(dict(zip(field_names, list(args))))

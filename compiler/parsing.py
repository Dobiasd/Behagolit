from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from functools import partial
from typing import List, Dict, Tuple, Set

from .expressions import Expression, PrimitiveExpression, Variable, Call, CompoundFunction, PrimitiveFunction, Constant, \
    Definition
from .lexing import Token, Name, Assignment, StringConstant, IntegerConstant, Semicolon, BoolConstant, LeftParenthesis, \
    RightParenthesis, Colon, Arrow, Comma, ColonEqual, NoneConstant, VerticalBar, ScopeOpen, ScopeClose
from .type_signatures import TypeSignaturePrimitive, TypeSignature, TypeSignatureFunction, BuiltInPrimitiveType, \
    CustomPrimitiveType


@dataclass(frozen=True)
class StructField(TypeSignature):
    name: str
    type_sig: TypeSignature


@dataclass(frozen=True)
class Struct(TypeSignature):
    fields: List[StructField]


@dataclass(frozen=True)
class SumType(TypeSignature):
    options: List[TypeSignature]


def is_primitive_type_name(name: str) -> bool:
    return name in ["Integer", "String", "Boolean", "None"]


def primitive_type_signature_from_name(name: str) -> TypeSignaturePrimitive:
    return TypeSignaturePrimitive(
        BuiltInPrimitiveType[name.upper()] if is_primitive_type_name(name) else CustomPrimitiveType(name))


def parse_type(tokens: List[Token]) -> Tuple[TypeSignature, int]:
    idx = 0
    curr = tokens[idx]
    idx += 1
    if isinstance(curr, Name):
        return primitive_type_signature_from_name(curr.value), idx
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


def parse_expression(tokens: List[Token]) -> Tuple[Expression, int]:
    idx = 0
    parts: List[Expression] = []
    while not isinstance(tokens[idx], RightParenthesis) and not isinstance(tokens[idx], Semicolon):
        curr = tokens[idx]
        if isinstance(curr, StringConstant):
            idx += 1
            parts.append(PrimitiveExpression(curr.value))
            continue
        if isinstance(curr, IntegerConstant):
            idx += 1
            parts.append(PrimitiveExpression(curr.value))
            continue
        if isinstance(curr, BoolConstant):
            idx += 1
            parts.append(PrimitiveExpression(curr.value))
            continue
        if isinstance(curr, NoneConstant):
            idx += 1
            parts.append(PrimitiveExpression(None))
            continue
        if isinstance(curr, LeftParenthesis):
            idx += 1
            exp, progress = parse_expression(tokens[idx:])
            idx += progress
            assert isinstance(tokens[idx], RightParenthesis)
            idx += 1
            parts.append(exp)
            continue
        if isinstance(curr, Name):
            idx += 1
            parts.append(Variable(curr.value))
            continue
        assert False
    if len(parts) == 1:
        return parts[0], idx
    else:
        return Call(parts[0], parts[1:]), idx


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

    sub_definitions: Dict[str, Definition] = {}
    if idx < len(tokens) - 1 and isinstance(tokens[idx], Semicolon) and isinstance(tokens[idx + 1], ScopeOpen):
        idx += 2
        while not isinstance(tokens[idx], ScopeClose):
            if isinstance(tokens[idx], Semicolon):
                idx += 1
                continue
            sub_def_name, sub_definition, progress = parse_definition(tokens[idx:])
            sub_definitions[sub_def_name] = sub_definition
            idx += progress
            while idx < len(tokens) and isinstance(tokens[idx], Semicolon):
                idx += 1
        assert isinstance(tokens[idx], ScopeClose)
        idx += 1

    if len(params) == 0:
        return def_name, Constant(sub_definitions, expression, def_type), idx
    else:
        return def_name, CompoundFunction(sub_definitions, TypeSignatureFunction(param_types, def_type), params,
                                          expression), idx


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
        options.append(primitive_type_signature_from_name(option.value))
    return union_name, SumType(options), idx


def with_sub_definitions(definition: Definition, sub_definitions: Dict[str, Definition]) -> Definition:
    if isinstance(definition, Constant):
        return Constant(sub_definitions, definition.expression, definition.type_sig)
    if isinstance(definition, CompoundFunction):
        return CompoundFunction(sub_definitions, definition.type_sig, definition.parameters, definition.body)
    assert False


def parse(tokens: List[Token]) -> Tuple[
    Dict[str, Definition], Dict[TypeSignaturePrimitive, Set[TypeSignaturePrimitive]]]:
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
            {},
            TypeSignatureFunction(field_types,
                                  primitive_type_signature_from_name(name)),
            field_names, partial(create_struct, field_names))
        for field in struct.fields:
            definitions[name + "." + field.name] = PrimitiveFunction(
                {},
                TypeSignatureFunction(
                    [primitive_type_signature_from_name(name)],
                    field.type_sig),
                ["the_struct"],
                partial(get_struct_field, field.name))
    type_aliases: Dict[TypeSignaturePrimitive, Set[TypeSignaturePrimitive]] = defaultdict(set)
    for name, union in unions.items():
        for option in union.options:
            assert isinstance(option, TypeSignaturePrimitive)
            type_aliases[TypeSignaturePrimitive(CustomPrimitiveType(name))].add(option)
    return definitions, type_aliases


def get_struct_field(field_name: str, struct: PrimitiveExpression) -> PrimitiveExpression:
    assert isinstance(struct.value, dict)
    ret = struct.value[field_name]
    assert isinstance(ret, PrimitiveExpression)
    return ret


def create_struct(field_names: List[str], *args: PrimitiveExpression) -> PrimitiveExpression:
    return PrimitiveExpression(dict(zip(field_names, list(args))))

from functools import partial
from typing import Dict, Set, List

from .expressions import Call, Variable, PrimitiveExpression, CompoundFunction, Constant, Definition, PrimitiveFunction, \
    Expression
from .type_signatures import TypeSignatureFunction, TypeSignaturePrimitive, TypeSignature, BuiltInPrimitiveType


class TypeCheckException(Exception):
    pass


def type_assert(condition: bool, error_msg: str) -> None:
    if not condition:
        raise TypeCheckException(error_msg)


def assert_types_are_the_same(
        type_aliases: Dict[TypeSignaturePrimitive, Set[TypeSignaturePrimitive]],
        a: TypeSignature, b: TypeSignature,
        error_msg: str) -> None:
    if isinstance(a, TypeSignaturePrimitive) and isinstance(b, TypeSignaturePrimitive):
        a_plain = type_aliases.get(a, {a})
        b_plain = type_aliases.get(b, {b})
        if len(a_plain) > 1 and len(b_plain) > 1:
            type_assert(a_plain == b_plain, error_msg)
        elif len(a_plain) == 1 and len(b_plain) == 1:
            type_assert(a == b, error_msg)
        elif len(a_plain) == 1:
            single_a = next(iter(a_plain))
            assert isinstance(single_a, TypeSignaturePrimitive)
            type_assert(single_a in b_plain, error_msg)
        elif len(b_plain) == 1:
            single_b = next(iter(b_plain))
            assert isinstance(single_b, TypeSignaturePrimitive)
            type_assert(single_b in a_plain, error_msg)
        else:
            assert False
    else:
        type_assert(a == b, error_msg)


def derive_type(exp: PrimitiveExpression) -> TypeSignaturePrimitive:
    if isinstance(exp.value, bool):
        return TypeSignaturePrimitive(BuiltInPrimitiveType.BOOLEAN)
    if isinstance(exp.value, int):
        return TypeSignaturePrimitive(BuiltInPrimitiveType.INTEGER)
    if isinstance(exp.value, str):
        return TypeSignaturePrimitive(BuiltInPrimitiveType.STRING)
    assert False


def check_call(definitions: Dict[str, Definition],
               type_aliases: Dict[TypeSignaturePrimitive, Set[TypeSignaturePrimitive]],
               call: Call) -> None:
    if isinstance(call.operator, Variable) and call.operator.name == "ifElse":
        return
    if isinstance(call.operator, Call):
        op_sig = get_type(definitions, call.operator)
    else:
        assert isinstance(call.operator, Variable)
        op = definitions[call.operator.name]
        assert isinstance(op, (Constant, PrimitiveFunction, CompoundFunction))
        op_sig = op.type_sig
    arg_types = list(map(partial(get_type, definitions), call.operands))
    assert isinstance(op_sig, TypeSignatureFunction)
    type_assert(len(arg_types) == len(op_sig.params), "Wrong number of arguments")
    for arg_type, param_type in zip(arg_types, op_sig.params):
        assert_types_are_the_same(type_aliases, arg_type, param_type, "todo message")


def get_type(definitions: Dict[str, Definition], expression: Expression) -> TypeSignature:
    if isinstance(expression, Call):
        if isinstance(expression.operator, Variable) and expression.operator.name == "ifElse":
            assert get_type(definitions, expression.operands[0]) == TypeSignaturePrimitive(BuiltInPrimitiveType.BOOLEAN)
            assert get_type(definitions, expression.operands[1]) == get_type(definitions, expression.operands[2])
            return get_type(definitions, expression.operands[1])
        if isinstance(expression.operator, (CompoundFunction, PrimitiveFunction)):
            return expression.operator.type_sig
        assert isinstance(expression.operator, Variable)
        d = definitions[expression.operator.name]
        assert isinstance(d, (CompoundFunction, PrimitiveFunction))
        if len(expression.operands) != len(d.parameters):
            return TypeSignatureFunction(d.type_sig.params[len(expression.operands):], d.type_sig.return_type)
        return d.type_sig.return_type
    if isinstance(expression, Variable):
        d = definitions[expression.name]
        if isinstance(d, Constant):
            return d.type_sig
        if isinstance(d, (CompoundFunction, PrimitiveFunction)):
            return d.type_sig
        assert False
    if isinstance(expression, PrimitiveExpression):
        return derive_type(expression)
    assert False


def attach_sub_definitions(definitions: Dict[str, Definition],
                           sub_definitions: Dict[str, Definition]) -> Dict[str, Definition]:
    return definitions | sub_definitions


def extend_definitions(definitions: Dict[str, Definition],
                       parameters: List[str],
                       args: List[TypeSignature]) -> Dict[str, Definition]:
    return definitions | dict(map(lambda name_and_sig: (name_and_sig[0], Constant({}, Expression(), name_and_sig[1])),
                                  zip(parameters, args)))


def check_definition(definitions: Dict[str, Definition],
                     item: Definition,
                     type_aliases: Dict[TypeSignaturePrimitive, Set[TypeSignaturePrimitive]]) -> None:
    if len(item.sub_definitions) > 0:
        for sub_def in item.sub_definitions.values():
            if isinstance(item, CompoundFunction):
                check_definition(
                    extend_definitions(attach_sub_definitions(definitions, item.sub_definitions), item.parameters,
                                       item.type_sig.params), sub_def, type_aliases)
            else:
                check_definition(attach_sub_definitions(definitions, item.sub_definitions), sub_def, type_aliases)
    if isinstance(item, Constant):
        if isinstance(item.expression, PrimitiveExpression):
            assert_types_are_the_same(type_aliases, derive_type(item.expression), item.type_sig,
                                      "Invalid constant type")
        elif isinstance(item.expression, Call):
            check_call(attach_sub_definitions(definitions, item.sub_definitions), type_aliases, item.expression)
    if isinstance(item, PrimitiveFunction):
        pass  # PrimitiveFunction is only instantiated from standard library. We have to trust it.
    elif isinstance(item, CompoundFunction):
        type_assert(isinstance(item.type_sig, TypeSignatureFunction), "Invalid type signature for function")
        type_assert(len(item.type_sig.params) == len(item.parameters), "Inconsistent number of parameters")
        if isinstance(item, CompoundFunction):
            if isinstance(item.body, Call):
                check_call(
                    extend_definitions(attach_sub_definitions(definitions, item.sub_definitions), item.parameters,
                                       item.type_sig.params), type_aliases,
                    item.body)
            elif isinstance(item.body, Variable):
                type_assert(get_type(
                    extend_definitions(attach_sub_definitions(definitions, item.sub_definitions), item.parameters,
                                       item.type_sig.params),
                    item.body) == item.type_sig.return_type, "Invalid definition")
                pass
            else:
                assert False
        else:
            assert False


def check_types(definitions: Dict[str, Definition],
                type_aliases: Dict[TypeSignaturePrimitive, Set[TypeSignaturePrimitive]]) -> None:
    for def_name, item in definitions.items():
        check_definition(definitions, item, type_aliases)

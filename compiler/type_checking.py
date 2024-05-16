from functools import partial
from typing import Dict, Set

from .expressions import Call, Variable, PrimitiveExpression, CompoundFunction, Constant, Definition, PrimitiveFunction, \
    Expression
from .type_signatures import TypeSignatureFunction, TypeSignaturePrimitive, TypeSignature


def type_assert(condition: bool, error_msg: str) -> None:
    if not condition:
        raise TypeError(error_msg)


def assert_types_are_the_same(type_aliases: Dict[str, Set[str]], a: TypeSignature, b: TypeSignature,
                              error_msg: str) -> None:
    if isinstance(a, TypeSignaturePrimitive) and isinstance(b, TypeSignaturePrimitive):
        a_plain = type_aliases.get(a.name, {a})
        b_plain = type_aliases.get(b.name, {b})
        if len(a_plain) > 1 and len(b_plain) > 1:
            type_assert(a_plain == b_plain, error_msg)
        elif len(a_plain) == 1 and len(b_plain) == 1:
            type_assert(a == b, error_msg)
        elif len(a_plain) == 1:
            single_a = next(iter(a_plain))
            assert isinstance(single_a, TypeSignaturePrimitive)
            type_assert(single_a.name in b_plain, error_msg)
        elif len(b_plain) == 1:
            single_b = next(iter(b_plain))
            assert isinstance(single_b, TypeSignaturePrimitive)
            type_assert(single_b.name in a_plain, error_msg)
        else:
            assert False
    else:
        type_assert(a == b, error_msg)


def derive_type(exp: PrimitiveExpression) -> TypeSignaturePrimitive:
    if isinstance(exp.value, bool):
        return TypeSignaturePrimitive("Boolean")
    if isinstance(exp.value, int):
        return TypeSignaturePrimitive("Integer")
    if isinstance(exp.value, str):
        return TypeSignaturePrimitive("String")
    assert False


def check_call(ast: Dict[str, Definition], type_aliases: Dict[str, Set[str]], call: Call) -> None:
    assert isinstance(call.operator, Variable)
    if call.operator.name != "ifElse":
        op = ast[call.operator.name]
        assert isinstance(op, (PrimitiveFunction, CompoundFunction))
        arg_types = list(map(partial(get_type, ast), call.operands))
        type_assert(len(arg_types) == len(op.type_sig.params), "Wrong number of arguments")
        for arg_type, param_type in zip(arg_types, op.type_sig.params):
            assert_types_are_the_same(type_aliases, arg_type, param_type, "todo message")


def get_type(ast: Dict[str, Definition], expression: Expression) -> TypeSignature:
    if isinstance(expression, Call):
        if isinstance(expression.operator, Variable) and expression.operator.name == "ifElse":
            assert get_type(ast, expression.operands[0]) == TypeSignaturePrimitive("Boolean")
            assert get_type(ast, expression.operands[1]) == get_type(ast, expression.operands[2])
            return get_type(ast, expression.operands[1])
        return get_type(ast, expression.operator)
    if isinstance(expression, Variable):
        d = ast[expression.name]
        if isinstance(d, Constant):
            return get_type(ast, d.expression)
        if isinstance(d, (CompoundFunction, PrimitiveFunction)):
            return d.type_sig.return_type
    if isinstance(expression, PrimitiveExpression):
        return derive_type(expression)
    assert False


def check_types(ast: Dict[str, Definition], type_aliases: Dict[str, Set[str]]) -> None:
    for item in ast.values():
        if isinstance(item, Constant):
            if isinstance(item.expression, PrimitiveExpression):
                assert_types_are_the_same(type_aliases, derive_type(item.expression), item.type_sig,
                                          "Invalid constant type")
            if isinstance(item.expression, Call):
                check_call(ast, type_aliases, item.expression)
        if isinstance(item, (PrimitiveFunction, CompoundFunction)):
            # todo: does the below actually do something?
            type_assert(isinstance(item.type_sig, TypeSignatureFunction), "Invalid type signature for function")
            type_assert(len(item.type_sig.params) == len(item.parameters), "Inconsistent number of parameters")
            if isinstance(item, CompoundFunction):
                if isinstance(item.body, Call):
                    if isinstance(item.body.operator, Variable):
                        if item.body.operator.name in ast:
                            op = ast[item.body.operator.name]
                            assert isinstance(op, (PrimitiveFunction, CompoundFunction))
                            type_assert(len(op.type_sig.params) == len(item.body.operands),
                                        "Inconsistent number of arguments")
                            for x, y in zip(op.type_sig.params, item.body.operands):
                                if isinstance(y, Variable):
                                    checked = False
                                    for idx, p in enumerate(item.parameters):
                                        if p == y.name:
                                            type_assert(x == item.type_sig.params[idx], "todo message")
                                            checked = True
                                            break
                                    if not checked:
                                        y2 = ast[y.name]
                                        if isinstance(y2, (PrimitiveFunction, CompoundFunction)):
                                            type_assert(x == y2.type_sig, "todo message")
                                        else:
                                            type_assert(False, "Check not yet implemented")
                                elif isinstance(y, PrimitiveExpression):
                                    # todo: attach sig to PrimitiveExpression instead or parse them as Constant?
                                    type_assert(derive_type(y) == x, "Invalid type")

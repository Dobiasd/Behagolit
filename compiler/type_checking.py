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


def check_call(ast: Dict[str, Definition], type_aliases: Dict[TypeSignaturePrimitive, Set[TypeSignaturePrimitive]],
               call: Call) -> None:
    assert isinstance(call.operator, Variable)
    if call.operator.name != "ifElse":
        op = ast[call.operator.name]
        assert isinstance(op, (Constant, PrimitiveFunction, CompoundFunction))
        arg_types = list(map(partial(get_type, ast), call.operands))
        assert isinstance(op.type_sig, TypeSignatureFunction)
        type_assert(len(arg_types) == len(op.type_sig.params), "Wrong number of arguments")
        for arg_type, param_type in zip(arg_types, op.type_sig.params):
            assert_types_are_the_same(type_aliases, arg_type, param_type, "todo message")


def get_type(ast: Dict[str, Definition], expression: Expression) -> TypeSignature:
    if isinstance(expression, Call):
        if isinstance(expression.operator, Variable) and expression.operator.name == "ifElse":
            assert get_type(ast, expression.operands[0]) == TypeSignaturePrimitive(BuiltInPrimitiveType.BOOLEAN)
            assert get_type(ast, expression.operands[1]) == get_type(ast, expression.operands[2])
            return get_type(ast, expression.operands[1])
        if isinstance(expression.operator, (CompoundFunction, PrimitiveFunction)):
            return expression.operator.type_sig
        if isinstance(expression.operator, Variable):
            d = ast[expression.operator.name]
            assert isinstance(d, (CompoundFunction, PrimitiveFunction))
            return d.type_sig.return_type
        return get_type(ast, expression.operator)
    if isinstance(expression, Variable):
        d = ast[expression.name]
        if isinstance(d, Constant):
            return d.type_sig
        if isinstance(d, (CompoundFunction, PrimitiveFunction)):
            return d.type_sig
    if isinstance(expression, PrimitiveExpression):
        return derive_type(expression)
    assert False


def extend_ast(ast: Dict[str, Definition],
               parameters: List[str],
               args: List[TypeSignature]) -> Dict[str, Definition]:
    return ast | dict(map(lambda name_and_sig: (name_and_sig[0], Constant(Expression(), name_and_sig[1])),
                          zip(parameters, args)))


def check_types(ast: Dict[str, Definition],
                type_aliases: Dict[TypeSignaturePrimitive, Set[TypeSignaturePrimitive]]) -> None:
    for item in ast.values():
        if isinstance(item, Constant):
            if isinstance(item.expression, PrimitiveExpression):
                assert_types_are_the_same(type_aliases, derive_type(item.expression), item.type_sig,
                                          "Invalid constant type")
            if isinstance(item.expression, Call):
                check_call(ast, type_aliases, item.expression)
        if isinstance(item, PrimitiveFunction):
            pass  # PrimitiveFunction is only instantiated from standard library. We have to trust it.
        if isinstance(item, CompoundFunction):
            type_assert(isinstance(item.type_sig, TypeSignatureFunction), "Invalid type signature for function")
            type_assert(len(item.type_sig.params) == len(item.parameters), "Inconsistent number of parameters")
            if isinstance(item, CompoundFunction):
                if isinstance(item.body, Call):
                    check_call(extend_ast(ast, item.parameters, item.type_sig.params), type_aliases, item.body)
                elif isinstance(item.body, Variable):
                    type_assert(get_type(extend_ast(ast, item.parameters, item.type_sig.params),
                                         item.body) == item.type_sig.return_type, "Invalid definition")
                    pass
                else:
                    assert False
            else:
                assert False

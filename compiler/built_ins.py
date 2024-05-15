from typing import Dict

from .expressions import PrimitiveExpression, PrimitiveFunction, Definition
from .type_signatures import TypeSignatureFunction, TypeSignaturePrimitive


def get_const_int(exp: PrimitiveExpression) -> int:
    assert isinstance(exp.value, int)
    return exp.value


def get_const_str(exp: PrimitiveExpression) -> str:
    assert isinstance(exp.value, str)
    return exp.value


def get_const_bool(exp: PrimitiveExpression) -> bool:
    assert isinstance(exp.value, bool)
    return exp.value


def printline(text: PrimitiveExpression) -> PrimitiveExpression:
    print(text.value)
    return PrimitiveExpression(None)


def concat(*args: PrimitiveExpression) -> PrimitiveExpression:
    def get_value(exp: PrimitiveExpression) -> str:
        return get_const_str(exp)

    arg_values = list(map(get_value, args))
    return PrimitiveExpression("".join(arg_values))


def inttostr(number: PrimitiveExpression) -> PrimitiveExpression:
    return PrimitiveExpression(str(get_const_int(number)))


def plus(a: PrimitiveExpression, b: PrimitiveExpression) -> PrimitiveExpression:
    return PrimitiveExpression(get_const_int(a) + get_const_int(b))


def minus(a: PrimitiveExpression, b: PrimitiveExpression) -> PrimitiveExpression:
    return PrimitiveExpression(get_const_int(a) - get_const_int(b))


def multiply(a: PrimitiveExpression, b: PrimitiveExpression) -> PrimitiveExpression:
    return PrimitiveExpression(get_const_int(a) * get_const_int(b))


def divide(a: PrimitiveExpression, b: PrimitiveExpression) -> PrimitiveExpression:
    return PrimitiveExpression(get_const_int(a) // get_const_int(b))


def modulo(a: PrimitiveExpression, b: PrimitiveExpression) -> PrimitiveExpression:
    return PrimitiveExpression(get_const_int(a) % get_const_int(b))


def less(a: PrimitiveExpression, b: PrimitiveExpression) -> PrimitiveExpression:
    return PrimitiveExpression(get_const_int(a) < get_const_int(b))


def greater(a: PrimitiveExpression, b: PrimitiveExpression) -> PrimitiveExpression:
    return PrimitiveExpression(get_const_int(a) > get_const_int(b))


def equal(a: PrimitiveExpression, b: PrimitiveExpression) -> PrimitiveExpression:
    return PrimitiveExpression(a.value == b.value)


def default_environment() -> Dict[str, Definition]:
    return {
        "printLine": PrimitiveFunction(
            TypeSignatureFunction([TypeSignaturePrimitive("String")],
                                  TypeSignaturePrimitive("String")),
            ["message"], printline),
        "concat": PrimitiveFunction(
            TypeSignatureFunction([TypeSignaturePrimitive("String"), TypeSignaturePrimitive("String")],
                                  TypeSignaturePrimitive("String")),
            ["a", "b"], concat),
        "intToStr": PrimitiveFunction(
            TypeSignatureFunction([TypeSignaturePrimitive("Integer")],
                                  TypeSignaturePrimitive("String")),
            ["number"], inttostr),
        "plus": PrimitiveFunction(
            TypeSignatureFunction([TypeSignaturePrimitive("Integer"), TypeSignaturePrimitive("Integer")],
                                  TypeSignaturePrimitive("Integer")),
            ["a", "b"], plus),
        "minus": PrimitiveFunction(
            TypeSignatureFunction([TypeSignaturePrimitive("Integer"), TypeSignaturePrimitive("Integer")],
                                  TypeSignaturePrimitive("Integer")),
            ["a", "b"], minus),
        "multiply": PrimitiveFunction(
            TypeSignatureFunction([TypeSignaturePrimitive("Integer"), TypeSignaturePrimitive("Integer")],
                                  TypeSignaturePrimitive("Integer")),
            ["a", "b"], multiply),
        "divide": PrimitiveFunction(
            TypeSignatureFunction([TypeSignaturePrimitive("Integer"), TypeSignaturePrimitive("Integer")],
                                  TypeSignaturePrimitive("Integer")),
            ["numerator", "denominator"], divide),
        "modulo": PrimitiveFunction(
            TypeSignatureFunction([TypeSignaturePrimitive("Integer"), TypeSignaturePrimitive("Integer")],
                                  TypeSignaturePrimitive("Integer")),
            ["numerator", "denominator"], modulo),
        "less": PrimitiveFunction(
            TypeSignatureFunction([TypeSignaturePrimitive("Integer"), TypeSignaturePrimitive("Integer")],
                                  TypeSignaturePrimitive("Integer")),
            ["a", "b"], less),
        "greater": PrimitiveFunction(
            TypeSignatureFunction([TypeSignaturePrimitive("Integer"), TypeSignaturePrimitive("Integer")],
                                  TypeSignaturePrimitive("Integer")),
            ["a", "b"], greater),
        "equal": PrimitiveFunction(
            TypeSignatureFunction([TypeSignaturePrimitive("Integer"), TypeSignaturePrimitive("Integer")],
                                  TypeSignaturePrimitive("Integer")),
            ["a", "b"], equal),
    }

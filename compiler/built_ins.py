from typing import Dict

from compiler.expressions import PrimitiveExpression, Expression, Parameter, PrimitiveClosure


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


def default_environment() -> Dict[str, Expression]:
    return {
        "printLine": PrimitiveClosure([Parameter("message")], {}, printline),
        "concat": PrimitiveClosure([Parameter("a"), Parameter("b")], {}, concat),
        "intToStr": PrimitiveClosure([Parameter("number")], {}, inttostr),
        "plus": PrimitiveClosure([Parameter("a"), Parameter("b")], {}, plus),
        "minus": PrimitiveClosure([Parameter("a"), Parameter("b")], {}, minus),
        "multiply": PrimitiveClosure([Parameter("a"), Parameter("b")], {}, multiply),
        "divide": PrimitiveClosure([Parameter("numerator"), Parameter("denominator")], {}, divide),
        "modulo": PrimitiveClosure([Parameter("numerator"), Parameter("denominator")], {}, modulo),
        "less": PrimitiveClosure([Parameter("a"), Parameter("b")], {}, less),
        "greater": PrimitiveClosure([Parameter("a"), Parameter("b")], {}, greater),
        "equal": PrimitiveClosure([Parameter("a"), Parameter("b")], {}, equal),
    }

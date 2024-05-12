from typing import Dict

from compiler.expressions import PlainExpression, Expression, Parameter, PrimitiveProcedure


def get_const_int(exp: PlainExpression) -> int:
    #    assert exp.type_sig == TypeSignaturePlain("Integer")
    assert isinstance(exp.value, int)
    return exp.value


def get_const_str(exp: PlainExpression) -> str:
    # assert exp.type_sig == TypeSignaturePlain("String")
    assert isinstance(exp.value, str)
    return exp.value


def get_const_bool(exp: PlainExpression) -> bool:
    # assert exp.type_sig == TypeSignaturePlain("Boolean")
    assert isinstance(exp.value, bool)
    return exp.value


def printline(text: PlainExpression) -> None:
    print(text.value)


def concat(*args: PlainExpression) -> PlainExpression:
    def get_value(exp: PlainExpression) -> str:
        return get_const_str(exp)

    arg_values = list(map(get_value, args))
    return PlainExpression("".join(arg_values))


def inttostr(number: PlainExpression) -> PlainExpression:
    return PlainExpression(str(get_const_int(number)))


def plus(a: PlainExpression, b: PlainExpression) -> PlainExpression:
    return PlainExpression(get_const_int(a) + get_const_int(b))


def minus(a: PlainExpression, b: PlainExpression) -> PlainExpression:
    return PlainExpression(get_const_int(a) - get_const_int(b))


def multiply(a: PlainExpression, b: PlainExpression) -> PlainExpression:
    return PlainExpression(get_const_int(a) * get_const_int(b))


def divide(a: PlainExpression, b: PlainExpression) -> PlainExpression:
    return PlainExpression(get_const_int(a) // get_const_int(b))


def modulo(a: PlainExpression, b: PlainExpression) -> PlainExpression:
    return PlainExpression(get_const_int(a) % get_const_int(b))


def less(a: PlainExpression, b: PlainExpression) -> PlainExpression:
    return PlainExpression(get_const_int(a) < get_const_int(b))


def greater(a: PlainExpression, b: PlainExpression) -> PlainExpression:
    return PlainExpression(get_const_int(a) > get_const_int(b))


def equal(a: PlainExpression, b: PlainExpression) -> PlainExpression:
    return PlainExpression(a.value == b.value)


def default_environment() -> Dict[str, Expression]:
    return {
        "printLine": PrimitiveProcedure([Parameter("message")], {}, printline),
        "concat": PrimitiveProcedure([Parameter("a"), Parameter("b")], {}, concat),
        "intToStr": PrimitiveProcedure([Parameter("number")], {}, inttostr),
        "plus": PrimitiveProcedure([Parameter("a"), Parameter("b")], {}, plus),
        "minus": PrimitiveProcedure([Parameter("a"), Parameter("b")], {}, minus),
        "multiply": PrimitiveProcedure([Parameter("a"), Parameter("b")], {}, multiply),
        "divide": PrimitiveProcedure([Parameter("numerator"), Parameter("denominator")], {}, divide),
        "modulo": PrimitiveProcedure([Parameter("numerator"), Parameter("denominator")], {}, modulo),
        "less": PrimitiveProcedure([Parameter("a"), Parameter("b")], {}, less),
        "greater": PrimitiveProcedure([Parameter("a"), Parameter("b")], {}, greater),
        "equal": PrimitiveProcedure([Parameter("a"), Parameter("b")], {}, equal),
    }

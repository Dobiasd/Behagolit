from functools import partial
from typing import List

from parser import Definition, Call, Expression, ConstantIntegerExpression, ConstantStringExpression, \
    ConstantExpression, get_definition, Variable


def printLine(text: ConstantStringExpression) -> None:
    print(text.value)


def concat(*args: List[ConstantStringExpression]) -> ConstantStringExpression:
    arg_values = list(map(lambda arg: arg.value, args))
    return ConstantStringExpression("".join(arg_values))


def intToStr(number: ConstantIntegerExpression) -> ConstantStringExpression:
    return ConstantStringExpression(str(number.value))


def add(a: ConstantIntegerExpression, b: ConstantIntegerExpression) -> ConstantIntegerExpression:
    return ConstantIntegerExpression(a.value + b.value)


def multiply(a: ConstantIntegerExpression, b: ConstantIntegerExpression) -> ConstantIntegerExpression:
    return ConstantIntegerExpression(a.value * b.value)


builtin_functions = {
    "printLine": printLine,
    "concat": concat,
    "intToStr": intToStr,
    "+": add,
    "*": multiply,
}


def evaluate(ast: List[Definition], expression: Expression) -> ConstantExpression:
    if isinstance(expression, (ConstantIntegerExpression | ConstantStringExpression)):
        return expression
    if isinstance(expression, Call):
        evaluated_args = list(map(partial(evaluate, ast), expression.args))
        assert expression.function in builtin_functions
        return builtin_functions[expression.function](*evaluated_args)
    if isinstance(expression, Variable):
        definition = get_definition(ast, expression.name)
        return evaluate(ast, definition.expression)
    raise RuntimeError("Wat")


def interpret(ast: List[Definition]):
    mains = list(filter(lambda d: d.name == "main", ast))
    assert len(mains) == 1
    main = mains[0].expression
    assert isinstance(main, Call)
    evaluate(ast, main)

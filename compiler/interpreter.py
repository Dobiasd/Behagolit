from functools import partial
from typing import Dict

from parser import Definition, ConstantStringExpression, ConstantIntegerExpression, Expression, Variable, \
    ConstantExpression, Call


def print_line(text: ConstantStringExpression) -> None:
    print(text.value)


def concat(*args: ConstantStringExpression) -> ConstantStringExpression:
    def get_value(exp: ConstantStringExpression) -> str:
        return exp.value

    arg_values = list(map(get_value, args))
    return ConstantStringExpression("".join(arg_values))


def int_to_str(number: ConstantIntegerExpression) -> ConstantStringExpression:
    return ConstantStringExpression(str(number.value))


def add(a: ConstantIntegerExpression, b: ConstantIntegerExpression) -> ConstantIntegerExpression:
    return ConstantIntegerExpression(a.value + b.value)


def multiply(a: ConstantIntegerExpression, b: ConstantIntegerExpression) -> ConstantIntegerExpression:
    return ConstantIntegerExpression(a.value * b.value)


builtin_functions = {
    "printLine": print_line,
    "concat": concat,
    "intToStr": int_to_str,
    "+": add,
    "*": multiply,
}


def replace_variable(replacements: Dict[str, Expression], expression: Expression) -> Expression:
    if isinstance(expression, Variable):
        return replacements[expression.name]
    return expression


def evaluate(ast: Dict[str, Definition], expression: Expression) -> ConstantExpression:
    if isinstance(expression, (ConstantIntegerExpression | ConstantStringExpression)):
        return expression
    if isinstance(expression, Call):
        evaluated_args = list(map(partial(evaluate, ast), expression.args))
        definition = ast.get(expression.function, None)
        if definition is not None:
            param_names = list(map(lambda p: p.name, definition.params))
            arguments = dict(zip(param_names, evaluated_args))
            call = definition.expression
            assert isinstance(call, Call)
            replaced_args = list(map(partial(replace_variable, arguments), call.args))
            return evaluate(ast, Call(call.function, replaced_args))
        assert expression.function in builtin_functions
        return builtin_functions[expression.function](*evaluated_args)  # type: ignore
    if isinstance(expression, Variable):
        definition = ast.get(expression.name, None)
        if not definition:
            raise RuntimeError(f"No definition found for: {expression.name}")
        return evaluate(ast, definition.expression)
    raise RuntimeError("Wat")


def interpret(ast: Dict[str, Definition]) -> None:
    main = ast["main"]
    assert len(main.params) == 0
    assert isinstance(main.expression, Call)
    evaluate(ast, main.expression)

from functools import partial
from typing import Dict, List, Optional

from parser import Definition, ConstantStringExpression, ConstantIntegerExpression, Expression, Variable, \
    ConstantExpression, Call, ConstantBoolExpression


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


def if_else(cond: ConstantBoolExpression, a: Expression, b: Expression) -> Expression:
    if cond.value:
        return a
    else:
        return b


builtin_functions = {
    "printLine": print_line,
    "concat": concat,
    "intToStr": int_to_str,
    "+": add,
    "*": multiply,
    "if": if_else,
}


def replace_params(args: Dict[str, Expression], expression: Expression) -> Expression:
    if isinstance(expression, Variable):
        if expression.name in args:
            return args[expression.name]
    return expression


def fqn(scope: List[str], name: str) -> str:
    scope_fqn = ".".join(scope)
    return (scope_fqn + "." if len(scope_fqn) != 0 else "") + name


def evaluate(ast: Dict[str, Definition], scope: List[str], expression: Expression) -> ConstantExpression:
    if isinstance(expression, (ConstantBoolExpression | ConstantIntegerExpression | ConstantStringExpression)):
        return expression
    if isinstance(expression, Call):
        definition = ast.get(expression.function, None)
        evaluated_args = list(map(partial(evaluate, ast, scope), expression.args))
        if definition is not None:
            param_names = list(map(lambda p: p.name, definition.params))
            extension = dict(map(lambda n, a: (n, Definition([], a)), param_names, evaluated_args))
            extended_ast = ast | extension
            return evaluate(extended_ast, scope, definition.expression)
        assert expression.function in builtin_functions
        return builtin_functions[expression.function](*evaluated_args)  # type: ignore
    if isinstance(expression, Variable):
        var_definition: Optional[Definition] = None
        containing_scope: List[str] = []
        for idx in range(len(scope), -1, -1):
            scope_fqn = fqn(scope[:idx], expression.name)
            var_definition = ast.get(scope_fqn, None)
            if var_definition is not None:
                containing_scope = scope[:idx]
                break
        if not var_definition:
            raise RuntimeError(f"No definition found for: {expression.name}")
        return evaluate(ast, containing_scope + [expression.name], var_definition.expression)
    raise RuntimeError("Wat")


def interpret(ast: Dict[str, Definition]) -> None:
    main = ast["main"]
    assert len(main.params) == 0
    assert isinstance(main.expression, Call)
    evaluate(ast, ["main"], main.expression)

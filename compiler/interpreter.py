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


def plus(a: ConstantIntegerExpression, b: ConstantIntegerExpression) -> ConstantIntegerExpression:
    return ConstantIntegerExpression(a.value + b.value)


def minus(a: ConstantIntegerExpression, b: ConstantIntegerExpression) -> ConstantIntegerExpression:
    return ConstantIntegerExpression(a.value - b.value)


def multiply(a: ConstantIntegerExpression, b: ConstantIntegerExpression) -> ConstantIntegerExpression:
    return ConstantIntegerExpression(a.value * b.value)


def modulo(a: ConstantIntegerExpression, b: ConstantIntegerExpression) -> ConstantIntegerExpression:
    return ConstantIntegerExpression(a.value * b.value)


def less_than(a: ConstantIntegerExpression, b: ConstantIntegerExpression) -> ConstantBoolExpression:
    return ConstantBoolExpression(a.value < b.value)


def greater_than(a: ConstantIntegerExpression, b: ConstantIntegerExpression) -> ConstantBoolExpression:
    return ConstantBoolExpression(a.value > b.value)


builtin_functions = {
    "printLine": print_line,
    "concat": concat,
    "intToStr": int_to_str,
    "+": plus,
    "-": minus,
    "*": multiply,
    "%": modulo,
    "<": less_than,
    ">": greater_than,
}


def replace_params(args: Dict[str, Expression], expression: Expression) -> Expression:
    if isinstance(expression, Variable):
        if expression.name in args:
            return args[expression.name]
    return expression


def fqn(scope: List[str], name: str) -> str:
    scope_fqn = ".".join(scope)
    return (scope_fqn + "." if len(scope_fqn) != 0 else "") + name

def raise_type_error(expected: str, given: str) -> None:
    raise RuntimeError(f"Incorrect type. {given} given. {expected} wanted.")
def assert_types_match(type_name: str, expression: ConstantExpression) -> None:
    if not isinstance(expression,
                      {"Integer": ConstantIntegerExpression,
                       "String": ConstantStringExpression,
                       "Boolean": ConstantBoolExpression,
                       }[type_name]):
        raise_type_error(type_name, expression.type_name)


def evaluate(ast: Dict[str, Definition], scope: List[str], target_type: str,
             expression: Expression) -> ConstantExpression:
    if isinstance(expression, ConstantExpression):
        if target_type != "None":
            assert_types_match(target_type, expression)
        return expression
    if isinstance(expression, Call):
        if expression.function == "ifElse":
            assert len(expression.args) == 3
            cond = evaluate(ast, scope, "Boolean", expression.args[0])
            assert isinstance(cond, ConstantBoolExpression)
            if cond.value:
                return evaluate(ast, scope, target_type, expression.args[1])
            else:
                return evaluate(ast, scope, target_type, expression.args[2])
        definition = ast.get(expression.function, None)
        evaluated_args = list(map(partial(evaluate, ast, scope, "None"), expression.args))
        if definition is not None:
            for param, arg in zip(definition.params, evaluated_args):
                assert_types_match(param.p_type, arg)
            extension = dict(map(lambda p, a: (p.name, Definition(p.p_type, [], a)), definition.params, evaluated_args))
            extended_ast = ast | extension
            return evaluate(extended_ast, [expression.function], definition.def_type, definition.expression)
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
        return evaluate(ast, containing_scope + [expression.name], var_definition.def_type, var_definition.expression)  # todo
    raise RuntimeError("Wat")


def interpret(ast: Dict[str, Definition]) -> None:
    main = ast["main"]
    assert len(main.params) == 0
    assert isinstance(main.expression, Call)
    evaluate(ast, ["main"], "None", main.expression)

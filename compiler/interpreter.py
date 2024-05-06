from functools import partial
from typing import Dict, List, Optional

from .parser import Definition, Expression, Variable, \
    ConstantExpression, Call, TypeSignaturePlain, TypeSignature, PlainType, get_const_str, get_const_int, Struct


def print_line(text: ConstantExpression) -> None:
    assert text.type_sig == TypeSignaturePlain(PlainType.STRING)
    print(text.value)


def concat(*args: ConstantExpression) -> ConstantExpression:
    def get_value(exp: ConstantExpression) -> str:
        return get_const_str(exp)

    arg_values = list(map(get_value, args))
    return ConstantExpression(TypeSignaturePlain(PlainType.STRING), "".join(arg_values))


def int_to_str(number: ConstantExpression) -> ConstantExpression:
    return ConstantExpression(TypeSignaturePlain(PlainType.STRING), str(get_const_int(number)))


def plus(a: ConstantExpression, b: ConstantExpression) -> ConstantExpression:
    return ConstantExpression(TypeSignaturePlain(PlainType.INTEGER), get_const_int(a) + get_const_int(b))


def minus(a: ConstantExpression, b: ConstantExpression) -> ConstantExpression:
    return ConstantExpression(TypeSignaturePlain(PlainType.INTEGER), get_const_int(a) - get_const_int(b))


def multiply(a: ConstantExpression, b: ConstantExpression) -> ConstantExpression:
    return ConstantExpression(TypeSignaturePlain(PlainType.INTEGER), get_const_int(a) * get_const_int(b))


def modulo(a: ConstantExpression, b: ConstantExpression) -> ConstantExpression:
    return ConstantExpression(TypeSignaturePlain(PlainType.INTEGER), get_const_int(a) * get_const_int(b))


def less_than(a: ConstantExpression, b: ConstantExpression) -> ConstantExpression:
    return ConstantExpression(TypeSignaturePlain(PlainType.BOOLEAN), get_const_int(a) < get_const_int(b))


def greater_than(a: ConstantExpression, b: ConstantExpression) -> ConstantExpression:
    return ConstantExpression(TypeSignaturePlain(PlainType.BOOLEAN), get_const_int(a) > get_const_int(b))


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


def assert_types_match(target_type: TypeSignature, expression: ConstantExpression) -> None:
    assert isinstance(target_type, TypeSignaturePlain)
    assert isinstance(expression.type_sig, TypeSignaturePlain)
    if expression.type_sig != target_type:
        raise_type_error(target_type.plain_type, expression.type_sig.plain_type)


def evaluate(ast: Dict[str, Definition],
             custom_struct_types: Dict[str, Struct],
             scope: List[str],
             target_type: TypeSignature,
             expression: Expression) -> ConstantExpression:
    if isinstance(expression, ConstantExpression):
        if target_type != TypeSignaturePlain(PlainType.NONE):
            assert_types_match(target_type, expression)
        return expression
    if isinstance(expression, Call):
        if expression.function_name == "ifElse":
            assert len(expression.args) == 3
            cond = evaluate(ast, custom_struct_types, scope, TypeSignaturePlain(PlainType.BOOLEAN), expression.args[0])
            assert cond.type_sig == TypeSignaturePlain(PlainType.BOOLEAN)
            if cond.value:
                return evaluate(ast, custom_struct_types, scope, target_type, expression.args[1])
            else:
                return evaluate(ast, custom_struct_types, scope, target_type, expression.args[2])
        definition = ast.get(expression.function_name, None)
        evaluated_args = list(
            map(partial(evaluate, ast, custom_struct_types, scope, TypeSignaturePlain(PlainType.NONE)),
                expression.args))
        if definition is not None:
            for param, arg in zip(definition.params, evaluated_args):
                assert_types_match(param.type_sig, arg)
            extension = dict(
                map(lambda p, a: (p.name, Definition(p.type_sig, [], a)), definition.params, evaluated_args))
            extended_ast = ast | extension
            return evaluate(extended_ast, custom_struct_types, [expression.function_name], definition.def_type,
                            definition.expression)
        assert expression.function_name in builtin_functions
        return builtin_functions[expression.function_name](*evaluated_args)  # type: ignore
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
        return evaluate(ast, custom_struct_types, containing_scope + [expression.name], var_definition.def_type,
                        var_definition.expression)
    raise RuntimeError("Wat")


def interpret(ast: Dict[str, Definition], custom_struct_types: Dict[str, Struct]) -> None:
    main = ast["main"]
    assert len(main.params) == 0
    assert isinstance(main.expression, Call)
    evaluate(ast, custom_struct_types, ["main"], TypeSignaturePlain(PlainType.NONE), main.expression)

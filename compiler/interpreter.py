from functools import partial
from typing import Dict, List, Optional, Any

from .parser import Definition, Expression, Variable, \
    ConstantPlainExpression, Call, TypeSignaturePlain, TypeSignature, PlainType, get_const_str, get_const_int, Struct, \
    ConstantStructExpression, TypeSignatureCustom, ConstantExpression


def print_line(text: ConstantPlainExpression) -> None:
    assert text.type_sig == TypeSignaturePlain(PlainType.STRING)
    print(text.value)


def concat(*args: ConstantPlainExpression) -> ConstantPlainExpression:
    def get_value(exp: ConstantPlainExpression) -> str:
        return get_const_str(exp)

    arg_values = list(map(get_value, args))
    return ConstantPlainExpression(TypeSignaturePlain(PlainType.STRING), "".join(arg_values))


def int_to_str(number: ConstantPlainExpression) -> ConstantPlainExpression:
    return ConstantPlainExpression(TypeSignaturePlain(PlainType.STRING), str(get_const_int(number)))


def plus(a: ConstantPlainExpression, b: ConstantPlainExpression) -> ConstantPlainExpression:
    return ConstantPlainExpression(TypeSignaturePlain(PlainType.INTEGER), get_const_int(a) + get_const_int(b))


def minus(a: ConstantPlainExpression, b: ConstantPlainExpression) -> ConstantPlainExpression:
    return ConstantPlainExpression(TypeSignaturePlain(PlainType.INTEGER), get_const_int(a) - get_const_int(b))


def multiply(a: ConstantPlainExpression, b: ConstantPlainExpression) -> ConstantPlainExpression:
    return ConstantPlainExpression(TypeSignaturePlain(PlainType.INTEGER), get_const_int(a) * get_const_int(b))


def modulo(a: ConstantPlainExpression, b: ConstantPlainExpression) -> ConstantPlainExpression:
    return ConstantPlainExpression(TypeSignaturePlain(PlainType.INTEGER), get_const_int(a) * get_const_int(b))


def less_than(a: ConstantPlainExpression, b: ConstantPlainExpression) -> ConstantPlainExpression:
    return ConstantPlainExpression(TypeSignaturePlain(PlainType.BOOLEAN), get_const_int(a) < get_const_int(b))


def greater_than(a: ConstantPlainExpression, b: ConstantPlainExpression) -> ConstantPlainExpression:
    return ConstantPlainExpression(TypeSignaturePlain(PlainType.BOOLEAN), get_const_int(a) > get_const_int(b))


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


def assert_types_match(target_type: TypeSignature, expression: ConstantPlainExpression) -> None:
    assert isinstance(target_type, TypeSignaturePlain)
    assert isinstance(expression.type_sig, TypeSignaturePlain)
    if expression.type_sig != target_type:
        raise_type_error(target_type.plain_type, expression.type_sig.plain_type)


def evaluate(ast: Dict[str, Definition],
             custom_struct_types: Dict[str, Struct],
             getters: Dict[str, Any],
             scope: List[str],
             target_type: TypeSignature,
             expression: Expression) -> ConstantExpression:
    if isinstance(expression, ConstantPlainExpression):
        if target_type != TypeSignaturePlain(PlainType.NONE):
            assert_types_match(target_type, expression)
        return expression
    if isinstance(expression, Call):
        if expression.function_name == "ifElse":
            assert len(expression.args) == 3
            cond = evaluate(ast, custom_struct_types, getters, scope, TypeSignaturePlain(PlainType.BOOLEAN),
                            expression.args[0])
            assert cond.type_sig == TypeSignaturePlain(PlainType.BOOLEAN)
            if cond.value:
                return evaluate(ast, custom_struct_types, getters, scope, target_type, expression.args[1])
            else:
                return evaluate(ast, custom_struct_types, getters, scope, target_type, expression.args[2])
        evaluated_args = list(
            map(partial(evaluate, ast, custom_struct_types, getters, scope, TypeSignaturePlain(PlainType.NONE)),
                expression.args))
        definition = ast.get(expression.function_name, None)
        if definition is not None:
            for param, arg in zip(definition.params, evaluated_args):
                assert_types_match(param.type_sig, arg)
            extension = dict(
                map(lambda p, a: (p.name, Definition(p.type_sig, [], a)), definition.params, evaluated_args))
            extended_ast = ast | extension
            return evaluate(extended_ast, custom_struct_types, getters, [expression.function_name], definition.def_type,
                            definition.expression)
        custom_struct = custom_struct_types.get(expression.function_name, None)
        if custom_struct is not None:
            field_names = [f.name for f in custom_struct.fields]
            return ConstantStructExpression(TypeSignatureCustom(expression.function_name),
                                            dict(zip(field_names, evaluated_args)))
        getter = getters.get(expression.function_name, None)
        if getter is not None:
            assert len(evaluated_args) == 1
            return getter(evaluated_args[0].value)
        assert expression.function_name in builtin_functions, f"Wat? {expression.function_name}"
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
        return evaluate(ast, custom_struct_types, getters, containing_scope + [expression.name],
                        var_definition.def_type,
                        var_definition.expression)
    raise RuntimeError("Wat")


def interpret(ast: Dict[str, Definition], custom_struct_types: Dict[str, Struct], getters: Dict[str, Any]) -> None:
    main = ast["main"]
    assert len(main.params) == 0
    assert isinstance(main.expression, Call)
    evaluate(ast, custom_struct_types, getters, ["main"], TypeSignaturePlain(PlainType.NONE), main.expression)

from functools import partial
from typing import Dict, List, Optional, Any

from .parser import Definition, Expression, Variable, \
    ConstantPlainExpression, Call, TypeSignaturePlain, TypeSignature, PlainType, get_const_str, get_const_int, Struct, \
    ConstantStructExpression, TypeSignatureCustom, ConstantExpression, BuiltInFunction, Parameter


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


def equality_check(a: ConstantPlainExpression, b: ConstantPlainExpression) -> ConstantPlainExpression:
    return ConstantPlainExpression(TypeSignaturePlain(PlainType.BOOLEAN), a.value == b.value)


builtin_functions: Dict[str, Definition] = {
    "printLine": Definition(TypeSignatureCustom("todo"),
                            [Parameter(TypeSignaturePlain(PlainType.STRING), "msg")],
                            BuiltInFunction(TypeSignaturePlain(PlainType.NONE), print_line)),
    "concat": Definition(TypeSignatureCustom("todo"),
                         [Parameter(TypeSignaturePlain(PlainType.STRING), "a"),
                          Parameter(TypeSignaturePlain(PlainType.STRING), "b")],
                         BuiltInFunction(TypeSignaturePlain(PlainType.STRING), concat)),
    "intToStr": Definition(TypeSignatureCustom("todo"),
                           [Parameter(TypeSignaturePlain(PlainType.INTEGER), "a")],
                           BuiltInFunction(TypeSignaturePlain(PlainType.STRING), int_to_str)),
    "+": Definition(TypeSignatureCustom("todo"),
                    [Parameter(TypeSignaturePlain(PlainType.INTEGER), "a"),
                     Parameter(TypeSignaturePlain(PlainType.INTEGER), "b")],
                    BuiltInFunction(TypeSignaturePlain(PlainType.INTEGER), plus)),
    "-": Definition(TypeSignatureCustom("todo"),
                    [Parameter(TypeSignaturePlain(PlainType.INTEGER), "a"),
                     Parameter(TypeSignaturePlain(PlainType.INTEGER), "b")],
                    BuiltInFunction(TypeSignaturePlain(PlainType.INTEGER), minus)),
    "*": Definition(TypeSignatureCustom("todo"),
                    [Parameter(TypeSignaturePlain(PlainType.INTEGER), "a"),
                     Parameter(TypeSignaturePlain(PlainType.INTEGER), "b")],
                    BuiltInFunction(TypeSignaturePlain(PlainType.INTEGER), multiply)),
    "%": Definition(TypeSignatureCustom("todo"),
                    [Parameter(TypeSignaturePlain(PlainType.INTEGER), "a"),
                     Parameter(TypeSignaturePlain(PlainType.INTEGER), "b")],
                    BuiltInFunction(TypeSignaturePlain(PlainType.INTEGER), modulo)),
    "<": Definition(TypeSignatureCustom("todo"),
                    [Parameter(TypeSignaturePlain(PlainType.INTEGER), "a"),
                     Parameter(TypeSignaturePlain(PlainType.INTEGER), "b")],
                    BuiltInFunction(TypeSignaturePlain(PlainType.BOOLEAN), less_than)),
    ">": Definition(TypeSignatureCustom("todo"),
                    [Parameter(TypeSignaturePlain(PlainType.INTEGER), "a"),
                     Parameter(TypeSignaturePlain(PlainType.INTEGER), "b")],
                    BuiltInFunction(TypeSignaturePlain(PlainType.BOOLEAN), greater_than)),
    "==": Definition(TypeSignatureCustom("todo"),
                     [Parameter(TypeSignaturePlain(PlainType.INTEGER), "a"),
                      Parameter(TypeSignaturePlain(PlainType.INTEGER), "b")],
                     BuiltInFunction(TypeSignaturePlain(PlainType.BOOLEAN), equality_check)),
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
    if isinstance(target_type, TypeSignaturePlain) and isinstance(expression.type_sig, TypeSignaturePlain):
        assert isinstance(expression.type_sig, TypeSignaturePlain)
        if expression.type_sig != target_type:
            raise_type_error(target_type.plain_type, expression.type_sig.plain_type)
    # todo: check non-plain types too


def evaluate(ast: Dict[str, Definition],
             custom_struct_types: Dict[str, Struct],
             getters: Dict[str, Any],
             unions: Dict[str, List[TypeSignature]],
             scope: List[str],
             target_type: TypeSignature,
             expression: Expression) -> Expression:
    if isinstance(expression, ConstantExpression):
        if target_type != TypeSignaturePlain(PlainType.NONE):
            assert_types_match(target_type, expression)
        return expression
    if isinstance(expression, Call):
        if expression.function_name == "ifElse":
            assert len(expression.args) == 3
            cond = evaluate(ast, custom_struct_types, getters, unions, scope, TypeSignaturePlain(PlainType.BOOLEAN),
                            expression.args[0])
            assert isinstance(cond, ConstantPlainExpression)
            assert cond.type_sig == TypeSignaturePlain(PlainType.BOOLEAN)
            if cond.value:
                return evaluate(ast, custom_struct_types, getters, unions, scope, target_type, expression.args[1])
            else:
                return evaluate(ast, custom_struct_types, getters, unions, scope, target_type, expression.args[2])
        evaluated_args = list(
            map(partial(evaluate, ast, custom_struct_types, getters, unions, scope, TypeSignaturePlain(PlainType.NONE)),
                expression.args))
        definition = ast.get(expression.function_name, None)
        if definition is not None:
            if isinstance(definition.expression, BuiltInFunction):
                return definition.expression.impl(*evaluated_args)
            for param, arg in zip(definition.params, evaluated_args):
                assert_types_match(param.type_sig, arg)
            #def look(ex: Expression):
#                if isinstance()
            extension = dict(  # todo params
                map(lambda p, a: (p.name, Definition(p.type_sig, [], a)), definition.params, evaluated_args))
            extended_ast = ast | extension
            return evaluate(extended_ast, custom_struct_types, getters, unions, [expression.function_name],
                            definition.def_type,
                            definition.expression)
        custom_struct = custom_struct_types.get(expression.function_name, None)
        if custom_struct is not None:
            field_names = [f.name for f in custom_struct.fields]
            return ConstantStructExpression(TypeSignatureCustom(expression.function_name),
                                            dict(zip(field_names, evaluated_args)))
        getter = getters.get(expression.function_name, None)
        if getter is not None:
            assert len(evaluated_args) == 1
            result: ConstantExpression = getter(evaluated_args[0].value)
            return result
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
        if isinstance(expression, BuiltInFunction):
            return expression
        if not var_definition:
            raise RuntimeError(f"No definition found for: {expression.name}")
        if isinstance(var_definition.expression, Call):
            if len(var_definition.params) > 0:
                return var_definition.expression
        return evaluate(ast, custom_struct_types, getters, unions, containing_scope + [expression.name],
                        var_definition.def_type,
                        var_definition.expression)
    raise RuntimeError("Wat")


def interpret(ast: Dict[str, Definition], custom_struct_types: Dict[str, Struct], getters: Dict[str, Any],
              unions: Dict[str, List[TypeSignature]]) -> None:
    main = ast["main"]
    assert len(main.params) == 0
    assert isinstance(main.expression, Call)
    extended_ast = ast | builtin_functions
    evaluate(extended_ast, custom_struct_types, getters, unions, ["main"], TypeSignaturePlain(PlainType.NONE),
             main.expression)

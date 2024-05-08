from functools import partial
from typing import Dict, List, Any

from . import lexer, augmenter
from .parser import Definition, Expression, \
    Call, TypeSignaturePlain, TypeSignature, get_const_str, get_const_int, Struct, \
    parser, PlainExpression


def printline(text: PlainExpression) -> None:
    assert text.type_sig == TypeSignaturePlain("String")
    print(text.value)


def concat(*args: PlainExpression) -> PlainExpression:
    def get_value(exp: PlainExpression) -> str:
        return get_const_str(exp)

    arg_values = list(map(get_value, args))
    return PlainExpression(TypeSignaturePlain("String"), "".join(arg_values))


def inttostr(number: PlainExpression) -> PlainExpression:
    return PlainExpression(TypeSignaturePlain("String"), str(get_const_int(number)))


def plus(a: PlainExpression, b: PlainExpression) -> PlainExpression:
    return PlainExpression(TypeSignaturePlain("Integer"), get_const_int(a) + get_const_int(b))


def minus(a: PlainExpression, b: PlainExpression) -> PlainExpression:
    return PlainExpression(TypeSignaturePlain("Integer"), get_const_int(a) - get_const_int(b))


def multiply(a: PlainExpression, b: PlainExpression) -> PlainExpression:
    return PlainExpression(TypeSignaturePlain("Integer"), get_const_int(a) * get_const_int(b))


def modulo(a: PlainExpression, b: PlainExpression) -> PlainExpression:
    return PlainExpression(TypeSignaturePlain("Integer"), get_const_int(a) * get_const_int(b))


def less(a: PlainExpression, b: PlainExpression) -> PlainExpression:
    return PlainExpression(TypeSignaturePlain("Boolean"), get_const_int(a) < get_const_int(b))


def greater(a: PlainExpression, b: PlainExpression) -> PlainExpression:
    return PlainExpression(TypeSignaturePlain("Boolean"), get_const_int(a) > get_const_int(b))


def equal(a: PlainExpression, b: PlainExpression) -> PlainExpression:
    return PlainExpression(TypeSignaturePlain("Boolean"), a.value == b.value)


def fqn(scope: List[str], name: str) -> str:
    scope_fqn = ".".join(scope)
    return (scope_fqn + "." if len(scope_fqn) != 0 else "") + name


def raise_type_error(expected: str, given: str) -> None:
    raise RuntimeError(f"Incorrect type. {given} given. {expected} wanted.")


def assert_types_match(target_type: TypeSignature, expression: Any) -> None:
    if isinstance(target_type, TypeSignaturePlain) and isinstance(expression, PlainExpression) and isinstance(
            expression.type_sig, TypeSignaturePlain):
        assert isinstance(expression.type_sig, TypeSignaturePlain)
        if expression.type_sig != target_type:
            raise_type_error(target_type.name, expression.type_sig.name)
    # todo: check non-plain types too


def evaluate(ast: Dict[str, Definition],
             custom_struct_types: Dict[str, Struct],
             getters: Dict[str, Any],
             unions: Dict[str, List[TypeSignature]],
             scope: List[str],
             expression: Expression) -> Expression:
    if isinstance(expression, PlainExpression):
        return expression
    if isinstance(expression, Call):
        if expression.function_name == "ifElse":
            assert len(expression.args) == 3
            cond = evaluate(ast, custom_struct_types, getters, unions, scope, expression.args[0])
            assert isinstance(cond, PlainExpression)
            assert cond.type_sig == TypeSignaturePlain("Boolean")
            if cond.value:
                return evaluate(ast, custom_struct_types, getters, unions, scope, expression.args[1])
            else:
                return evaluate(ast, custom_struct_types, getters, unions, scope, expression.args[2])
        evaluated_args = list(map(partial(evaluate, ast, custom_struct_types, getters, unions, scope), expression.args))
        definition = ast.get(expression.function_name, None)
        if definition is not None:
            if len(expression.args) == 0 and len(definition.params) != 0:  # no partial application yet
                return definition.expression
            for param, arg in zip(definition.params, evaluated_args):
                assert_types_match(param.type_sig, arg)
            if isinstance(definition.expression, Call) and definition.expression.function_name.startswith(
                    "__builtin__") and len(definition.expression.args) == 0:
                global_name = definition.expression.function_name.split("__")[-1]
                f = globals()[global_name]
                return f(*evaluated_args)
            extension = dict(  # todo params
                map(lambda p, a: (p.name, Definition(p.type_sig, [], a)), definition.params, evaluated_args))
            extended_ast = ast | extension
            return evaluate(extended_ast, custom_struct_types, getters, unions, [expression.function_name],
                            definition.expression)
        assert False
    raise RuntimeError("Wat")


def load_standard_library_ast() -> Dict[str, Definition]:
    standard_library_source = """printLine:None message:String = __builtin__printline
concat:String a:String b:String = __builtin__concat
intToStr:String a:Integer = __builtin__inttostr
plus:Integer a:Integer b:Integer = __builtin__plus
minus:Integer a:Integer b:Integer = __builtin__minus
multiply:Integer a:Integer b:Integer = __builtin__multiply
modulo:Integer a:Integer b:Integer = __builtin__modulo
less:Integer a:Integer b:Boolean = __builtin__less
greater:Integer a:Integer b:Boolean = __builtin__greater
equal:Integer a:Integer b:Boolean = __builtin__equal"""
    standard_library_ast, _, _, _ = parser(lexer(augmenter(standard_library_source)))
    return standard_library_ast


def interpret(ast: Dict[str, Definition], custom_struct_types: Dict[str, Struct], getters: Dict[str, Any],
              unions: Dict[str, List[TypeSignature]]) -> None:
    main = ast["main"]
    assert len(main.params) == 0
    assert isinstance(main.expression, Call)

    extended_ast = ast | load_standard_library_ast()
    evaluate(extended_ast, custom_struct_types, getters, unions, ["main"], main.expression)

from functools import partial
from typing import Dict, List, Any, Callable

from .augmenting import augment
from .lexing import lex
from .parsing import Expression, \
    Call, TypeSignaturePlain, TypeSignature, get_const_str, get_const_int, Struct, \
    parse, PlainExpression, Variable, Parameter


def printline(text: PlainExpression) -> None:
    assert text.type_sig == TypeSignaturePlain("String")
    print(text.value)


def concat(*args: PlainExpression) -> PlainExpression:
    def get_value(exp: PlainExpression) -> str:
        return get_const_str(exp)

    arg_values = list(map(get_value, args))
    return PlainExpression(TypeSignaturePlain("String"), "".join(arg_values))


def inttostr(number: PlainExpression) -> PlainExpression:
    return PlainExpression(str(get_const_int(number)))


def plus(a: PlainExpression, b: PlainExpression) -> PlainExpression:
    return PlainExpression(get_const_int(a) + get_const_int(b))


def minus(a: PlainExpression, b: PlainExpression) -> PlainExpression:
    return PlainExpression(get_const_int(a) - get_const_int(b))


def multiply(a: PlainExpression, b: PlainExpression) -> PlainExpression:
    return PlainExpression(get_const_int(a) * get_const_int(b))


def modulo(a: PlainExpression, b: PlainExpression) -> PlainExpression:
    return PlainExpression(get_const_int(a) * get_const_int(b))


def less(a: PlainExpression, b: PlainExpression) -> PlainExpression:
    return PlainExpression(get_const_int(a) < get_const_int(b))


def greater(a: PlainExpression, b: PlainExpression) -> PlainExpression:
    return PlainExpression(get_const_int(a) > get_const_int(b))


def equal(a: PlainExpression, b: PlainExpression) -> PlainExpression:
    return PlainExpression(a.value == b.value)


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


def bind(arguments: Dict[str, Expression], call: Call) -> Call:
    def replace_variable(a: Expression) -> Expression:
        if isinstance(a, PlainExpression):
            return a
        if isinstance(a, Call):
            return bind(arguments, Call(list(map(partial(bind, arguments), a.expressions))))
        if isinstance(a, Variable):
            if a.name in arguments:
                return arguments[a.name]
            else:
                return a
        assert False

    return Call(list(map(replace_variable, call.expressions)))


def augment_env(env: Dict[str, Expression],
                parameters: List[Parameter],
                args: List[Expression]) -> Dict[str, Expression]:
    # todo: make sure things in the original env can be overwritten (shadowed)
    parameter_names = list(map(lambda p: p.name, parameters))
    return env | dict(zip(parameter_names, args))


def apply_builtin(function: Variable, args: List[Expression]) -> Expression:
    global_name = function.name.split("__")[-1]
    f: Callable[[Any], Expression] = globals()[global_name]

    return f(*args)


# https://wiki.c2.com/?EvalApply
def apply(environment: Dict[str, Expression], function: Expression, args: List[Expression]) -> Expression:
    if isinstance(function, Variable):
        assert function.name.startswith("__builtin__")
        return apply_builtin(function, args)
    assert isinstance(function, Call)
    augmented_environment = augment_env(environment, function.params, args)
    return evaluate(augmented_environment, function)


# https://github.com/reah/scheme_interpreter/blob/master/scheme.py
def evaluate(environment: Dict[str, Expression], expression: Expression) -> Expression:
    if isinstance(expression, PlainExpression):
        return expression
    if isinstance(expression, Variable):
        if expression.name.startswith("__builtin__"):
            return expression
        #return environment[expression.name]
        ret = environment[expression.name]
        #if not isinstance(ret, Variable):
        #    return ret
        return evaluate(environment, ret)
    assert isinstance(expression, Call)
    first_expression = expression.expressions[0]
    if isinstance(first_expression, Variable) and first_expression.name == "ifElse":
        raise RuntimeError("ifElse not yet implemented")
    evaluated_expressions = list(map(partial(evaluate, environment), expression.expressions))
    function, args = evaluated_expressions[0], evaluated_expressions[1:]
    return apply(environment, function, args)


def load_standard_library_ast() -> Dict[str, Expression]:
    standard_library_source = """printLine:None message:String = __builtin__printline
concat:String a:String b:String = __builtin__concat
intToStr:String a:Integer = __builtin__inttostr
plus:Integer a:Integer b:Integer = __builtin__plus
minus:Integer a:Integer b:Integer = __builtin__minus
multiply:Integer a:Integer b:Integer = __builtin__multiply
modulo:Integer a:Integer b:Integer = __builtin__modulo
less:Boolean a:Integer b:Integer = __builtin__less
greater:Boolean a:Integer b:Integer = __builtin__greater
equal:Boolean a:Integer b:Integer = __builtin__equal"""
    standard_library_ast, _, _ = parse(lex(augment(standard_library_source)))
    return standard_library_ast


def interpret(ast: Dict[str, Expression], custom_struct_types: Dict[str, Struct], getters: Dict[str, Any],
              unions: Dict[str, List[TypeSignature]]) -> None:
    main = ast["main"]
    evaluate(custom_struct_types, unions, load_standard_library_ast(), main)

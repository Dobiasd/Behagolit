from functools import partial
from typing import Dict, List, Any, Sequence

from .builtins import default_environment
from .expressions import PrimitiveProcedure, Procedure, Function
from .parsing import Expression, Application, TypeSignature, Struct, PlainExpression, Variable, Parameter, \
    CompoundProcedure


def fqn(scope: List[str], name: str) -> str:
    scope_fqn = ".".join(scope)
    return (scope_fqn + "." if len(scope_fqn) != 0 else "") + name


def raise_type_error(expected: str, given: str) -> None:
    raise RuntimeError(f"Incorrect type. {given} given. {expected} wanted.")


def extend_env(env: Dict[str, Expression],
               parameters: List[Parameter],
               args: List[Expression]) -> Dict[str, Expression]:
    parameter_names = list(map(lambda p: p.name, parameters))
    return env | dict(zip(parameter_names, args))


def apply_primitive_procedure(procedure: PrimitiveProcedure, arguments: Sequence[Expression]) -> Expression:
    return procedure.impl(*arguments)  # type:ignore


def make_procedure(parameters: List[Parameter], body: Sequence[Expression], env: Dict[str, Expression]) -> Procedure:
    return CompoundProcedure(parameters, env, body)


def eval_sequence(environment: Dict[str, Expression], expressions: Sequence[Expression]) -> Expression:
    if len(expressions) == 1:
        return evaluate(environment, expressions[0])
    else:
        return evaluate(environment, Application(expressions[0], expressions[1:]))


# https://wiki.c2.com/?EvalApply
def apply(procedure: Procedure, arguments: List[Expression]) -> Expression:
    if isinstance(procedure, PrimitiveProcedure):
        return apply_primitive_procedure(procedure, arguments)
    if isinstance(procedure, CompoundProcedure):
        extended_env = extend_env(procedure.env, procedure.parameters, arguments)
        return eval_sequence(extended_env, procedure.body)
    else:
        raise RuntimeError(f"Unknown function type to apply: {procedure}")


def list_of_values(environment: Dict[str, Expression], expressions: Sequence[Expression]) -> List[Expression]:
    return list(map(partial(evaluate, environment), expressions))


def lookup_variable_value(environment: Dict[str, Expression], name: str) -> Expression:
    exp = environment[name]
    while isinstance(exp, Variable):
        if not exp.name in environment:
            break
        exp = environment[exp.name]
    return exp


# https://github.com/reah/scheme_interpreter/blob/master/scheme.py
def evaluate(environment: Dict[str, Expression], expression: Expression) -> Expression:
    # todo: remove
    print(f"{expression=}")
    print(f"{environment=}")
    if isinstance(expression, PlainExpression) or isinstance(expression, PrimitiveProcedure):
        return expression
    if isinstance(expression, Variable):
        # todo: which
        #return lookup_variable_value(environment, expression.name)
        return evaluate(environment, lookup_variable_value(environment, expression.name))
    if isinstance(expression, Function):
        # todo: does this ever happen?
        return make_procedure(expression.parameters, expression.body, environment)
    if isinstance(expression, Application):
        evaluated_operator = evaluate(environment, expression.operator)
        assert isinstance(evaluated_operator, Procedure)
        evaluated_operands = list_of_values(environment, expression.operands)
        return apply(evaluated_operator, evaluated_operands)
    else:
        raise RuntimeError(f"Unknown expression type: {expression}")


def interpret(ast: Dict[str, Expression], custom_struct_types: Dict[str, Struct], getters: Dict[str, Any],
              unions: Dict[str, List[TypeSignature]]) -> None:
    main = ast["main"]
    evaluate(default_environment(), main)

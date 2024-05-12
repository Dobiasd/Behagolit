from functools import partial
from typing import Dict, List, Any

from .built_ins import default_environment
from .expressions import PrimitiveProcedure, Procedure, Function, Expression, Application, PlainExpression, Variable, \
    Parameter, CompoundProcedure
from .parsing import TypeSignature, Struct


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


def apply(procedure: Procedure, arguments: List[Expression]) -> Expression:
    if isinstance(procedure, PrimitiveProcedure):
        return procedure.impl(*list(map(partial(evaluate, procedure.env), arguments)))  # type:ignore
    if isinstance(procedure, CompoundProcedure):
        extended_env = extend_env(procedure.env, procedure.parameters, arguments)
        return evaluate(extended_env, Application(procedure.body.operator, procedure.body.operands))
    else:
        raise RuntimeError(f"Unknown function type to apply: {procedure}")


def evaluate(environment: Dict[str, Expression], expression: Expression) -> Expression:
    if isinstance(expression, PlainExpression) or isinstance(expression, PrimitiveProcedure):
        return expression
    if isinstance(expression, Variable):
        return evaluate(environment, environment[expression.name])
    if isinstance(expression, Function):
        return CompoundProcedure(expression.parameters, environment, expression.body)
    if isinstance(expression, CompoundProcedure):
        return expression
    if isinstance(expression, Application):
        if isinstance(expression.operator, Variable) and expression.operator.name == "ifElse":
            assert len(expression.operands) == 3
            condition = evaluate(environment, expression.operands[0])
            assert isinstance(condition, PlainExpression)
            assert isinstance(condition.value, bool)
            if condition.value:
                return evaluate(environment, expression.operands[1])
            else:
                return evaluate(environment, expression.operands[2])
        evaluated_operator = evaluate(environment, expression.operator)
        assert isinstance(evaluated_operator, Procedure)
        evaluated_operands = list(map(partial(evaluate, environment), expression.operands))
        return apply(evaluated_operator, evaluated_operands)
    else:
        raise RuntimeError(f"Unknown expression type: {expression}")


def interpret(ast: Dict[str, Expression], custom_struct_types: Dict[str, Struct], getters: Dict[str, Any],
              unions: Dict[str, List[TypeSignature]]) -> None:
    main = ast["main"]
    evaluate(default_environment(), main)

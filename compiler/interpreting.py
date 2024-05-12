from functools import partial
from typing import Dict, List

from .built_ins import default_environment
from .expressions import PrimitiveClosure, Closure, Function, Expression, Call, PrimitiveExpression, Variable, \
    Parameter, CompoundClosure


def fqn(scope: List[str], name: str) -> str:
    scope_fqn = ".".join(scope)
    return (scope_fqn + "." if len(scope_fqn) != 0 else "") + name


def raise_type_error(expected: str, given: str) -> None:
    raise RuntimeError(f"Incorrect type. {given} given. {expected} wanted.")


def extend_env(environment: Dict[str, Expression],
               parameters: List[Parameter],
               args: List[Expression]) -> Dict[str, Expression]:
    parameter_names = list(map(lambda p: p.name, parameters))
    return environment | dict(zip(parameter_names, args))


def apply(closure: Closure, arguments: List[Expression]) -> Expression:
    if isinstance(closure, PrimitiveClosure):
        return closure.impl(*list(map(partial(evaluate, closure.environment), arguments)))
    if isinstance(closure, CompoundClosure):
        extended_env = extend_env(closure.environment, closure.parameters, arguments)
        return evaluate(extended_env, closure.body)
    else:
        raise RuntimeError(f"Unknown function type to apply: {closure}")


def evaluate(environment: Dict[str, Expression], expression: Expression) -> Expression:
    if isinstance(expression, PrimitiveExpression) or isinstance(expression, PrimitiveClosure):
        return expression
    if isinstance(expression, Variable):
        return evaluate(environment, environment[expression.name])
    if isinstance(expression, Function):
        return CompoundClosure(expression.parameters, environment, expression.body)
    if isinstance(expression, CompoundClosure):
        return expression
    if isinstance(expression, Call):
        if isinstance(expression.operator, Variable) and expression.operator.name == "ifElse":
            assert len(expression.operands) == 3
            condition = evaluate(environment, expression.operands[0])
            assert isinstance(condition, PrimitiveExpression)
            assert isinstance(condition.value, bool)
            if condition.value:
                return evaluate(environment, expression.operands[1])
            else:
                return evaluate(environment, expression.operands[2])
        evaluated_operator = evaluate(environment, expression.operator)
        assert isinstance(evaluated_operator, Closure)
        evaluated_operands = list(map(partial(evaluate, environment), expression.operands))
        return apply(evaluated_operator, evaluated_operands)
    else:
        raise RuntimeError(f"Unknown expression type: {expression}")


def interpret(ast: Dict[str, Expression]) -> None:
    main = ast["main"]
    evaluate(default_environment(), main)

from functools import partial
from typing import Dict, List

from .built_ins import default_environment
from .expressions import PrimitiveClosure, Expression, Call, PrimitiveExpression, Variable, CompoundClosure, \
    CompoundFunction, PrimitiveFunction, Constant, Definition


def fqn(scope: List[str], name: str) -> str:
    scope_fqn = ".".join(scope)
    return (scope_fqn + "." if len(scope_fqn) != 0 else "") + name


def raise_type_error(expected: str, given: str) -> None:
    raise RuntimeError(f"Incorrect type. {given} given. {expected} wanted.")


def extend_env(environment: Dict[str, Expression],
               parameters: List[str],
               args: List[Expression]) -> Dict[str, Expression]:
    return environment | dict(zip(parameters, args))


def apply(closure: Expression, arguments: List[Expression]) -> Expression:
    if isinstance(closure, PrimitiveClosure):
        return closure.impl(*list(map(partial(evaluate, closure.environment), arguments)))
    if isinstance(closure, CompoundClosure):
        extended_env = extend_env(closure.environment, closure.parameters, arguments)
        return evaluate(extended_env, closure.body)
    else:
        raise RuntimeError(f"Unknown closure type to apply: {closure}")


def evaluate(environment: Dict[str, Expression], exp: Expression) -> Expression:
    if isinstance(exp, PrimitiveExpression):
        return exp
    if isinstance(exp, PrimitiveClosure):
        return PrimitiveClosure(exp.parameters, environment | exp.environment, exp.impl)
    if isinstance(exp, CompoundClosure):
        return CompoundClosure(exp.parameters, environment | exp.environment, exp.body)
    if isinstance(exp, Variable):
        return evaluate(environment, environment[exp.name])
    if isinstance(exp, Constant):
        return evaluate(environment, exp.expression)
    if isinstance(exp, CompoundFunction):
        return CompoundClosure(exp.parameters, environment, exp.body)
    if isinstance(exp, PrimitiveFunction):
        return PrimitiveClosure(exp.parameters, environment, exp.impl)
    if isinstance(exp, Call):
        if isinstance(exp.operator, Variable) and exp.operator.name == "ifElse":
            cond = evaluate(environment, exp.operands[0])
            assert len(exp.operands) == 3 and isinstance(cond, PrimitiveExpression) and isinstance(cond.value, bool)
            return evaluate(environment, exp.operands[1]) if cond.value else evaluate(environment, exp.operands[2])
        evaluated_operator = evaluate(environment, exp.operator)
        evaluated_operands = list(map(partial(evaluate, environment), exp.operands))
        return apply(evaluated_operator, evaluated_operands)
    else:
        raise RuntimeError(f"Unknown expression type to evaluate: {exp}")


def strip_definition_type(d: Definition) -> Expression:
    if isinstance(d, Constant):
        return d.expression
    if isinstance(d, CompoundFunction):
        return CompoundClosure(d.parameters, {}, d.body)
    if isinstance(d, PrimitiveFunction):
        return PrimitiveClosure(d.parameters, {}, d.impl)
    assert False


def definitions_to_expressions(ast: Dict[str, Definition]) -> Dict[str, Expression]:
    return dict(zip(ast, map(strip_definition_type, ast.values())))


def interpret(ast: Dict[str, Definition]) -> None:
    main = ast["main"]
    assert isinstance(main, Constant)

    evaluate(definitions_to_expressions(default_environment()), main.expression)

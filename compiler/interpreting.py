import copy
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


def bind_arguments_to_parameters(parameters: List[Parameter],
                                 args: List[Expression]) -> Dict[str, Expression]:
    parameter_names = list(map(lambda p: p.name, parameters))
    return dict(zip(parameter_names, args))


def extend_env(base_environment: Dict[str, Expression],
               ext_environment: Dict[str, Expression]) -> Dict[str, Expression]:
    return base_environment | ext_environment


def remove_parameters(parameters: List[Parameter], names: List[str]) -> List[Parameter]:
    return list(filter(lambda p: p.name not in names, parameters))


def apply(closure: Closure, arguments: List[Expression]) -> Expression:
    if len(arguments) > len(closure.parameters):
        raise RuntimeError("Too many arguments.")
    if len(arguments) < len(closure.parameters):
        bindings = bind_arguments_to_parameters(closure.parameters, arguments)
        new_closure = copy.deepcopy(closure)
        new_closure.parameters = remove_parameters(new_closure.parameters, list(bindings.keys()))
        return new_closure
    if isinstance(closure, PrimitiveClosure):
        return closure.impl(*list(map(partial(evaluate, closure.environment), arguments)))
    if isinstance(closure, CompoundClosure):
        extended_env = extend_env(closure.environment, bind_arguments_to_parameters(closure.parameters, arguments))
        return evaluate(extended_env, closure.body)
    else:
        raise RuntimeError(f"Unknown closure type to apply: {closure}")


def evaluate(environment: Dict[str, Expression], exp: Expression) -> Expression:
    if isinstance(exp, PrimitiveExpression) or isinstance(exp, Closure):
        return exp
    if isinstance(exp, Variable):
        return evaluate(environment, environment[exp.name])
    if isinstance(exp, Function):
        return CompoundClosure(exp.parameters, environment, exp.body)
    if isinstance(exp, Call):
        if isinstance(exp.operator, Variable) and exp.operator.name == "ifElse":
            cond = evaluate(environment, exp.operands[0])
            assert len(exp.operands) == 3 and isinstance(cond, PrimitiveExpression) and isinstance(cond.value, bool)
            return evaluate(environment, exp.operands[1]) if cond.value else evaluate(environment, exp.operands[2])
        evaluated_operator = evaluate(environment, exp.operator)
        assert isinstance(evaluated_operator, Closure)
        evaluated_operands = list(map(partial(evaluate, environment), exp.operands))
        return apply(evaluated_operator, evaluated_operands)
    else:
        raise RuntimeError(f"Unknown expression type to evaluate: {exp}")


def interpret(ast: Dict[str, Expression]) -> None:
    main = ast["main"]
    evaluate(default_environment(), main)

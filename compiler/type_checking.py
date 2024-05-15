from typing import Dict

from .expressions import Call, Variable, PrimitiveExpression, CompoundFunction, Constant, Definition, PrimitiveFunction
from .type_signatures import TypeSignatureFunction, TypeSignaturePrimitive


def derive_type(exp: PrimitiveExpression) -> TypeSignaturePrimitive:
    if isinstance(exp.value, bool):
        return TypeSignaturePrimitive("Boolean")
    if isinstance(exp.value, int):
        return TypeSignaturePrimitive("Integer")
    if isinstance(exp.value, str):
        return TypeSignaturePrimitive("String")
    assert False


def check_types(ast: Dict[str, Definition]) -> None:
    for item in ast.values():
        if isinstance(item, Constant):
            if isinstance(item.expression, PrimitiveExpression):
                if derive_type(item.expression) != item.type_sig:
                    raise RuntimeError("Invalid constant type")
            if isinstance(item.expression, Call):
                assert isinstance(item.expression.operator, Variable)
                if item.expression.operator.name != "ifElse":
                    op = ast[item.expression.operator.name]
                    assert isinstance(op, (PrimitiveFunction, CompoundFunction))
        if isinstance(item, (PrimitiveFunction, CompoundFunction)):
            if not isinstance(item.type_sig, TypeSignatureFunction):
                raise RuntimeError("Invalid type signature for function")
            if len(item.type_sig.params) != len(item.parameters):
                raise RuntimeError("Inconsistent number of parameters")
            if isinstance(item, CompoundFunction):
                if isinstance(item.body, Call):
                    if isinstance(item.body.operator, Variable):
                        if item.body.operator.name in ast:
                            op = ast[item.body.operator.name]
                            assert isinstance(op, (PrimitiveFunction, CompoundFunction))
                            if len(op.type_sig.params) != len(item.body.operands):
                                raise RuntimeError("Inconsistent number of arguments")
                            for x, y in zip(op.type_sig.params, item.body.operands):
                                if isinstance(y, Variable):
                                    checked = False
                                    for idx, p in enumerate(item.parameters):
                                        if p == y.name:
                                            assert x == item.type_sig.params[idx]
                                            checked = True
                                            break
                                    if not checked:
                                        y2 = ast[y.name]
                                        if isinstance(y2, (PrimitiveFunction, CompoundFunction)):
                                            assert x == y2.type_sig
                                        else:
                                            raise RuntimeError("Check not yet implemented")
                                elif isinstance(y, PrimitiveExpression):
                                    # todo: attach sig to PrimitiveExpression instead or parse them as Constant?
                                    if derive_type(y) != x:
                                        raise RuntimeError("Invalid type")

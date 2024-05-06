from abc import ABC
from dataclasses import dataclass
from enum import StrEnum
from typing import List, Optional, Type, Sequence, Dict, Tuple, Union
from typing import TypeVar, Generic, Any

from .lexer import Token, Name, Assignment, StringConstant, IntegerConstant, Semicolon, ScopeOpen, ScopeClose, \
    BoolConstant, LeftParenthesis, RightParenthesis, Colon, ColonEqual

T = TypeVar('T')


# https://stackoverflow.com/a/66941316/1866775
class MyTypeChecker(Generic[T]):
    def is_right_type(self, x: Any) -> bool:
        return isinstance(x, self.__orig_class__.__args__[0])  # type: ignore


class PlainType(StrEnum):
    INTEGER = "Integer"
    STRING = "String"
    BOOLEAN = "Boolean"
    NONE = "None"


@dataclass
class TypeSignature(ABC):
    pass


@dataclass
class TypeSignatureUnknown(TypeSignature):
    pass


@dataclass
class TypeSignaturePlain(TypeSignature):
    plain_type: PlainType


@dataclass
class TypeSignatureCustom(TypeSignature):
    name: str


@dataclass
class TypeSignatureFunction(TypeSignature):
    params: List[TypeSignature]
    return_type: TypeSignature


@dataclass
class Expression(ABC):
    type_sig: TypeSignature


@dataclass
class Variable(Expression):
    type_sig: TypeSignature
    name: str


@dataclass
class Struct(TypeSignature):
    fields: List[Variable]


@dataclass
class ConstantExpression(Expression):
    type_sig: TypeSignaturePlain
    value: Union[str, int, bool]


def get_const_int(exp: ConstantExpression) -> int:
    assert exp.type_sig == TypeSignaturePlain(PlainType.INTEGER)
    assert isinstance(exp.value, int)
    return exp.value


def get_const_str(exp: ConstantExpression) -> str:
    assert exp.type_sig == TypeSignaturePlain(PlainType.STRING)
    assert isinstance(exp.value, str)
    return exp.value


def get_const_bool(exp: ConstantExpression) -> bool:
    assert exp.type_sig == TypeSignaturePlain(PlainType.BOOLEAN)
    assert isinstance(exp.value, bool)
    return exp.value


@dataclass
class Parameter(Token):
    type_sig: TypeSignature
    name: str


@dataclass
class Call(Expression):
    type_sig: TypeSignature
    function_name: str
    args: Sequence[Expression]


@dataclass
class Definition:
    def_type: TypeSignature
    params: List[Parameter]
    expression: Expression


def parse_type_signature(type_sig_tokens: List[Token]) -> TypeSignature:
    assert len(type_sig_tokens) == 1
    first = type_sig_tokens[0]
    assert isinstance(first, Name)
    if first.value in PlainType._value2member_map_:
        return TypeSignaturePlain(PlainType[first.value.upper()])
    else:
        return TypeSignatureCustom(first.value)


def parser(tokens: List[Token]) -> Tuple[Dict[str, Definition], Dict[str, Struct]]:
    definitions: Dict[str, Definition] = {}
    custom_struct_types: Dict[str, Struct] = {}

    def done() -> bool:
        return len(tokens) == 0

    def current() -> Optional[Token]:
        if len(tokens) == 0:
            return None
        return tokens[0]

    def current_not_None() -> Token:
        if len(tokens) == 0:
            raise RuntimeError("No token left.")
        return tokens[0]

    def current_and_progress(cls: Type[T]) -> T:
        current_token = current()
        assert MyTypeChecker[cls]().is_right_type(  # type: ignore
            current_token), f"Expecting {cls.__name__}, but got {type(current_token).__name__} instead."
        progress()
        return current_token  # type: ignore

    def progress() -> Token:
        return tokens.pop(0)

    def add_definition(def_scope: List[str], name: str, definition: Definition) -> None:
        definitions[".".join(def_scope + [name])] = definition

    def add_custom_struct_type(def_scope: List[str], name: str, custom_type: Struct) -> None:
        custom_struct_types[".".join(def_scope + [name])] = custom_type


    def parse_expression(calls: bool = True) -> Expression:
        curr = current()
        if isinstance(curr, LeftParenthesis):
            current_and_progress(LeftParenthesis)
            res = parse_expression()
            current_and_progress(RightParenthesis)
            return res
        if isinstance(curr, StringConstant):
            return ConstantExpression(TypeSignaturePlain(PlainType.STRING), current_and_progress(StringConstant).value)
        if isinstance(curr, BoolConstant):
            return ConstantExpression(TypeSignaturePlain(PlainType.BOOLEAN), current_and_progress(BoolConstant).value)
        if isinstance(curr, IntegerConstant):
            return ConstantExpression(TypeSignaturePlain(PlainType.INTEGER),
                                      current_and_progress(IntegerConstant).value)
        if isinstance(curr, Name):
            if calls:
                func = current_and_progress(Name)
                args: List[Expression] = []
                while not isinstance(current(), (Semicolon, RightParenthesis)):
                    args.append(parse_expression(False))
                return Call(TypeSignatureUnknown(), func.value, args)
            else:
                return Variable(TypeSignatureUnknown(), current_and_progress(Name).value)
        raise RuntimeError(f"Wat: {curr}")

    def parse_type() -> TypeSignature:
        if isinstance(current(), LeftParenthesis):
            type_sig_tokens = []
            open_parenthesis = 1
            while open_parenthesis > 0:
                type_sig_tokens.append(current_not_None())
                progress()
                if isinstance(current(), LeftParenthesis):
                    open_parenthesis += 1
                if isinstance(current(), RightParenthesis):
                    open_parenthesis -= 1
            progress()
        else:
            type_sig_tokens = [current_and_progress(Name)]
        def_type = parse_type_signature(type_sig_tokens)
        return def_type

    def parse_typed_name() -> Tuple[str, TypeSignature]:
        def_name = current_and_progress(Name)
        current_and_progress(Colon)
        def_type = parse_type()
        return def_name.value, def_type

    last_defined_name: Optional[str] = None
    scope: List[str] = []

    while not done():
        if isinstance(current(), ScopeOpen):
            assert last_defined_name is not None
            scope.append(last_defined_name)
            progress()
            continue

        if isinstance(current(), ScopeClose):
            assert last_defined_name is not None
            scope.pop(-1)
            if len(scope) == 0:
                last_defined_name = None
            progress()
            continue

        if isinstance(current(), Semicolon):
            progress()
            continue

        defined_name = current_and_progress(Name).value
        if current() == Colon():
            current_and_progress(Colon)
            defined_type = parse_type()

            assert defined_name not in definitions
            last_defined_name = defined_name

            params: List[Parameter] = []
            while not isinstance(current(), Assignment):
                param_name, param_type = parse_typed_name()
                params.append(Parameter(param_type, param_name))

            current_and_progress(Assignment)

            expression = parse_expression()

            add_definition(scope, defined_name, Definition(defined_type, params, expression))
            progress()
        elif current() == ColonEqual():
            progress()
            kind = current_and_progress(Name)
            assert kind.value == "struct"
            fields: List[Variable] = []
            while not isinstance(current(), Semicolon):
                field_name, field_type = parse_typed_name()
                fields.append(Variable(field_type, field_name))
            add_custom_struct_type(scope, defined_name, Struct(fields))
            print(fields)
        else:
            raise RuntimeError(f"Wat? {current()}")

    return definitions, custom_struct_types

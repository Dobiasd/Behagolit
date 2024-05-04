from abc import ABC
from dataclasses import dataclass
from typing import List


@dataclass
class Token(ABC):
    pass


@dataclass
class Name(Token):
    value: str


@dataclass
class LeftParenthesis(Token):
    pass


class RightParenthesis(Token):
    pass


@dataclass
class BoolConstant(Token):
    value: bool


@dataclass
class StringConstant(Token):
    value: str


@dataclass
class IntegerConstant(Token):
    value: int


@dataclass
class Assignment(Token):
    pass


@dataclass
class EqualityCheck(Token):
    pass


@dataclass
class ScopeOpen(Token):
    pass


@dataclass
class ScopeClose(Token):
    pass


@dataclass
class Semicolon(Token):
    pass

@dataclass
class Colon(Token):
    pass


def lexer(augmented_source_orig: str) -> List[Token]:
    augmented_source: List[str] = [*augmented_source_orig]
    tokens: List[Token] = []

    def done() -> bool:
        return len(augmented_source) == 0

    def current() -> str:
        return augmented_source[0]

    def progress() -> str:
        return augmented_source.pop(0)

    while not done():
        if current() == " ":
            progress()
            continue
        if current() == "(":
            tokens.append(LeftParenthesis())
            progress()
            continue
        if current() == ":":
            tokens.append(Colon())
            progress()
            continue
        if current() == ")":
            tokens.append(RightParenthesis())
            progress()
            continue
        if current() == ";":
            tokens.append(Semicolon())
            progress()
            continue
        if current() == "{":
            tokens.append(ScopeOpen())
            progress()
            continue
        if current() == "}":
            tokens.append(ScopeClose())
            progress()
            continue
        if current() in ["+", "-", "*", "/", "%", "<", ">"]:
            tokens.append(Name(current()))
            progress()
            continue
        if current().isalpha():
            acc = ""
            while not done() and (current().isalnum()):
                acc = acc + current()
                progress()
            if acc in ["True", "False"]:
                tokens.append(BoolConstant(True if acc == "True" else False))
            else:
                tokens.append(Name(acc))
            continue
        if current().isnumeric():
            acc = ""
            while not done() and current().isnumeric():
                acc = acc + current()
                progress()
            tokens.append(IntegerConstant(int(acc)))
            continue
        if current() == "\"":
            progress()
            acc = ""
            while not done() and current() != "\"":
                acc = acc + current()
                progress()
            acc = acc.encode().decode('unicode_escape')
            tokens.append(StringConstant(acc))
            assert current() == "\""
            progress()
            continue
        if current() == "=":
            acc = ""
            while current() == "=":
                acc = acc + current()
                progress()
            if acc == "=":
                tokens.append(Assignment())
            elif acc == "==":
                tokens.append(EqualityCheck())
            else:
                raise RuntimeError(f"Wat? {acc}")
            continue
        raise RuntimeError(f"Unexpected character: {current()}")

    return tokens

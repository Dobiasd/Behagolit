from abc import ABC
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Token(ABC):
    pass


@dataclass(frozen=True)
class Name(Token):
    value: str


@dataclass(frozen=True)
class LeftParenthesis(Token):
    pass


@dataclass(frozen=True)
class Comma(Token):
    pass


class RightParenthesis(Token):
    pass


@dataclass(frozen=True)
class BoolConstant(Token):
    value: bool


@dataclass(frozen=True)
class NoneConstant(Token):
    pass


@dataclass(frozen=True)
class StringConstant(Token):
    value: str


@dataclass(frozen=True)
class IntegerConstant(Token):
    value: int


@dataclass(frozen=True)
class Assignment(Token):
    pass


@dataclass(frozen=True)
class ScopeOpen(Token):
    pass


@dataclass(frozen=True)
class ScopeClose(Token):
    pass


@dataclass(frozen=True)
class VerticalBar(Token):
    pass


@dataclass(frozen=True)
class Semicolon(Token):
    pass


@dataclass(frozen=True)
class Colon(Token):
    pass


@dataclass(frozen=True)
class Arrow(Token):
    pass


@dataclass(frozen=True)
class ColonEqual(Token):
    pass


def lex(augmented_source_orig: str) -> List[Token]:
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
        if current() == ",":
            tokens.append(Comma())
            progress()
            continue
        if current() == "(":
            tokens.append(LeftParenthesis())
            progress()
            continue
        if current() == ":":
            progress()
            if current() == "=":
                progress()
                tokens.append(ColonEqual())
                continue
            tokens.append(Colon())
            continue
        if current() == "-":
            progress()
            if current() == ">":
                progress()
                tokens.append(Arrow())
                continue
            tokens.append(Name("-"))
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
        if current() == "|":
            tokens.append(VerticalBar())
            progress()
            continue
        if current() in ["+", "*", "/", "%", "<", ">"]:
            tokens.append(Name(current()))
            progress()
            continue
        if current().isalpha() or current() == "_":
            acc = ""
            while not done() and (current().isalnum() or current() == "." or current() == "_"):
                acc = acc + current()
                progress()
            if acc in ["true", "false"]:
                tokens.append(BoolConstant(True if acc == "true" else False))
            elif acc == "none":
                tokens.append(NoneConstant())
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
                tokens.append(Name(acc))
            else:
                raise RuntimeError(f"Wat? {acc}")
            continue
        raise RuntimeError(f"Unexpected character: {current()}")

    return tokens

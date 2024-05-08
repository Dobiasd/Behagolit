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


@dataclass
class Comma(Token):
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


@dataclass
class Arrow(Token):
    pass


@dataclass
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
        if current() in ["+", "*", "/", "%", "<", ">", "|"]:  # todo split , and | into different token types
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

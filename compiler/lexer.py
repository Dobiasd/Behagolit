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
class StringConstant(Token):
    value: str


@dataclass
class IntegerConstant(Token):
    value: int


@dataclass
class Assignment(Token):
    pass


@dataclass
class Semicolon(Token):
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
        if current() == ";":
            tokens.append(Semicolon())
            progress()
            continue
        if current() in ["+", "-", "*", "/"]:
            tokens.append(Name(current()))
            progress()
            continue
        if current().isalpha():
            acc = ""
            while not done() and current().isalpha():
                acc = acc + current()
                progress()
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
            else:
                raise RuntimeError(f"Wat? {acc}")
            continue
        raise RuntimeError(f"Unexpected character: {current()}")

    return tokens

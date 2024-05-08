from compiler.augmenting import augment
from compiler.interpreting import interpret
from compiler.lexing import lex
from compiler.parsing import parse


def main() -> None:
    with open("hello_world.behagolit", "r") as file:
        source = file.read()
    print(source)

    augmented_source = augment(source)
    print(f"{augmented_source=}")

    tokens = lex(augmented_source)
    print(f"{tokens=}")

    ast, custom_struct_types, getters, unions = parse(tokens)
    print(f"{ast=}")
    print(f"{custom_struct_types=}")
    print(f"{getters=}")
    print(f"{unions=}")

    print("Running:")
    interpret(ast, custom_struct_types, getters, unions)


if __name__ == "__main__":
    main()

# todo: lexer: constants (int, float, str), maybe lists
# todo: tokens -> parser -> ast (does also not yet know what a function is)
# todo: figure out types
# todo: ast with function calls etc, actual expressions

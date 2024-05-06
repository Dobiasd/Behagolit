from compiler.augmenter import augmenter
from compiler.interpreter import interpret
from compiler.lexer import lexer
from compiler.parser import parser


def main() -> None:
    with open("hello_world.behagolit", "r") as file:
        source = file.read()
    print(source)

    augmented_source = augmenter(source)
    print(f"{augmented_source=}")

    tokens = lexer(augmented_source)
    print(f"{tokens=}")

    ast, custom_struct_types = parser(tokens)
    print(f"{ast=}")
    print(f"{custom_struct_types=}")

    print("Running:")
    interpret(ast, custom_struct_types)


if __name__ == "__main__":
    main()

# todo: lexer: constants (int, float, str), maybe lists
# todo: tokens -> parser -> ast (does also not yet know what a function is)
# todo: figure out types
# todo: ast with function calls etc, actual expressions

from augmenter import augmenter
from compiler.interpreter import interpret
from lexer import lexer
from parser import parser


def main():
    with open("hello_world.behagolit", "r") as file:
        source = file.read()
    print(source)

    augmented_source = augmenter(source)
    print(augmented_source)

    tokens = lexer(augmented_source)
    print(tokens)

    ast = parser(tokens)
    print(ast)

    print("Running:")
    interpret(ast)


if __name__ == "__main__":
    main()

# todo: lexer: constants (int, float, str), maybe lists
# todo: tokens -> parser -> ast (does also not yet know what a function is)
# todo: figure out types
# todo: ast with function calls etc, actual expressions

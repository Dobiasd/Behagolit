import unittest

from compiler import lexer, augmenter
from compiler.interpreter import evaluate, load_standard_library_ast
from compiler.lexer import Name, Colon, Assignment, Semicolon
from compiler.parser import parse_type, TypeSignaturePlain, TypeSignatureFunction, parse_expression, Call, \
    PlainExpression, Definition, parser


class TestFoo(unittest.TestCase):

    def test_augmenter(self) -> None:
        augmented = augmenter("foo\nbar")
        self.assertEqual(augmented, "foo;bar;")

    def test_lexer(self) -> None:
        tokens = lexer(augmenter("main:None = printLine message"))
        self.assertEqual(tokens, [
            Name(value='main'),
            Colon(),
            Name(value='None'),
            Assignment(),
            Name(value='printLine'),
            Name(value='message'),
            Semicolon(),
        ])

    def test_parse_plain_type(self) -> None:
        self.assertEqual(parse_type(lexer(augmenter("None"))), (TypeSignaturePlain(name='None'), 1))

    def test_parse_function_type(self) -> None:
        self.assertEqual(parse_type(lexer(augmenter("(Integer, Boolean -> String)"))), (
            TypeSignatureFunction(params=[TypeSignaturePlain(name='Integer'),
                                          TypeSignaturePlain(name='Boolean')],
                                  return_type=TypeSignaturePlain(name='String')), 7))

    def test_parse_higher_order_function_type(self) -> None:
        self.assertEqual(parse_type(lexer(augmenter("(String, (String -> Boolean) -> Integer))"))),
                         (TypeSignatureFunction(params=[TypeSignaturePlain(name='String'),
                                                        TypeSignatureFunction(
                                                            params=[TypeSignaturePlain(name='String')],
                                                            return_type=TypeSignaturePlain(name='Boolean'))],
                                                return_type=TypeSignaturePlain(name='Integer')), 11))

    def test_parse_plain_expression(self) -> None:
        self.assertEqual(parse_expression(lexer(augmenter("plus 1 2"))),
                         (Call(function_name='plus',
                               args=[PlainExpression(type_sig=TypeSignaturePlain(name='Integer'), value=1),
                                     PlainExpression(type_sig=TypeSignaturePlain(name='Integer'), value=2)]),
                          3))

    def test_parse_parenthesised_expression(self) -> None:
        self.assertEqual(parse_expression(lexer(augmenter("plus (minus 3 2) (multiply 4 5)"))),
                         (Call(function_name='plus',
                               args=[Call(function_name='minus',
                                          args=[PlainExpression(type_sig=TypeSignaturePlain(name='Integer'),
                                                                value=3),
                                                PlainExpression(type_sig=TypeSignaturePlain(name='Integer'),
                                                                value=2)]),
                                     Call(function_name='multiply',
                                          args=[PlainExpression(type_sig=TypeSignaturePlain(name='Integer'),
                                                                value=4),
                                                PlainExpression(type_sig=TypeSignaturePlain(name='Integer'),
                                                                value=5)])]),
                          11))

    def test_evaluate_simple_expression(self) -> None:
        exp, _ = parse_expression(lexer(augmenter("plus 1 2")))
        self.assertEqual(evaluate(load_standard_library_ast(), {}, {}, {}, [], exp),
                         PlainExpression(TypeSignaturePlain("Integer"), 3))

    def test_load_standard_library(self) -> None:
        load_standard_library_ast()

    def test_evaluate_nested_expression(self) -> None:
        exp, _ = parse_expression(lexer(augmenter("intToStr (plus (plus 1 1) (plus 1 (plus 1 1)))")))
        self.assertEqual(evaluate(load_standard_library_ast(), {}, {}, {}, [], exp),
                         PlainExpression(TypeSignaturePlain("String"), "5"))

    def test_parse_definition(self) -> None:
        ast, _, _, _ = parser(lexer(augmenter("a:Integer = 1")))
        self.assertEqual(
            ast,
            {'a':
                 Definition(def_type=TypeSignaturePlain(name='Integer'), params=[],
                            expression=PlainExpression(type_sig=TypeSignaturePlain(name='Integer'),
                                                       value=1))})

    def test_with_definitions(self) -> None:
        exp, _ = parse_expression(lexer(augmenter("plus a b")))
        code_ast, _, _, _ = parser(lexer(augmenter("a:Integer = 1\nb:Integer=c\nc:Integer=2")))
        ast = load_standard_library_ast() | code_ast
        self.assertEqual(evaluate(ast, {}, {}, {}, [], exp),
                         PlainExpression(TypeSignaturePlain("Integer"), 3))

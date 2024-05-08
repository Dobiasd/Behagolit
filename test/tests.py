import unittest

from compiler import augment
from compiler.interpreting import evaluate, load_standard_library_ast
from compiler.lexing import Name, Colon, Assignment, Semicolon, lex
from compiler.parsing import parse_type, TypeSignaturePlain, TypeSignatureFunction, parse_expression, Call, \
    PlainExpression, Definition, parse


class TestFoo(unittest.TestCase):

    def test_augment(self) -> None:
        augmented = augment("foo\nbar")
        self.assertEqual(augmented, "foo;bar;")

    def test_lex(self) -> None:
        tokens = lex(augment("main:None = printLine message"))
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
        self.assertEqual(parse_type(lex(augment("None"))), (TypeSignaturePlain(name='None'), 1))

    def test_parse_function_type(self) -> None:
        self.assertEqual(parse_type(lex(augment("(Integer, Boolean -> String)"))), (
            TypeSignatureFunction(params=[TypeSignaturePlain(name='Integer'),
                                          TypeSignaturePlain(name='Boolean')],
                                  return_type=TypeSignaturePlain(name='String')), 7))

    def test_parse_higher_order_function_type(self) -> None:
        self.assertEqual(parse_type(lex(augment("(String, (String -> Boolean) -> Integer))"))),
                         (TypeSignatureFunction(params=[TypeSignaturePlain(name='String'),
                                                        TypeSignatureFunction(
                                                            params=[TypeSignaturePlain(name='String')],
                                                            return_type=TypeSignaturePlain(name='Boolean'))],
                                                return_type=TypeSignaturePlain(name='Integer')), 11))

    def test_parse_plain_expression(self) -> None:
        self.assertEqual(parse_expression(lex(augment("plus 1 2"))),
                         (Call(function_name='plus',
                               args=[PlainExpression(type_sig=TypeSignaturePlain(name='Integer'), value=1),
                                     PlainExpression(type_sig=TypeSignaturePlain(name='Integer'), value=2)]),
                          3))

    def test_parse_parenthesised_expression(self) -> None:
        self.assertEqual(parse_expression(lex(augment("plus (minus 3 2) (multiply 4 5)"))),
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
        exp, _ = parse_expression(lex(augment("plus 1 2")))
        self.assertEqual(evaluate(load_standard_library_ast(), {}, {}, [], exp),
                         PlainExpression(TypeSignaturePlain("Integer"), 3))

    def test_load_standard_library(self) -> None:
        load_standard_library_ast()

    def test_evaluate_nested_expression(self) -> None:
        exp, _ = parse_expression(lex(augment("intToStr (plus (plus 1 1) (plus 1 (plus 1 1)))")))
        self.assertEqual(evaluate(load_standard_library_ast(), {}, {}, [], exp),
                         PlainExpression(TypeSignaturePlain("String"), "5"))

    def test_parse_definition(self) -> None:
        ast, _, _ = parse(lex(augment("a:Integer = 1")))
        self.assertEqual(
            ast,
            {'a':
                 Definition(def_type=TypeSignaturePlain(name='Integer'), params=[],
                            expression=PlainExpression(type_sig=TypeSignaturePlain(name='Integer'),
                                                       value=1))})

    def test_with_definitions(self) -> None:
        exp, _ = parse_expression(lex(augment("plus a b")))
        code_ast, _, _ = parse(lex(augment("a:Integer = 1\nb:Integer=c\nc:Integer=2")))
        ast = load_standard_library_ast() | code_ast
        self.assertEqual(evaluate(ast, {}, {}, [], exp),
                         PlainExpression(TypeSignaturePlain("Integer"), 3))

    def test_higher_order_functions(self) -> None:
        source = """
apply:Integer f:(Integer->Integer) x:Integer = f x
square:Integer x:Integer = multiply x x
"""
        exp, _ = parse_expression(lex(augment("apply square 3")))
        code_ast, _, _ = parse(lex(augment(source)))
        ast = load_standard_library_ast() | code_ast
        self.assertEqual(evaluate(ast, {}, {}, [], exp),
                         PlainExpression(TypeSignaturePlain("Integer"), 9))

    def test_struct(self) -> None:
        source = "Foo := struct x:Integer y:Boolean"
        exp, _ = parse_expression(lex(augment("Foo.y (Foo 42 true)")))
        code_ast, structs, _ = parse(lex(augment(source)))
        ast = load_standard_library_ast() | code_ast
        self.assertEqual(evaluate(ast, structs, {}, [], exp),
                         PlainExpression(TypeSignaturePlain("Boolean"), True))

    def test_union(self) -> None:
        source = "Foo := union Boolean Integer\nf:Foo = 42"
        exp, _ = parse_expression(lex(augment("equal f 42")))
        code_ast, structs, _ = parse(lex(augment(source)))
        ast = load_standard_library_ast() | code_ast
        self.assertEqual(evaluate(ast, structs, {}, [], exp),
                         PlainExpression(TypeSignaturePlain("Boolean"), True))

    def test_more_complex_higher_order_functions(self) -> None:
        source = """
fourteen:Integer = sum (map oneTwoThree square)
oneTwoThree:IntList = IntListElem 1 (IntListElem 2 (IntListElem 3 (EmptyList 0)))
IntListElem := struct head:Integer tail:IntList
EmptyList := struct nothing:Integer # todo: support none or empty structs
IntList := union EmptyList | IntListElem
sum:Integer xs:IntList = foldr plus 0 oneTwoThree
map:IntList xs:IntList f:(Integer -> Integer) = ifElse (equal xs (EmptyList 0)) (EmptyList 0) (IntListElem (f (IntListElem.head xs)) (map (IntListElem.tail xs) f))
foldr:Integer f:(Integer, Integer -> Integer) acc:Integer xs:IntList = ifElse (equal xs (EmptyList 0)) acc (f (IntListElem.head xs) (foldr f acc (IntListElem.tail xs)))
square:Integer x:Integer = multiply x x
"""
        exp, _ = parse_expression(lex(augment("intToStr fourteen")))
        code_ast, structs, _ = parse(lex(augment(source)))
        ast = load_standard_library_ast() | code_ast
        self.assertEqual(evaluate(ast, structs, {}, [], exp),
                         PlainExpression(TypeSignaturePlain("String"), "14"))

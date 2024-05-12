import unittest

from compiler import augment
from compiler.builtins import default_environment
from compiler.interpreting import evaluate
from compiler.lexing import Name, Colon, Assignment, Semicolon, lex
from compiler.parsing import parse_type, TypeSignaturePlain, TypeSignatureFunction, parse_expression, Application, \
    PlainExpression, parse, Variable


class TestBehagolit(unittest.TestCase):

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
                         (Application(
                             Variable("plus"), [
                                 PlainExpression(1),
                                 PlainExpression(2)]),
                          3))

    def test_parse_parenthesised_expression(self) -> None:
        self.assertEqual(parse_expression(lex(augment("plus (minus 3 2) (multiply 4 5)"))),
                         (Application(
                             Variable("plus"), [
                                 Application(Variable("minus"), [PlainExpression(3), PlainExpression(2)]),
                                 Application(Variable("multiply"), [PlainExpression(4), PlainExpression(5)])]),
                          11))

    def test_evaluate_simple_expression(self) -> None:
        exp, _ = parse_expression(lex(augment("plus 1 2")))
        self.assertEqual(evaluate(default_environment(), exp), PlainExpression(3))

    def test_evaluate_nested_expression(self) -> None:
        exp, _ = parse_expression(lex(augment("intToStr (plus (plus 1 1) (plus 1 (plus 1 1)))")))
        self.assertEqual(evaluate(default_environment(), exp),
                         PlainExpression("5"))

    def test_parse_definition(self) -> None:
        ast, _, _ = parse(lex(augment("a:Integer = 1")))
        self.assertEqual(
            ast,
            {'a': PlainExpression(1)})

    def test_with_definitions(self) -> None:
        exp, _ = parse_expression(lex(augment("plus a b")))
        code_ast, _, _ = parse(lex(augment("a:Integer = 1\nb:Integer=c\nc:Integer=2")))
        ast = default_environment() | code_ast
        self.assertEqual(evaluate(ast, exp), PlainExpression(3))

    def test_variable(self) -> None:
        source = "fourteen:Integer = plus 10 4"
        exp, _ = parse_expression(lex(augment("intToStr fourteen")))
        code_ast, _, _ = parse(lex(augment(source)))
        ast = default_environment() | code_ast
        self.assertEqual(evaluate(ast, exp), PlainExpression("14"))

    def test_higher_order_functions(self) -> None:
        source = """
apply:Integer f:(Integer->Integer) v:Integer = f v
square:Integer x:Integer = multiply x x
"""
        exp, _ = parse_expression(lex(augment("apply square 3")))
        code_ast, _, _ = parse(lex(augment(source)))
        ast = default_environment() | code_ast
        self.assertEqual(evaluate(ast, exp), PlainExpression(9))

    def test_struct(self) -> None:
        source = "Foo := struct x:Integer y:Boolean"
        exp, _ = parse_expression(lex(augment("Foo.y (Foo 42 true)")))
        code_ast, structs, _ = parse(lex(augment(source)))
        ast = default_environment() | code_ast
        self.assertEqual(evaluate(ast, exp), PlainExpression(True))

    @unittest.skip("type checks yet implemented")
    def test_union(self) -> None:
        source = "Foo := union Boolean Integer\nf:Foo = 42"
        exp, _ = parse_expression(lex(augment("equal f 42")))
        code_ast, structs, _ = parse(lex(augment(source)))
        ast = default_environment() | code_ast
        self.assertEqual(evaluate(ast, exp), PlainExpression(True))

    def test_more_complex_higher_order_functions(self) -> None:
        source = """
main:None = printLine message
message:String = concat "Hello, world!" (concat "\\n" answerSentence)
answerSentence:String = tellFact "answer" theAnswer
theAnswer:String = ifElse true fourtyTwoRepr "No."
tellFact:String name:String value:String = concat "The " (concat name (concat " is: " value))
fourtyTwoRepr:String = intToStr fourtyTwo
fourtyTwo:Integer = plus fourteen (plus 15 thirteen)
thirteen:Integer = divide (plus (modulo 29 19) (plus (fib 8) sixty)) 7
fib:Integer n:Integer = ifElse (less n 2) n (plus (fib (minus n 1)) (fib (minus n 2)))
sixty:Integer = plus (multiply 10 (TwoDigitNumber.tens weirdSixty)) (TwoDigitNumber.ones weirdSixty)
TwoDigitNumber := struct tens:Integer ones:Integer
weirdSixty:TwoDigitNumber = TwoDigitNumber 6 0
fourteen:Integer = sum (map oneTwoThree square)
oneTwoThree:IntList = IntListElem 1 (IntListElem 2 (IntListElem 3 (EmptyList 0)))
IntListElem := struct head:Integer tail:IntList
EmptyList := struct nothing:Integer # todo: support none or empty structs
IntList := union EmptyList | IntListElem
sum:Integer xs:IntList = foldr plus 0 xs
map:IntList xs:IntList f:(Integer -> Integer) = ifElse (equal xs (EmptyList 0)) (EmptyList 0) (IntListElem (f (IntListElem.head xs)) (map (IntListElem.tail xs) f))
foldr:Integer f:(Integer, Integer -> Integer) acc:Integer xs:IntList = ifElse (equal xs (EmptyList 0)) acc (f (IntListElem.head xs) (foldr f acc (IntListElem.tail xs)))
square:Integer x:Integer = multiply x x"""
        exp, _ = parse_expression(lex(augment("message")))
        code_ast, structs, _ = parse(lex(augment(source)))
        ast = default_environment() | code_ast
        self.assertEqual(evaluate(ast, exp), PlainExpression("Hello, world!\nThe answer is: 42"))

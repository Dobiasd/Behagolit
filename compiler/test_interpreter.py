import unittest

from .augmenting import augment
from .built_ins import default_environment
from .expressions import Call, PrimitiveExpression, Variable
from .interpreting import evaluate
from .lexing import Name, Colon, Assignment, Semicolon, lex
from .parsing import parse_type, TypeSignaturePrimitive, TypeSignatureFunction, parse_expression, parse


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
        self.assertEqual(parse_type(lex(augment("None"))), (TypeSignaturePrimitive(name='None'), 1))

    def test_parse_function_type(self) -> None:
        self.assertEqual(parse_type(lex(augment("(Integer, Boolean -> String)"))), (
            TypeSignatureFunction(params=[TypeSignaturePrimitive(name='Integer'),
                                          TypeSignaturePrimitive(name='Boolean')],
                                  return_type=TypeSignaturePrimitive(name='String')), 7))

    def test_parse_higher_order_function_type(self) -> None:
        self.assertEqual(parse_type(lex(augment("(String, (String -> Boolean) -> Integer))"))),
                         (TypeSignatureFunction(params=[TypeSignaturePrimitive(name='String'),
                                                        TypeSignatureFunction(
                                                            params=[TypeSignaturePrimitive(name='String')],
                                                            return_type=TypeSignaturePrimitive(name='Boolean'))],
                                                return_type=TypeSignaturePrimitive(name='Integer')), 11))

    def test_parse_plain_expression(self) -> None:
        self.assertEqual(parse_expression(lex(augment("plus 1 2"))),
                         (Call(
                             Variable("plus"), [
                                 PrimitiveExpression(1),
                                 PrimitiveExpression(2)]),
                          3))

    def test_parse_parenthesised_expression(self) -> None:
        self.assertEqual(parse_expression(lex(augment("plus (minus 3 2) (multiply 4 5)"))),
                         (Call(
                             Variable("plus"), [
                                 Call(Variable("minus"), [PrimitiveExpression(3), PrimitiveExpression(2)]),
                                 Call(Variable("multiply"), [PrimitiveExpression(4), PrimitiveExpression(5)])]),
                          11))

    def test_evaluate_simple_expression(self) -> None:
        exp, _ = parse_expression(lex(augment("plus 1 2")))
        self.assertEqual(evaluate(default_environment(), exp), PrimitiveExpression(3))

    def test_evaluate_nested_expression(self) -> None:
        exp, _ = parse_expression(lex(augment("intToStr (plus (plus 1 1) (plus 1 (plus 1 1)))")))
        self.assertEqual(evaluate(default_environment(), exp),
                         PrimitiveExpression("5"))

    def test_parse_definition(self) -> None:
        ast, _, _ = parse(lex(augment("a:Integer = 1")))
        self.assertEqual(
            ast,
            {'a': PrimitiveExpression(1)})

    def test_with_definitions(self) -> None:
        exp, _ = parse_expression(lex(augment("plus a (identity b)")))
        code_ast, _, _ = parse(lex(augment("a:Integer = 1\nb:Integer=c\nc:Integer=2\nidentity:Integer x:Integer=x")))
        ast = default_environment() | code_ast
        self.assertEqual(evaluate(ast, exp), PrimitiveExpression(3))

    def test_variable(self) -> None:
        source = "fourteen:Integer = plus 10 4"
        exp, _ = parse_expression(lex(augment("intToStr fourteen")))
        code_ast, _, _ = parse(lex(augment(source)))
        ast = default_environment() | code_ast
        self.assertEqual(evaluate(ast, exp), PrimitiveExpression("14"))

    def test_higher_order_functions(self) -> None:
        source = """
apply:Integer f:(Integer->Integer) v:Integer = f v
square:Integer x:Integer = multiply x x
"""
        exp, _ = parse_expression(lex(augment("apply square 3")))
        code_ast, _, _ = parse(lex(augment(source)))
        ast = default_environment() | code_ast
        self.assertEqual(evaluate(ast, exp), PrimitiveExpression(9))

    def test_partial_application(self) -> None:
        source = "plusForty:Integer = plus 40"
        # Expressions like "(plus 40) 2" are not even parsed correctly
        exp, _ = parse_expression(lex(augment("plusForty 2")))
        code_ast, _, _ = parse(lex(augment(source)))
        ast = default_environment() | code_ast
        self.assertEqual(evaluate(ast, exp), PrimitiveExpression(42))

    def test_struct(self) -> None:
        source = "Foo := struct x:Integer y:Boolean"
        exp, _ = parse_expression(lex(augment("Foo.y (Foo 42 true)")))
        code_ast, structs, _ = parse(lex(augment(source)))
        ast = default_environment() | code_ast
        self.assertEqual(evaluate(ast, exp), PrimitiveExpression(True))

    @unittest.skip("type checks yet implemented")
    def test_union(self) -> None:
        source = "Foo := union Boolean Integer\nf:Foo = 42"
        exp, _ = parse_expression(lex(augment("equal f 42")))
        code_ast, structs, _ = parse(lex(augment(source)))
        ast = default_environment() | code_ast
        self.assertEqual(evaluate(ast, exp), PrimitiveExpression(True))

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
oneTwoThree:IntList = IntListElem 1 (IntListElem 2 (IntListElem 3 (EmptyList none)))
IntListElem := struct head:Integer tail:IntList
EmptyList := struct nothing:None
IntList := union EmptyList | IntListElem
sum:Integer xs:IntList = foldr plus 0 xs
map:IntList xs:IntList f:(Integer -> Integer) = ifElse (equal xs (EmptyList none)) (EmptyList none) (IntListElem (f (IntListElem.head xs)) (map (IntListElem.tail xs) f))
foldr:Integer f:(Integer, Integer -> Integer) acc:Integer xs:IntList = ifElse (equal xs (EmptyList none)) acc (f (IntListElem.head xs) (foldr f acc (IntListElem.tail xs)))
square:Integer x:Integer = multiply x x"""
        exp, _ = parse_expression(lex(augment("message")))
        code_ast, structs, _ = parse(lex(augment(source)))
        ast = default_environment() | code_ast
        self.assertEqual(evaluate(ast, exp), PrimitiveExpression("Hello, world!\nThe answer is: 42"))

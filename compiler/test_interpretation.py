import unittest

from .augmenting import augment
from .built_ins import default_environment
from .expressions import Call, PrimitiveExpression, Variable, Constant
from .interpreting import evaluate, definitions_to_expressions
from .lexing import Name, Colon, Assignment, Semicolon, lex
from .parsing import parse_type, parse_expression, parse
from .type_checking import check_types, TypeCheckException
from .type_signatures import TypeSignaturePrimitive, TypeSignatureFunction, BuiltInPrimitiveType


class TestBehagolit(unittest.TestCase):

    def test_augment(self) -> None:
        augmented = augment("foo\nbar")
        self.assertEqual("foo;bar;", augmented)

    def test_lex(self) -> None:
        tokens = lex(augment("main:None = printLine message"))
        self.assertEqual([
            Name(value='main'),
            Colon(),
            Name(value='None'),
            Assignment(),
            Name(value='printLine'),
            Name(value='message'),
            Semicolon(),
        ], tokens)

    def test_parse_plain_type(self) -> None:
        self.assertEqual((TypeSignaturePrimitive(BuiltInPrimitiveType.NONE), 1), parse_type(lex(augment("None"))))

    def test_parse_function_type(self) -> None:
        self.assertEqual((TypeSignatureFunction(params=[TypeSignaturePrimitive(BuiltInPrimitiveType.INTEGER),
                                                        TypeSignaturePrimitive(BuiltInPrimitiveType.BOOLEAN)],
                                                return_type=TypeSignaturePrimitive(BuiltInPrimitiveType.STRING)), 7),
                         parse_type(lex(augment("(Integer, Boolean -> String)"))))

    def test_parse_higher_order_function_type(self) -> None:
        self.assertEqual((TypeSignatureFunction(params=[TypeSignaturePrimitive(BuiltInPrimitiveType.STRING),
                                                        TypeSignatureFunction(
                                                            params=[
                                                                TypeSignaturePrimitive(BuiltInPrimitiveType.STRING)],
                                                            return_type=TypeSignaturePrimitive(
                                                                BuiltInPrimitiveType.BOOLEAN))],
                                                return_type=TypeSignaturePrimitive(BuiltInPrimitiveType.INTEGER)), 11),
                         parse_type(lex(augment("(String, (String -> Boolean) -> Integer))"))))

    def test_parse_plain_expression(self) -> None:
        self.assertEqual(
            (Call(Variable("plus"), [PrimitiveExpression(1), PrimitiveExpression(2)]), 3),
            parse_expression(lex(augment("plus 1 2"))))

    def test_parse_parenthesised_expression(self) -> None:
        self.assertEqual(
            (Call(
                Variable("plus"), [
                    Call(Variable("minus"), [PrimitiveExpression(3), PrimitiveExpression(2)]),
                    Call(Variable("multiply"), [PrimitiveExpression(4), PrimitiveExpression(5)])]),
             11),
            parse_expression(lex(augment("plus (minus 3 2) (multiply 4 5)"))))

    def test_evaluate_simple_expression(self) -> None:
        exp, _ = parse_expression(lex(augment("plus 1 2")))
        self.assertEqual(PrimitiveExpression(3), evaluate(definitions_to_expressions(default_environment()), exp))

    def test_evaluate_nested_expression(self) -> None:
        exp, _ = parse_expression(lex(augment("intToStr (plus (plus 1 1) (plus 1 (plus 1 1)))")))
        self.assertEqual(PrimitiveExpression("5"), evaluate(definitions_to_expressions(default_environment()), exp))

    def test_parse_definition(self) -> None:
        definitions, _ = parse(lex(augment("a:Integer = 1")))
        self.assertEqual({'a': Constant(expression=PrimitiveExpression(value=1),
                                        type_sig=TypeSignaturePrimitive(BuiltInPrimitiveType.INTEGER),
                                        sub_definitions={})}, definitions)

    def test_with_definitions(self) -> None:
        exp, _ = parse_expression(lex(augment("plus a (identity b)")))
        user_definitions, type_aliases = parse(
            lex(augment("a:Integer = 1\nb:Integer=c\nc:Integer=2\nidentity:Integer x:Integer=x")))
        definitions = default_environment() | user_definitions
        check_types(definitions, type_aliases)
        env = definitions_to_expressions(definitions)
        self.assertEqual(PrimitiveExpression(3), evaluate(env, exp))

    def test_variable(self) -> None:
        source = "fourteen:Integer = plus 10 4"
        exp, _ = parse_expression(lex(augment("intToStr fourteen")))
        user_definitions, type_aliases = parse(lex(augment(source)))
        definitions = default_environment() | user_definitions
        check_types(definitions, type_aliases)
        env = definitions_to_expressions(definitions)
        self.assertEqual(PrimitiveExpression("14"), evaluate(env, exp))

    def test_higher_order_functions(self) -> None:
        source = """
apply:Integer f:(Integer->Integer) v:Integer = f v
square:Integer x:Integer = multiply x x
"""
        exp, _ = parse_expression(lex(augment("apply square 3")))
        user_definitions, type_aliases = parse(lex(augment(source)))
        definitions = default_environment() | user_definitions
        check_types(definitions, type_aliases)
        env = definitions_to_expressions(definitions)
        self.assertEqual(PrimitiveExpression(9), evaluate(env, exp))

    def test_scope(self) -> None:
        source = "y:Integer = plusTwo 40\n    plusTwo:Integer x:Integer = plus x two\n        two:Integer = 2"
        exp, _ = parse_expression(lex(augment("y")))
        user_definitions, type_aliases = parse(lex(augment(source)))
        definitions = default_environment() | user_definitions
        check_types(definitions, type_aliases)
        env = definitions_to_expressions(definitions)
        self.assertEqual(PrimitiveExpression(42), evaluate(env, exp))

    def test_first_expression_with_parentheses(self) -> None:
        exp, _ = parse_expression(lex(augment("(plus) 40 2")))
        env = definitions_to_expressions(default_environment())
        self.assertEqual(PrimitiveExpression(42), evaluate(env, exp))

    def test_expression_starting_with_parentheses_and_returning_function(self) -> None:
        source = """
foo:(Integer -> Integer) x:Integer = helper
    helper:Integer y:Integer = plus x y
        """
        user_definitions, type_aliases = parse(lex(augment(source)))
        exp, _ = parse_expression(lex(augment("(foo 40) 2")))
        definitions = default_environment() | user_definitions
        check_types(definitions, type_aliases)
        env = definitions_to_expressions(definitions)
        self.assertEqual(PrimitiveExpression(42), evaluate(env, exp))

    @unittest.skip("not yet implemented")
    def test_partial_application_transformation(self) -> None:
        source = "a:Integer = (plus 40) 2"
        exp, _ = parse_expression(lex(augment("a")))
        user_definitions, type_aliases = parse(lex(augment(source)))
        definitions = default_environment() | user_definitions
        check_types(definitions, type_aliases)
        env = definitions_to_expressions(definitions)
        self.assertEqual(PrimitiveExpression(42), evaluate(env, exp))

    @unittest.skip("not yet implemented")
    def test_ubiquefix_chain_transformation(self) -> None:
        source = """
input: str
split_lines: str -> List[str]
map: List[a] -> (a -> b) -> List[b]
strToInt: str -> int
square: int -> int
sum: List[int] -> int
result:Integer = input split_lines map strToInt map square sum
"""
        exp, _ = parse_expression(lex(augment("result")))
        user_definitions, type_aliases = parse(lex(augment(source)))
        definitions = default_environment() | user_definitions
        check_types(definitions, type_aliases)
        env = definitions_to_expressions(definitions)
        self.assertEqual(PrimitiveExpression(1234), evaluate(env, exp))

    def test_struct(self) -> None:
        source = "Foo := struct x:Integer y:Boolean"
        exp, _ = parse_expression(lex(augment("Foo.y (Foo 42 true)")))
        user_definitions, type_aliases = parse(lex(augment(source)))
        definitions = default_environment() | user_definitions
        check_types(definitions, type_aliases)
        env = definitions_to_expressions(definitions)
        self.assertEqual(PrimitiveExpression(True), evaluate(env, exp))

    def test_union(self) -> None:
        source = "Foo := union Boolean | Integer\nf:Foo = 42"
        exp, _ = parse_expression(lex(augment("equal f 42")))
        user_definitions, type_aliases = parse(lex(augment(source)))
        definitions = default_environment() | user_definitions
        check_types(definitions, type_aliases)
        env = definitions_to_expressions(definitions)
        self.assertEqual(PrimitiveExpression(True), evaluate(env, exp))

    def test_more_complex_higher_order_functions(self) -> None:
        # todo: currently fails because IntListElem != IntList, i.e., implement union type checks
        source = """
main:None = printLine message
message:String = concat "Hello, world!" (concat "\\n" answerSentence)
    answerSentence:String = tellFact "answer" theAnswer
        tellFact:String name:String value:String = concat "The " (concat name (concat " is: " value))
    theAnswer:String = ifElse true fourtyTwoRepr "No."
        fourtyTwoRepr:String = intToStr fourtyTwo
            fourtyTwo:Integer = plus fourteen (plus 15 thirteen)
                thirteen:Integer = divide (plus (modulo 29 19) (plus (fib 8) sixty)) 7
                    sixty:Integer = plus (multiply 10 (TwoDigitNumber.tens weirdSixty)) (TwoDigitNumber.ones weirdSixty)
                        weirdSixty:TwoDigitNumber = TwoDigitNumber 6 0
                fourteen:Integer = sum (map oneTwoThree square)
                    oneTwoThree:IntList = IntListElem 1 (IntListElem 2 (IntListElem 3 none))
fib:Integer n:Integer = ifElse (less n 2) n (plus (fib (minus n 1)) (fib (minus n 2)))
TwoDigitNumber := struct tens:Integer ones:Integer
IntListElem := struct head:Integer tail:IntList
IntList := union None | IntListElem
sum:Integer xs:IntList = foldr plus 0 xs
foldr:Integer f:(Integer, Integer -> Integer) acc:Integer xs:IntList = ifElse (equal xs none) acc (f (IntListElem.head xs) (foldr f acc (IntListElem.tail xs)))
map:IntList xs:IntList f:(Integer -> Integer) = ifElse (equal xs none) none (IntListElem (f (IntListElem.head xs)) (map (IntListElem.tail xs) f))
square:Integer x:Integer = multiply x x"""
        exp, _ = parse_expression(lex(augment("message")))
        user_definitions, type_aliases = parse(lex(augment(source)))
        definitions = default_environment() | user_definitions
        check_types(definitions, type_aliases)
        env = definitions_to_expressions(definitions)
        self.assertEqual(PrimitiveExpression("Hello, world!\nThe answer is: 42"), evaluate(env, exp))

    def test_type_error_wrong_definition_tfype(self) -> None:
        source = "foo:Integer = \"hi\""
        definitions, type_aliases = parse(lex(augment(source)))
        self.assertRaises(TypeCheckException, check_types, definitions, type_aliases)

    def test_type_error_wrong_literal_argument_type(self) -> None:
        source = "foo:Integer = plus 1 true"
        user_definitions, type_aliases = parse(lex(augment(source)))
        definitions = default_environment() | user_definitions
        self.assertRaises(TypeCheckException, check_types, definitions, type_aliases)

    def test_type_error_wrong_definition_argument_type(self) -> None:
        source = "foo:Integer = add 1 bar\nbar:Boolean = true\nadd:Integer x:Integer y:Integer = plus x y"
        definitions, type_aliases = parse(lex(augment(source)))
        self.assertRaises(TypeCheckException, check_types, definitions, type_aliases)

    def test_type_error_wrong_number_or_arguments(self) -> None:
        source = "foo:Integer = plus 1"
        user_definitions, type_aliases = parse(lex(augment(source)))
        definitions = default_environment() | user_definitions
        self.assertRaises(TypeCheckException, check_types, definitions, type_aliases)

    def test_type_error_compound_function(self) -> None:
        source = "foo:Integer x:String = plus 1 x"
        user_definitions, type_aliases = parse(lex(augment(source)))
        definitions = default_environment() | user_definitions
        self.assertRaises(TypeCheckException, check_types, definitions, type_aliases)

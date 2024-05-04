## Syntax

Everything is an expression. (with no statements, everything is immutable)
Functions are values too.
Expression are formed by concatenating variables and functions into a succession.
A succession is left-associative.
Functions fill their open parameters from left to right.
- First attracting every value that is left of them.
- Then (if still parameter cavities left), attracting values from the right.
Examples:
x: int
f: int -> bool
x f # x is passed to f, resulting in a bool
f x # x is passed to f, resulting in a bool

x: int
y: str
f: int -> str -> bool
x y f # x and y are passed to f, resulting in a bool
x f y # x and y are passed to f, resulting in a bool
f x y # x and y are passed to f, resulting in a bool
y x f # error
y f x # error
f x y # error

x: int
f: str -> float
g: float -> int
x f g # x is passed to f, resulting in a float, which is passed to g, resulting in an int

xs: List[int]
map: List[int] -> (str -> int) -> List[str]
strToInt: str -> int
xs map strToInt # map applies the given function to all arguments in the list
map xs strToInt # map applies the given function to all arguments in the list
xs strToInt map # map applies the given function to all arguments in the list

### sum of squares (text file, lines)
input: str
split_lines: str -> List[str]
map: List[a] -> (a -> b) -> List[b]
strToInt: str -> int
square: int -> int
sum: List[int] -> int
input split_lines map strToInt map square sum # does the job
-> splitted_lines map strToInt map square sum
-> ints map square sum
-> squared_ints sum
-> result
same as:
split_lines input strToInt map square map sum
input split_lines strToIntAll squareAll sum
with
    squareAll = map square
    strToIntAll = map strToInt

a plain value is similar to a function (disregarding side effects) taking 0 parameters

more formal:
f takes 6 params
call: l0 l1 l2 f r0 r1 r2
happens: f l0 l1 l2 r0 r1 r2?

so space is function application f x or x f
f is always filles from left to right

a function attracts arguments to fill its parameter cavities from left to right

this means, one can just shift f

x y z f
x y f z
x f y z
f x y z

is all the same.

So it's like in haskell and in RPN and infix, all at once.

why? Because it allows for more expressive/readable code

infix:
dividedBy: float -> float -> float
x dividedBy y
is better than
dividedBy x y
x y dividedBy

prefix Polish notation (PN)
minimumOf: float -> float -> float
minimumOf x y
is better than
x minimumOf y
x y minimumOf

postfix in pipelines Reverse Polish notation (RPN)
text splitLines sort uniq head show


import io.readLine
import string.strToInt
import string.toString


struct foo =
    a : Uint64
    b : String



add : Uint64 Uint64 -> Uint64
add a b = a b +

String := List<Character>

split : Character String -> List<String>

map : (X -> Y) List<X> -> List<Y>
map f xs = ...

square : Uint64 -> Uint64
square x = x x *

work : String -> String
work text = text splitLines strsToInts squareInts sum toString

    splitLines lines = newLine split
        newLine = "\n"

    strsToInts strs = strToInt strs map

    squareInts ints = square ints map


main : void -> void [IOIn, IOOut]
main = readLine work printLn

# traits/interfaces
# structs
# enforce elm?
# experiment with pipelines and non-unary functions


outdated Philosophy:
- No function composition / partial function application / point-free notation, because the code shall be explicit and parameters shall have names.

# todo

describe grammar is not context free

funktionen auf dem stack auch partial application erlauben und dann nicht nur links sondern auch rechts werte fressen?
function composition (point-free/tacid) erlauben?

forward declaration einführen? top-down enforcen macht mutual recursion unmöglich

Behagolit https://en.m.wikipedia.org/wiki/Stack-oriented_programming

https://mlir.llvm.org/docs/Tutorials/Toy/
https://llvm.org/docs/tutorial/MyFirstLanguageFrontend/index.html
https://www.dabeaz.com/ply/ply.html
https://ruslanspivak.com/lsbasi-part1/

vielleicht doch nicht semantic indentation? lexen/parsen wird dadurch schwerer: https://en.wikipedia.org/wiki/Off-side_rule

language name ideas:

- "schove", "dolang", "behaglang"

- stack based programming vergleichen (joy und cat)
zwei pipe operatoren: append und apply. append extended einfach das gestackte tuple, apply nimmt das rechteste im stack (muss function sein) und applied es auf alle links davon. muss alle fressen, aber darf partial application sein. dann gibts vielleicht noch appendapply als syntactic sugar, aber nur wenn nötig.

oder halt ganz tacit, alles sind nur pipelines, values sieht man eigentlich nich, außer man will, zb. bei mehreren function parameters

- concatenative programming vergleichen: https://github.com/factor/factor/

https://rainingcomputers.blog/dist/the_path_to_implementing_a_programming_language.md

example
elm
input |> split_lines |> map to_set |> fold_left_1 empty_set |> size |> show
|| append
# apply
|# appendapply
input : String
split_lines : (String, Bool) -> [String]
to_set : [a] -> {a}
map : (a -> b, [a]) -> [b]
fold_left : (((a, b) -> a), a, [b]) -> a
empty_set : {a}
size : Int
res = input |# split_lines |# map to_set |# fold_left_1 empty_set |# size |# show
=> res = input |# split_lines || to_set |# map || empty_set |# fold_left_1 |# size |# show
=> res = input || split_lines # || to_set || map # || empty_set || fold_left_1 || size # || show #

|# benimmt sich oft also wie |> in elm:
cond = (2 |# flip mod) >> (0 |# eq)
main = [(1, 2), (42, 23)]
  |# filter (second >> cond)
  |# map plus
  |# println

- typestates supporten: https://www.reddit.com/r/ProgrammingLanguages/comments/18x5g2v/what_do_you_guys_think_about_typestates/

elm architecture als default?

- functions take sets (not lists) of arguments, so order never matters. If more than one argument, it always has to be a named one, i.e., arg=value

- keyword for function should be "func" (if we need one at all), yeah, as in swift, wh o cares

- tailrec annotation that fails compilation of the function is not tail recursive

- enums / sum type classes should have a fromString function, like a factory stuff

- functions can simply be called normally or with param.function(), unary or more-ary

Universal Function Call Syntax, or UFCS. This makes method chaining nicer, for example:
a.f(3).g(true).h("Yendor")
as opposed to
h(g(f(a, 3), true), "Yendor").
Would also play nice with "this" in member functions.

- support modules for encapsulation

- math number types as types, natural, whole, real, rational, irrational

- avoid operator precedence completely by forcing the user to use parentheses

mark functions as pure/state_depending/idempotent_state_changing/non_idempotent_state_changing etc., perhaps automatically -> thread safety becomes type safety

mocking possible?
dependency injection (DI) possible/needed? extensible records as interface

extensible records

error on unused return values

higher kinded types for functors, monads, etc. zum definieren vielleicht types: ":" generics: "::", higher-kinded types: ":::"?

Compile time functions statt generics wie in zig. https://thume.ca/2019/07/14/a-tour-of-metaprogramming-models-for-generics/

Plainly types verbieten? Also Alles named, keine pairs in prelude, etc.

have standard scope functions like in kotlin: let, apply, run, with and also

- "bei compiler-errors den ganzen zweig vom AST als errorhaft markieren. Weitere Errors nur außerhalb davon anzeigen." geht das?

- using-statement wie in c#, zumindest wenns mit GC sein soll.

- logical operators as words, and, or, xor

- Seiteneffekte in Funktionen müssen markiert sein. (Pascal hatte ja schon function vs procedure.) Globales lesen aber anders als globales setzen und beides? Kann compiler das selbst erkennen? Sowas? https://www.stephendiehl.com/posts/exotic03.html

- get inspiration from flix https://flix.dev/principles/

- http://colinm.org/language_checklist.html
- https://www.mcmillen.dev/language_checklist.html
- https://gist.github.com/boppreh/3b88231b7af15af54d292963f3d79b02

constructor should not be some special function but a normal one, like a factory function for that object type

const correctness: Maybe a class definition actually created to classes with the same (immutable) interface and copy-converters between each other? Aber das macht doch das Liskov-Prinzip kaputt! Besser wenns keine classes/interfaces sondern nur traits gibt?

kein ADL: https://en.m.wikipedia.org/wiki/Argument-dependent_name_lookup#Criticism

covariance und contravariance: https://www.stephanboyer.com/post/132/what-are-covariance-and-contravariance

Does it make sense to let function parameter names be part of the function type?

Dolang Keine inheritance aber traits wie rust oder scala (oder type classes in Haskel)

nur switch case, kein if else

Wenn inheritance, dann nur interfaces, kein implementation, because for example fragile base class problem

If classes exist, should other instances of the same class be allowed to access private members?

use nominal typing, but perhaps do allow structural typing for assignments with annotation?

function application nur forward mit operator |>
function composition nur forward mit operator >>
monadic function application nur forward mit operator >>=
monadic function composition nur forward mit operator >=>
fmap nur forward mit auch irgendeinem operator >|

lambdas wi in kotlin, aber mit x, y und z als default parameters
- xs.map {x.mem1}
- zip({x + y.mem1}, xs, ys)

garbadge collection einstellbar (no gc, manual gc-call, ref-count, mark-and-sweep, Mark-Compact, Copying Collector), geht functional with deterministic destruction?

execute stuff at end of scope like RAII or defer in Go? https://blog.golang.org/defer-panic-and-recover

integer types mit fester bit-zahl, aber ein arch-abhängiger (fastest on machine)

integer literals mit separator schreiben können: 1_234_562

floats und double wie in IEEE-754, float32, float64

flix (programming language) als Beispiel anschauen

easily create new types to avoid boolean blindness: https://github.com/quchen/articles/blob/master/algebraic-blindness.md
https://softwareengineering.stackexchange.com/a/147983/104636

block comments nesting erlauben?

allow trailing comma in enumerations such as argument and parameter lists, also leading commas?

compiler targets: php, c (llvm), JS (/webasm)

units-of-measure like in F#: https://fsharpforfunandprofit.com/posts/units-of-measure/

type safe / size save arrays/vectors/matrices. Append etc. wär mit freier function die ownership nimmt. append : vec<T, N> -> T -> vec<T, N+1>, braucht borroring rules wie in Rust, damit der übergebene vektor nicht kopiert werden muss, sondern der speicherbereich wiederverwendet werden kann. Andere dürften den input param der funktion danach dann nicht mehr nutzen.

borroring rules wie in Rust.

interpretable as script

REPL

- support Elvis operator

- ||> operator: Passes the tuple of two arguments on the left side to the function on the right side. Make also for three (|||>).

physic types (meter, sekunde usw.) wie in F# definierbar (opaque typedef), für calculation type safety. Wenn man dann dividiert oder so, ergibt das automatisch einen neuen type. Newton kann man dann auf kg*m/s^2 aliasen usw.
"Int -> Miles
Int -> Hour
x : Miles = 100
y: Hour = 2
x/y => 50 Miles/Hour"

type month = range 1 .. 12
und dann darf man nicht next_month = month + 1 sagen, sondern muss eine plus-funktion benutzen, die garantiert in der range bleibt.

add : Num a => a->a->a
square : Num a => a->a
less : Ord a => a->a->Bool
map : (a->b)->[a]->[b]
filter : (a->Bool)->[a]->[a]
sum : Num a => [a]->a
x : a
y : a
z : a

Haskell:

result = add x y
result : a->a->a a a
result : a->a a
result : a

Infix:

result = x `add` y
result : a a->a->a a
result : a->a a
result : a

Dobilang

result = x y add
result : a a a->a->a
result : a a->a
result : a



haskell:

result = filter (less z) $ map square [x,y]
result = filter (less z) (map square [x,y])
result : (a->Bool)->[a]->[a] (a->a->Bool a) ((a->b)->[a]->[b] a->a [a])
result : (a->Bool)->[a]->[a] a->Bool ([a]->[a] [a])
result : (a->Bool)->[a]->[a] a->Bool [a]
result : [a]->[a] [a]
result : [a]


dobilang:

result = square [x,y] map z less filter
result : a->a [a] (a->b)->[a]->[b] a a->a->Bool (a->Bool)->[a]->[a]
result : [a] [a]->[b] a a->a->Bool (a->Bool)->[a]->[a]
result : [b] a a->a->Bool (a->Bool)->[a]->[a]
result : [b] a->Bool (a->Bool)->[a]->[a]
result : [b] [a]->[a]
result : [a]

--

assignment with destination last:

input
|> transform str_to_int"
|> split ','
|> product
=> result

--


automatic uncurry


haskell:

func : a->(a, [a])
bar : a->[a]->a
result = (uncurry bar) $ func 3


dobilang:

func : a->(a [a])
bar : a->[a]->a
result = func 3 bar
result : a->(a [a]) a a->[a]->a
result : (a [a]) a->[a]->a
result : a [a] a->[a]->a
result : [a] [a]->a
result : a


--


haskell:

($) : (a -> b) -> a -> b
f $ x = f x
infixr 0 $

(|>) : a -> (a -> b) -> b
(|>) x y = y x
infixl 0 |>

(.) : (b -> c) -> (a -> b) -> (a -> c)
(.) f g = f (g x)
infixr 9 .

(>>>) : (a -> b) -> (b -> c) -> (a -> c)
(.) f g = g (f x)
infixr 1 >>>

foo : a -> b
bar : b -> c
baz : a -> c
baz x = bar $ foo x
baz x = x |> foo |> bar
baz = bar . foo
baz = foo >>> bar


dobilang:

baz x = x foo bar
baz a : a a->b b->c
baz a : b b->c
baz a : c

baz = foo bar
baz : a->b b->c
baz : a->c



applications to implement for testing the language

hackerrank stuff
tic tac toe (terminal+keyboard and ui+mouse)
tetris
todo-list ui
text editor
drawing application
database
scheme compiler
webserver
ml library
chat client
spark-pandas-like thing





fancy point-free partial application

func foo(a: T, b: U, c: V) -> Z
    ...

xs : [b]
-> foo 1 _ 3

oder auch

xs : [b]
-> foo a=1 c=3




Wärs hilfreich wenn es von jeder Funktion den Parametersatz als struct type gäbe?







hypothetical example code 2020-04


String: [Char]

concat<T> = (a: [T], b: [T]) -> [T] ->
    [compiler detail]

concat<T> = (xs: [[T]]) -> [T] ->
    reduce_1 concat xs

generate: (f: (() -> T), num: Int) -> [T] =
\ f num -> range num | map (\ _ -> f())

repeat: [T] Int -> [T] =
\ xs num -> range num | map (always x) | concat


x: Int = 0
double: (x: Int -> Int) = x + x
double = func (x: Int) -> Int = x + x
func double (x: Int) -> Int =
    x + x

func double (x: Int) -> Int =
    x + x

effect double_and_log (x: Int) -> Int = {
    print
    x + x
}
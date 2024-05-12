# todo

- partial application
- type checks
- unions with non-plain options
- support uniqefix notation
- support list literals
- adjust Ubiquefix.md to current syntax
- union type check
- scopes, nested definitions 
- switch assert sides
- type aliases?
- automatic toString for every custom type?
- show code example in readme
- traits/interfaces
- enforce elm architecture?
- describe grammar is not context free https://en.wikipedia.org/wiki/Off-side_rule
- stack based programming vergleichen (joy und cat)
- concatenative programming vergleichen: https://github.com/factor/factor/
- tailrec annotation that fails compilation of the function is not tail recursive?
- enums / sum type classes should have a fromString function, like a factory stuff
- explain no member functions, just structs and free functions
- support modules for encapsulation
- math number types as types, natural, whole, real, rational, irrational
- syntax highlighting bauen
- online playground bauen
- avoid operator precedence completely in arithmetric expressions, force the user to use parentheses or so
- mark functions as pure/state_depending/idempotent_state_changing/non_idempotent_state_changing etc., perhaps
  automatically -> thread safety becomes type safety
- support extensible records (structural typing for structs)?
- use nominal typing, but perhaps do allow structural typing for assignments with annotation?
- can return values be unused? if so error when this happens
- higher kinded types for functors, monads, etc. zum definieren vielleicht types: ":" generics: "::", higher-kinded
  types: ":::"?
- Compile time functions statt generics wie in
  zig? https://thume.ca/2019/07/14/a-tour-of-metaprogramming-models-for-generics/
- Plainly types verbieten? Also Alles named, keine pairs in prelude, etc.
- "bei compiler-errors den ganzen zweig vom AST als errorhaft markieren. Weitere Errors nur außerhalb davon anzeigen."
  geht das?
- using-statement wie in c#, zumindest wenns mit GC sein soll. geht das?
- logical operators as words, and, or, xor
- Seiteneffekte in Funktionen müssen markiert sein. (Pascal hatte ja schon function vs procedure.) Globales lesen aber
  anders als globales setzen und beides? Kann compiler das selbst erkennen?
  Sowas? https://www.stephendiehl.com/posts/exotic03.html
- kein ADL: https://en.m.wikipedia.org/wiki/Argument-dependent_name_lookup#Criticism
- Does it make sense to let function parameter names be part of the function type?
- nur switch case, kein if else?
- typestates
  supporten? https://www.reddit.com/r/ProgrammingLanguages/comments/18x5g2v/what_do_you_guys_think_about_typestates/
- monadic function application als library function
- garbadge collection einstellbar (no gc, manual gc-call, ref-count, mark-and-sweep, Mark-Compact, Copying Collector),
  geht functional with deterministic destruction?
- execute stuff at end of scope like RAII or defer in Go? https://blog.golang.org/defer-panic-and-recover
- integer types mit fester bit-zahl, aber ein arch-abhängiger (fastest on machine)
- integer literals mit separator schreiben können: 1_234_562
- floats und double wie in IEEE-754, float32, float64
- easily create new types to avoid boolean
  blindness: https://github.com/quchen/articles/blob/master/algebraic-blindness.md https://softwareengineering.stackexchange.com/a/147983/104636
- allow trailing comma in enumerations such as argument and parameter lists, also leading commas?
- compiler targets: php, c (llvm), JS (/webasm)
- units-of-measure like in F#: https://fsharpforfunandprofit.com/posts/units-of-measure/
- type safe / size save arrays/vectors/matrices. Append etc. wär mit freier function die ownership nimmt. append : vec<
  T, N> -> T -> vec<T, N+1>, braucht borroring rules wie in Rust, damit der übergebene vektor nicht kopiert werden muss,
  sondern der speicherbereich wiederverwendet werden kann. Andere dürften den input param der funktion danach dann nicht
  mehr nutzen.
- REPL
- lib function um tuples and high-arity functions zu übergeben
- physic types (meter, sekunde usw.) wie in F# definierbar (opaque typedef), für calculation type safety. Wenn man dann
  dividiert oder so, ergibt das automatisch einen neuen type. Newton kann man dann auf kg*m/s^2 aliasen usw. x : Miles =
  100; y: Hour = 2; x/y => 50 Miles/Hour"
- type month = range 1 .. 12, und dann darf man nicht next_month = month + 1 sagen, sondern muss eine plus-funktion
  benutzen, die garantiert in der range bleibt.
- applications to implement for testing the language
    - hackerrank stuff
    - tic tac toe (terminal+keyboard and ui+mouse)
    - tetris
    - todo-list ui
    - text editor
    - drawing application
    - database
    - scheme compiler
    - webserver
    - ml library
    - chat client
    - spark-pandas-like thing
- Parametersatz jeder function automatisch als struct type anbieten? Auch invocation damit erlauben
- Look into these
    - get inspiration from flix https://flix.dev/principles/
    - http://colinm.org/language_checklist.html
    - https://www.mcmillen.dev/language_checklist.html
    - https://gist.github.com/boppreh/3b88231b7af15af54d292963f3d79b02
- compiler bauen
    - https://mlir.llvm.org/docs/Tutorials/Toy/
    - https://llvm.org/docs/tutorial/MyFirstLanguageFrontend/index.html
    - https://www.dabeaz.com/ply/ply.html
    - https://rainingcomputers.blog/dist/the_path_to_implementing_a_programming_language.md

### sum of squares (text file, lines)

```
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
```

a plain value is similar to a function (disregarding side effects) taking 0 parameters

```
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
```

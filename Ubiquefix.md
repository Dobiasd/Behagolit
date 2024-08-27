# Idea: "ubiquefix" notation

This document outlines a new function-call syntax, which perhaps could be used in a (not-yet-existing) programming language.

## Common notation syntaxes for (mathematical and other) expressions

### [Prefix notation](https://en.wikipedia.org/wiki/Polish_notation)

```
function arg1 arg2
```

This is not only used in languages like Haskell etc, but also the function call syntax in many mainstream programming
languages is somewhat similar, at least regarding the order of the three tokens:

```
function(arg1, arg2)
```

Examples:

```
+ 1 2
add(1, 2)
```

### [Infix notation](https://en.wikipedia.org/wiki/Infix_notation)

```
arg1 function arg2
```

It's used for binary functions (functions with an arity of 2), and is very well known from mathematical notation.
Example:

```
1 + 2
```

### [Postfix notation](https://en.wikipedia.org/wiki/Reverse_Polish_notation)

```
arg1 arg2 function
```

This is not so common anymore. But in the past, it was popular in calculators, and it is used in stack-oriented
programming languages such as Forth, etc.

Example:

```
1 2 +
```

## Ubiquefix notation

This syntax combines prefix, infix, and postfix into a more general notation.

A function fills its parameter cavities by attracting surrounding values from left to right.

This means, all the following are valid, and they all mean the same thing:

```
function arg1 arg2 
arg1 function arg2
arg1 arg2 function
```

For functions with more than two parameters, it works the same way:

```
function arg1 arg2 arg3
arg1 function arg2 arg3
arg1 arg2 function arg3
arg1 arg2 arg3 function
```

To disambiguate expressions containing more than one function application, expressions in ubiquefix notation are
left-associative. The advantages of this choice will become apparent later.

## Partial function application

A function fuses with its neighbor values until it's either full (i.e., fully applied) or until there are no more values left to
fuse with.

Given a function taking an `A` and `B`, and returning a `C`

```
f : A, B -> C
```

and a value

```
a : A
```

`f a` and `a f` both result in a partially applied function of type

```
B -> C
```

Arguments from the left side of a function are shifted into the parameter cavities from the left.
Arguments from the right side of a function are shifted into the parameter cavities from the right.

Example:

```
f : A, B, C -> D
```

```
a f : B, C -> D
a b f : C -> D
f c : A, B -> D
f b c : A -> D
a f c : B -> D
```

Here we can see that infix notation emerges automatically from first fusing with arguments on the left side (postfix
style) and then fusing with arguments on the right side (prefix style):

```
f : A, B -> C
```

`a f b` is just `f` being first (partially) applied to `a` (`(a f) b`) resulting in an intermediate function of
type `B -> C`, which is then applied to `c`.

### But why?

Because the versatility of ubiquefix notation allows for quite expressive/readable code. Example:

Given a string containing a comma-separated list of integer values (e.g., `42,1,23`)

```
input : String
```

which we want to parse and then calculate the sum of their squares with these helper functions

```
split : String, Character -> List[String]
map : List[A], (A -> B) -> List[B]
stringToInteger : String -> Integer
square : Integer -> Integer
sum : List[Integer] -> Integer
```

we can construct a [pipeline-like expression](https://en.wikipedia.org/wiki/Pipeline_(Unix))

```
input split ',' map stringToInteger map square sum
```

which can be read nicely from left to right. (Remember, ubiquefix notation is left-associative.)

Refactored a bit, it looks like this:

```
input splitOnComma stringsToIntegers squareIntegers
    splitOnComma = split ','
    stringsToIntegers = map stringToInteger
    squareIntegers = map square
```

The definitions of these helper functions use partial function application (with prefix-like notation), which gives
these helpers the following types:

```
splitOnComma : String -> List[String]
stringsToIntegers : List[String] -> List[Integer]
squareIntegers : List[Integer] -> Integer
```

The pipeline itself (`input splitOnComma stringsToIntegers squareIntegers`) uses the postfix-notation style to let the
data flow from left to right through the listed functions.

Using function composition, we could also do

```
input doTheThing
    doTheThing = splitOnComma . stringsToIntegers . squareIntegers
```

### Alleged ambiguities (and their resolution)

If two functions are next to each other, the ambiguity of which is applied to which, is resolved by the type system,
i.e., there are no situations in which both ways ("apply f to g" *and* "apply g to f") would work. Example:

```
f : A -> B
g : (A -> B) -> C
```

```
f g
```

`f` can't be applied to `g`, thus `g` is applied to `f`. (The same is true if we swap the order in the expression, i.e.,
have `g f`.)

In case neither direction is valid, it's just a type error.

### Function composition

Function composition can be implemented as a function provided by the standard library:

```
fwdCompose:(a->c) f:(a->b) g:(b->c) = composition
    composition x = x f g
```

(`a`, `b`, and `c` are type variables here, i.e., `fwdCompose` is a generic function.)

And then be used like this:

```
fAndThenG = f fwdCompose g
```

### Is ubiquefix notation good?

I don't yet know.

Sure, the fact, that the order of functions and their arguments is not the same in each (sub-) expression takes getting
used to. But maybe it's worth it. I'd love to find out!

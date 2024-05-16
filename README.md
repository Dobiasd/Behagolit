![logo](https://github.com/Dobiasd/Behagolit/raw/main/logo/behagolit_small.png)

[![CI](https://github.com/Dobiasd/Behagolit/workflows/ci/badge.svg)](https://github.com/Dobiasd/Behagolit/actions)
[![(License MIT 1.0)](https://img.shields.io/badge/license-MIT%201.0-blue.svg)][license]

[license]: LICENSE


Behagolit
=========
**a toy programming language experiment**

## Philosophy

- Everything is an expression. (with no statements, everything is immutable)
- Functions are values too.
- Values are lazily evaluated, like a functions taking zero arguments.
- [Ubiquefix notation](Ubiquefix.md)
- Expressions can only access other expressions defined after them. This encourages reading and writing code in a
  top-down approach. (Consequently, imports are found at the end of source files.)
- Functions can have side effects. The list of possible side effects is part of the type of the function.

## Etymology

- "Behag" comes from the German [behaglich](https://en.wiktionary.org/wiki/behaglich), meaning comfortable, cosy.
- "olit" is the second-person singular past indicative of the Finish [olla](https://en.wiktionary.org/wiki/olit), which
  means "to be".

So Behagolit could resemble something like "you were comfortable". (And maybe using Behagolit is the reason you now no
longer are comfortable. ^_-)

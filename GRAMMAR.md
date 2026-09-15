# Relational Algebra Grammar

## 1. Context-Free Grammar and EBNF

A context-free grammar is a set of rules that defines the valid structure of strings in a language.

This project uses EBNF (Extended Backus-Naur Form) to describe the syntax of relation definitions, relational algebra expressions, conditions, attributes, and literals.

The grammar generates the relational algebra language specified in Section 4 of the project description. This includes relation definitions and queries using select, project, rename, union, intersect, minus, times, join, comparisons, and boolean conditions.

## 2. Full EBNF

expr ::= union_expr ;

union_expr ::= intersect_expr { ("union" | "minus") intersect_expr } ;

intersect_expr ::= product_expr { "intersect" product_expr } ;

product_expr ::= unary_expr { ("times" unary_expr) | ("join" "[" condition "]" unary_expr) } ;

unary_expr ::= select_expr | project_expr | rename_expr | primary ;

select_expr ::= "select" "[" condition "]" "(" expr ")" ;

project_expr ::= "project" "[" attribute_list "]" "(" expr ")" ;

rename_expr ::= "rename" "[" IDENT "]" "(" expr ")" ;

primary ::= IDENT | "(" expr ")" ;

attribute_list ::= attribute { "," attribute } ;

attribute ::= IDENT [ "." IDENT ] ;

condition ::= or_condition ;

or_condition ::= and_condition { "or" and_condition } ;

and_condition ::= not_condition { "and" not_condition } ;

not_condition ::= "not" not_condition | condition_primary ;

condition_primary ::= comparison | "(" condition ")" ;

comparison ::= operand comparison_op operand ;

comparison_op ::= "=" | "!=" | "<" | "<=" | ">" | ">=" ;

operand ::= attribute | NUMBER | STRING ;

relation_definition ::= IDENT "(" attribute_list ")" "=" "{" tuple_list "}" ;

tuple_list ::= tuple { tuple } ;

tuple ::= value { "," value } ;

value ::= NUMBER | STRING | IDENT ;

IDENT ::= letter { letter | digit | "_" } ;

NUMBER ::= [ "-" ] digit { digit } [ "." digit { digit } ] ;

STRING ::= "'" { string_character | "''" } "'" ;

letter ::= "A".."Z" | "a".."z" ;

digit ::= "0".."9" ;

## 3. Precedence and Associativity

| Precedence | Operators | Associativity |
|---|---|---|
| 1 | select, project, rename | Prefix |
| 2 | times, join | Left |
| 3 | intersect | Left |
| 4 | union, minus | Left |

Precendence List:

1. (Select, Project, Rename) Associativity: Prefix
2. (Times, Join) Associativity: Left
3. (Intersect) Associativity: Left
4. (Union, Minus) Associativity: Left

So:

A union B minus C

means:

(A union B) minus C

Conditions use:

not > and > or

So:

a=1 and b=2 or c=3

means:

(a=1 and b=2) or c=3

Parentheses override precedence.

## 4. Ambiguity Demonstration

Expr ::= Expr "union" Expr | Expr "minus" Expr | "(" Expr ")" | IDENT

This Grammar provided by the project requirement is intentionally naive, it does not account for precendence between union and minus.

(A union B) minus C and A union (B minus C) are two different expressions with different outcomes but are viewed the same by this grammar.

My grammar removes this ambiguity by making union and minus left associative, so the first grouping is used.

Example:

A = {1, 3}
B = {2}
C = {3}

(A union B) minus C = {1, 2}

A union (B minus C) = {1, 2, 3}

## 5. Parsing Strategy

I chose a handwritten recursive descent parser because the language is small and its precedence levels map directly to parser functions. This keeps the parser simple to implement and inspect without using a parser generator.

Left-recursive rules such as:

Expr ::= Expr "union" Expr

would cause a recursive descent parser to call itself before consuming input. I avoid this by rewriting the rule as:

union_expr ::= intersect_expr { ("union" | "minus") intersect_expr } ;

## 6. Keyword Handling

Words such as union, select, and "and" are treated as identifiers by the tokenizer.

The parser determines whether a word is being used as a keyword or as an identifier based on its position in the query.

This allows queries such as:

select[union=3](R)

where union is an attribute name.

## 7. Sources
- Crafting Interpreters — chapters on scanning and parsing
- https://www.freecodecamp.org/news/what-are-bnf-and-ebnf/
- https://www.youtube.com/watch?v=OIKL6wFjFOo&t=6s
- AI assistance was used to discuss grammar structure, ambiguity, precedence, and parser design. Any incorrect or incomplete AI suggestions will be recorded in DESIGN_LOG.md.
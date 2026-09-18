# Design Log

## 2026-09-14

First Day!

Created the initial repository structure and began defining the query language before implementing the parser. I am reviewing context-free grammars, EBNF, ambiguity, precedence, recursive descent, and tokenization before writing code.

Lots of research using the RELAX repo, and taking a look specifically into EBNF and context-free gramars.

## 2026-09-17

Implemented the data-only AST, handwritten recursive-descent query parser,
tree printer, and `--tree` command. The repository handoff listed
`ast_nodes.py` as completed, but an inventory showed that it was absent, so
the parser milestone began by defining the node structure and verifying it
directly with structural tests. Contextual handling of `not` needed special
care so that it can be either a prefix operator or an attribute name; tests
now cover both meanings.

# Relational Algebra Interpreter

A handwritten relational algebra interpreter being built without regular
expressions, parser generators, `eval`, or data-processing libraries.

## Status

The tokenizer, query parser, AST, and tree printer are implemented. Query
execution, relation loading, relational operators, and performance
instrumentation are not implemented yet.

## Print a query tree

```console
python3 ra.py --tree "project[Name](select[Age>30](Employees))"
```

Output:

```text
Project(attrs=[Name])
└── Select(cond=Gt(Attr(Age), Num(30)))
    └── Relation(Employees)
```

The `--tree` command parses only; it does not execute the query.

## Run the tests

```console
python3 -m unittest discover -s tests -v
```

"""Readable tree formatting for relational algebra syntax trees."""

from src.ast_nodes import (
    And,
    Attribute,
    Comparison,
    Intersect,
    Join,
    Minus,
    Not,
    Number,
    Or,
    Project,
    Relation,
    Rename,
    Select,
    String,
    Times,
    Union,
)


COMPARISON_NAMES = {
    "=": "Eq",
    "!=": "Ne",
    "<": "Lt",
    "<=": "Le",
    ">": "Gt",
    ">=": "Ge",
}


def format_tree(node):
    """Return a relational syntax tree drawn with Unicode branch characters."""

    lines = []
    label, children = _relational_parts(node)
    lines.append(label)

    for index, child in enumerate(children):
        _append_subtree(
            child,
            prefix="",
            is_last=index == len(children) - 1,
            lines=lines,
        )

    return "\n".join(lines)


def print_tree(node):
    print(format_tree(node))


def _append_subtree(node, prefix, is_last, lines):
    connector = "└── " if is_last else "├── "
    label, children = _relational_parts(node)
    lines.append(prefix + connector + label)

    child_prefix = prefix + ("    " if is_last else "│   ")

    for index, child in enumerate(children):
        _append_subtree(
            child,
            prefix=child_prefix,
            is_last=index == len(children) - 1,
            lines=lines,
        )


def _relational_parts(node):
    if isinstance(node, Relation):
        return f"Relation({node.name})", ()

    if isinstance(node, Select):
        return f"Select(cond={_format_condition(node.condition)})", (node.operand,)

    if isinstance(node, Project):
        attributes = ", ".join(_format_attribute(attr) for attr in node.attributes)
        return f"Project(attrs=[{attributes}])", (node.operand,)

    if isinstance(node, Rename):
        return f"Rename(name={node.name})", (node.operand,)

    if isinstance(node, Union):
        return "Union", (node.left, node.right)

    if isinstance(node, Intersect):
        return "Intersect", (node.left, node.right)

    if isinstance(node, Minus):
        return "Minus", (node.left, node.right)

    if isinstance(node, Times):
        return "Times", (node.left, node.right)

    if isinstance(node, Join):
        return f"Join(cond={_format_condition(node.condition)})", (
            node.left,
            node.right,
        )

    raise TypeError(f"cannot print unknown relational node {type(node).__name__}")


def _format_condition(node):
    if isinstance(node, And):
        return (
            f"And({_format_condition(node.left)}, "
            f"{_format_condition(node.right)})"
        )

    if isinstance(node, Or):
        return (
            f"Or({_format_condition(node.left)}, "
            f"{_format_condition(node.right)})"
        )

    if isinstance(node, Not):
        return f"Not({_format_condition(node.operand)})"

    if isinstance(node, Comparison):
        name = COMPARISON_NAMES[node.operator]
        return (
            f"{name}({_format_value(node.left)}, "
            f"{_format_value(node.right)})"
        )

    raise TypeError(f"cannot print unknown condition node {type(node).__name__}")


def _format_value(node):
    if isinstance(node, Attribute):
        return f"Attr({_format_attribute(node)})"

    if isinstance(node, Number):
        return f"Num({node.value!r})"

    if isinstance(node, String):
        return f"Str({node.value!r})"

    raise TypeError(f"cannot print unknown value node {type(node).__name__}")


def _format_attribute(attribute):
    if attribute.source is None:
        return attribute.name

    return f"{attribute.source}.{attribute.name}"

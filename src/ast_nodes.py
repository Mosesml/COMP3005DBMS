"""Data-only nodes for relational expressions and conditions."""

from dataclasses import dataclass


class RelationalNode:
    """Base type for relational-expression nodes."""


class ConditionNode:
    """Base type for boolean-condition nodes."""


class ValueNode:
    """Base type for operands used by comparisons."""


@dataclass(frozen=True)
class Relation(RelationalNode):
    name: str


@dataclass(frozen=True)
class Select(RelationalNode):
    condition: ConditionNode
    operand: RelationalNode


@dataclass(frozen=True)
class Project(RelationalNode):
    attributes: tuple["Attribute", ...]
    operand: RelationalNode


@dataclass(frozen=True)
class Rename(RelationalNode):
    name: str
    operand: RelationalNode


@dataclass(frozen=True)
class Union(RelationalNode):
    left: RelationalNode
    right: RelationalNode


@dataclass(frozen=True)
class Intersect(RelationalNode):
    left: RelationalNode
    right: RelationalNode


@dataclass(frozen=True)
class Minus(RelationalNode):
    left: RelationalNode
    right: RelationalNode


@dataclass(frozen=True)
class Times(RelationalNode):
    left: RelationalNode
    right: RelationalNode


@dataclass(frozen=True)
class Join(RelationalNode):
    condition: ConditionNode
    left: RelationalNode
    right: RelationalNode


@dataclass(frozen=True)
class And(ConditionNode):
    left: ConditionNode
    right: ConditionNode


@dataclass(frozen=True)
class Or(ConditionNode):
    left: ConditionNode
    right: ConditionNode


@dataclass(frozen=True)
class Not(ConditionNode):
    operand: ConditionNode


@dataclass(frozen=True)
class Comparison(ConditionNode):
    operator: str
    left: ValueNode
    right: ValueNode


@dataclass(frozen=True)
class Attribute(ValueNode):
    name: str
    source: str | None = None


@dataclass(frozen=True)
class Number(ValueNode):
    value: int | float


@dataclass(frozen=True)
class String(ValueNode):
    value: str

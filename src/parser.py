"""Handwritten recursive-descent parser for relational algebra queries."""

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
from src.errors import ParseError
from src.tokenizer import tokenize


COMPARISON_TOKEN_KINDS = {"EQ", "NE", "LT", "LE", "GT", "GE"}


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        expression = self.parse_expr()

        if not self._check_kind("EOF"):
            token = self._peek()
            raise ParseError(
                f"unexpected token {token.value!r} after complete expression",
                token.position,
            )

        return expression

    def parse_expr(self):
        return self.parse_union()

    def parse_union(self):
        expression = self.parse_intersect()

        while self._check_keyword("union") or self._check_keyword("minus"):
            operator = self._advance().value
            right = self.parse_intersect()

            if operator == "union":
                expression = Union(expression, right)
            else:
                expression = Minus(expression, right)

        return expression

    def parse_intersect(self):
        expression = self.parse_product()

        while self._match_keyword("intersect"):
            right = self.parse_product()
            expression = Intersect(expression, right)

        return expression

    def parse_product(self):
        expression = self.parse_unary()

        while True:
            if self._match_keyword("times"):
                right = self.parse_unary()
                expression = Times(expression, right)
                continue

            if self._match_keyword("join"):
                self._expect("LBRACKET", "expected '[' after 'join'")
                condition = self.parse_condition()
                self._expect("RBRACKET", "expected ']' after join condition")
                right = self.parse_unary()
                expression = Join(condition, expression, right)
                continue

            break

        return expression

    def parse_unary(self):
        # Keywords are contextual. A word starts a unary operator only when it
        # is immediately followed by the operator's opening square bracket.
        if self._check_keyword("select") and self._peek(1).kind == "LBRACKET":
            return self.parse_select()

        if self._check_keyword("project") and self._peek(1).kind == "LBRACKET":
            return self.parse_project()

        if self._check_keyword("rename") and self._peek(1).kind == "LBRACKET":
            return self.parse_rename()

        return self.parse_primary()

    def parse_select(self):
        self._expect_keyword("select")
        self._expect("LBRACKET", "expected '[' after 'select'")
        condition = self.parse_condition()
        self._expect("RBRACKET", "expected ']' after select condition")
        self._expect("LPAREN", "expected '(' before select input")
        operand = self.parse_expr()
        self._expect("RPAREN", "expected ')' to close select input")
        return Select(condition, operand)

    def parse_project(self):
        self._expect_keyword("project")
        self._expect("LBRACKET", "expected '[' after 'project'")

        if self._check_kind("RBRACKET"):
            token = self._peek()
            raise ParseError("project requires at least one attribute", token.position)

        attributes = [self.parse_attribute()]

        while self._match_kind("COMMA"):
            attributes.append(self.parse_attribute())

        self._expect("RBRACKET", "expected ']' after project attribute list")
        self._expect("LPAREN", "expected '(' before project input")
        operand = self.parse_expr()
        self._expect("RPAREN", "expected ')' to close project input")
        return Project(tuple(attributes), operand)

    def parse_rename(self):
        self._expect_keyword("rename")
        self._expect("LBRACKET", "expected '[' after 'rename'")
        name = self._expect("IDENT", "expected a relation name in rename").value
        self._expect("RBRACKET", "expected ']' after rename relation name")
        self._expect("LPAREN", "expected '(' before rename input")
        operand = self.parse_expr()
        self._expect("RPAREN", "expected ')' to close rename input")
        return Rename(name, operand)

    def parse_primary(self):
        if self._match_kind("LPAREN"):
            expression = self.parse_expr()
            self._expect("RPAREN", "expected ')' after parenthesized expression")
            return expression

        if self._check_kind("IDENT"):
            return Relation(self._advance().value)

        token = self._peek()
        raise ParseError("expected a relation name or '(' expression ')'", token.position)

    def parse_condition(self):
        return self.parse_or()

    def parse_or(self):
        condition = self.parse_and()

        while self._match_keyword("or"):
            right = self.parse_and()
            condition = Or(condition, right)

        return condition

    def parse_and(self):
        condition = self.parse_not()

        while self._match_keyword("and"):
            right = self.parse_not()
            condition = And(condition, right)

        return condition

    def parse_not(self):
        if self._is_not_operator():
            self._advance()
            return Not(self.parse_not())

        return self.parse_condition_primary()

    def parse_condition_primary(self):
        if self._match_kind("LPAREN"):
            condition = self.parse_condition()
            self._expect("RPAREN", "expected ')' after parenthesized condition")
            return condition

        return self.parse_comparison()

    def parse_comparison(self):
        left = self.parse_operand()
        operator_token = self._peek()

        if operator_token.kind not in COMPARISON_TOKEN_KINDS:
            raise ParseError("expected a comparison operator", operator_token.position)

        self._advance()
        right = self.parse_operand()
        return Comparison(operator_token.value, left, right)

    def parse_operand(self):
        if self._check_kind("NUMBER"):
            return Number(self._advance().value)

        if self._check_kind("STRING"):
            return String(self._advance().value)

        if self._check_kind("IDENT"):
            return self.parse_attribute()

        token = self._peek()
        raise ParseError("expected an attribute, number, or string", token.position)

    def parse_attribute(self):
        first = self._expect("IDENT", "expected an attribute name")

        if self._match_kind("DOT"):
            second = self._expect(
                "IDENT", "expected an attribute name after '.'"
            )
            return Attribute(name=second.value, source=first.value)

        return Attribute(name=first.value)

    def _is_not_operator(self):
        if not self._check_keyword("not"):
            return False

        # At the start of a comparison, "not" can itself be an attribute.
        # A following comparison operator or dot makes that intent explicit.
        following_kind = self._peek(1).kind
        return following_kind not in COMPARISON_TOKEN_KINDS | {"DOT"}

    def _peek(self, offset=0):
        index = self.current + offset

        if index >= len(self.tokens):
            return self.tokens[-1]

        return self.tokens[index]

    def _advance(self):
        token = self._peek()

        if token.kind != "EOF":
            self.current += 1

        return token

    def _check_kind(self, kind):
        return self._peek().kind == kind

    def _match_kind(self, kind):
        if not self._check_kind(kind):
            return False

        self._advance()
        return True

    def _check_keyword(self, word):
        token = self._peek()
        return token.kind == "IDENT" and token.value == word

    def _match_keyword(self, word):
        if not self._check_keyword(word):
            return False

        self._advance()
        return True

    def _expect(self, kind, message):
        if self._check_kind(kind):
            return self._advance()

        token = self._peek()
        raise ParseError(message, token.position)

    def _expect_keyword(self, word):
        if self._check_keyword(word):
            return self._advance()

        token = self._peek()
        raise ParseError(f"expected {word!r}", token.position)


def parse(source):
    """Tokenize and parse one complete relational algebra expression."""

    return Parser(tokenize(source)).parse()


parse_query = parse

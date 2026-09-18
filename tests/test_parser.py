import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO

from ra import main
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
from src.parser import parse
from src.tree_printer import format_tree


def comparison(operator, left, right):
    return Comparison(operator, Attribute(left), Number(right))


class ParserRequiredCaseTests(unittest.TestCase):
    def test_case_10_union_and_minus_are_left_associative(self):
        self.assertEqual(
            parse("A union B minus C"),
            Minus(
                Union(Relation("A"), Relation("B")),
                Relation("C"),
            ),
        )

    def test_case_11_repeated_minus_is_left_associative(self):
        self.assertEqual(
            parse("A minus B minus C"),
            Minus(
                Minus(Relation("A"), Relation("B")),
                Relation("C"),
            ),
        )

    def test_case_12_not_and_or_precedence(self):
        tree = parse("select[not (a=1 and b=2) or c>3](R)")
        expected_condition = Or(
            Not(
                And(
                    comparison("=", "a", 1),
                    comparison("=", "b", 2),
                )
            ),
            comparison(">", "c", 3),
        )
        self.assertEqual(tree, Select(expected_condition, Relation("R")))

    def test_case_13_and_binds_more_tightly_than_or(self):
        tree = parse("select[a=1 and b=2 or c=3](R)")
        expected_condition = Or(
            And(
                comparison("=", "a", 1),
                comparison("=", "b", 2),
            ),
            comparison("=", "c", 3),
        )
        self.assertEqual(tree, Select(expected_condition, Relation("R")))

    def test_case_14_nested_project_and_select(self):
        tree = parse(
            "project[Name](select[Age>30](select[DID='D1'](Employees)))"
        )
        expected = Project(
            (Attribute("Name"),),
            Select(
                comparison(">", "Age", 30),
                Select(
                    Comparison(
                        "=",
                        Attribute("DID"),
                        String("D1"),
                    ),
                    Relation("Employees"),
                ),
            ),
        )
        self.assertEqual(tree, expected)

    def test_case_15_parentheses_override_precedence(self):
        self.assertEqual(
            parse("(A union B) minus (C intersect D)"),
            Minus(
                Union(Relation("A"), Relation("B")),
                Intersect(Relation("C"), Relation("D")),
            ),
        )

    def test_case_16_missing_closing_parenthesis_has_position(self):
        query = "select[Age>30](R"

        with self.assertRaises(ParseError) as error:
            parse(query)

        self.assertEqual(error.exception.position, len(query))
        self.assertIn("expected ')'", error.exception.message)

    def test_case_17_empty_project_list_is_an_error(self):
        query = "project[](R)"

        with self.assertRaises(ParseError) as error:
            parse(query)

        self.assertEqual(error.exception.position, query.index("]"))
        self.assertIn("at least one attribute", error.exception.message)


class ParserAdditionalTests(unittest.TestCase):
    def test_whitespace_does_not_change_the_tree(self):
        self.assertEqual(
            parse("select[x1=3](R)"),
            parse("select[ x1 = 3 ]( R )"),
        )

    def test_keyword_can_be_an_attribute(self):
        tree = parse("select[union=3](R)")
        self.assertEqual(
            tree,
            Select(comparison("=", "union", 3), Relation("R")),
        )

    def test_not_can_be_an_attribute_or_an_operator(self):
        tree = parse("select[not=1 or not a=2](R)")
        self.assertEqual(
            tree,
            Select(
                Or(
                    comparison("=", "not", 1),
                    Not(comparison("=", "a", 2)),
                ),
                Relation("R"),
            ),
        )

    def test_qualified_attribute(self):
        tree = parse("select[Emp.DID=Dept.DID](R)")
        self.assertEqual(
            tree,
            Select(
                Comparison(
                    "=",
                    Attribute(name="DID", source="Emp"),
                    Attribute(name="DID", source="Dept"),
                ),
                Relation("R"),
            ),
        )

    def test_project_accepts_ordered_qualified_attribute_list(self):
        self.assertEqual(
            parse("project[Emp.Name,DID](R)"),
            Project(
                (
                    Attribute(name="Name", source="Emp"),
                    Attribute("DID"),
                ),
                Relation("R"),
            ),
        )

    def test_rename_times_and_join_are_parsed(self):
        condition = Comparison(
            "=",
            Attribute(name="DID", source="Emp"),
            Attribute(name="DID", source="Dept"),
        )
        self.assertEqual(
            parse("rename[Emp](R) times S join[Emp.DID=Dept.DID] T"),
            Join(
                condition,
                Times(Rename("Emp", Relation("R")), Relation("S")),
                Relation("T"),
            ),
        )

    def test_all_comparison_operators_are_parsed(self):
        for operator in ("=", "!=", "<", "<=", ">", ">="):
            with self.subTest(operator=operator):
                tree = parse(f"select[a{operator}1](R)")
                self.assertEqual(
                    tree,
                    Select(comparison(operator, "a", 1), Relation("R")),
                )

    def test_tree_printer_is_readable_and_stable(self):
        tree = parse("project[Name](select[Age>30](Employees))")
        self.assertEqual(
            format_tree(tree),
            "Project(attrs=[Name])\n"
            "└── Select(cond=Gt(Attr(Age), Num(30)))\n"
            "    └── Relation(Employees)",
        )

    def test_binary_tree_printer_shows_grouping(self):
        self.assertEqual(
            format_tree(parse("A union B minus C")),
            "Minus\n"
            "├── Union\n"
            "│   ├── Relation(A)\n"
            "│   └── Relation(B)\n"
            "└── Relation(C)",
        )

    def test_trailing_input_is_rejected(self):
        with self.assertRaises(ParseError) as error:
            parse("A B")

        self.assertEqual(error.exception.position, 2)
        self.assertIn("after complete expression", error.exception.message)


class TreeCommandTests(unittest.TestCase):
    def test_tree_command_prints_without_executing(self):
        output = StringIO()

        with redirect_stdout(output):
            exit_code = main(
                ["--tree", "project[Name](select[Age>30](Employees))"]
            )

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            output.getvalue(),
            "Project(attrs=[Name])\n"
            "└── Select(cond=Gt(Attr(Age), Num(30)))\n"
            "    └── Relation(Employees)\n",
        )

    def test_tree_command_reports_parse_error_without_traceback(self):
        error_output = StringIO()

        with redirect_stderr(error_output):
            exit_code = main(["--tree", "select[Age>30](R"])

        message = error_output.getvalue()
        self.assertEqual(exit_code, 1)
        self.assertEqual(
            message,
            "Syntax error at position 16: "
            "expected ')' to close select input\n",
        )
        self.assertNotIn("Traceback", message)


if __name__ == "__main__":
    unittest.main()

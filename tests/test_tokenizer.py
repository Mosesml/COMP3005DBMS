import unittest

from src.errors import LexicalError
from src.tokenizer import tokenize


class TokenizerTests(unittest.TestCase):

    def test_no_whitespace(self):
        tokens = tokenize("select[x1=3](R)")
        self.assertEqual(tokens[2].value, "x1")
        self.assertEqual(tokens[3].kind, "EQ")
        self.assertEqual(tokens[4].value, 3)

    def test_whitespace_does_not_matter(self):
        a = [(t.kind, t.value) for t in tokenize("select[x1=3](R)")]
        b = [(t.kind, t.value) for t in tokenize("select[ x1 = 3 ](R)")]
        self.assertEqual(a, b)

    def test_greater_equal(self):
        tokens = tokenize("select[Age>=30](R)")
        self.assertTrue(any(t.kind == "GE" for t in tokens))

    def test_negative_number(self):
        tokens = tokenize("select[Age>-30](R)")
        values = [(t.kind, t.value) for t in tokens]
        self.assertIn(("GT", ">"), values)
        self.assertIn(("NUMBER", -30), values)

    def test_parenthesis_inside_string(self):
        tokens = tokenize("select[Name='Bob)'](R)")
        self.assertTrue(
            any(t.kind == "STRING" and t.value == "Bob)" for t in tokens)
        )

    def test_comma_inside_string(self):
        tokens = tokenize("select[Name='a,b'](R)")
        self.assertTrue(
            any(t.kind == "STRING" and t.value == "a,b" for t in tokens)
        )

    def test_doubled_quote(self):
        tokens = tokenize("select[Name='O''Brien'](R)")
        self.assertTrue(
            any(t.kind == "STRING" and t.value == "O'Brien" for t in tokens)
        )

    def test_keyword_can_be_identifier(self):
        tokens = tokenize("select[union=3](R)")
        self.assertTrue(
            any(t.kind == "IDENT" and t.value == "union" for t in tokens)
        )

    def test_unterminated_string(self):
        with self.assertRaises(LexicalError) as error:
            tokenize("select[Name='Bob](R)")

        self.assertEqual(error.exception.position, 12)


if __name__ == "__main__":
    unittest.main()
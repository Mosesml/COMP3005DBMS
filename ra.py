import argparse
import sys

from src.errors import LexicalError, ParseError
from src.parser import parse
from src.tree_printer import print_tree


def main(argv=None):
    argument_parser = argparse.ArgumentParser(
        description="Parse handwritten relational algebra queries."
    )
    argument_parser.add_argument(
        "--tree",
        required=True,
        metavar="QUERY",
        help="parse QUERY and print its syntax tree without executing it",
    )
    arguments = argument_parser.parse_args(argv)

    try:
        tree = parse(arguments.tree)
        print_tree(tree)
    except (LexicalError, ParseError) as error:
        print(error, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

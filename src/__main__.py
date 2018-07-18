import argparse
import sys

from sourced.ml.cmd.args import add_repo2_args
from sourced.ml.cmd import ArgumentDefaultsHelpFormatterNoNone
from cmd.code2vec_extract_features import code2vec_extract_features


def get_parser() -> argparse.ArgumentParser:
    """
    Creates the cmdline argument parser.
    """
    parser = argparse.ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatterNoNone)

    # sourced.engine args

    subparsers = parser.add_subparsers(help="Commands", dest="command")

    extract_parser = subparsers.add_parser("extract",
                                           help="Extract features from input repositories",
                                           formatter_class=ArgumentDefaultsHelpFormatterNoNone)

    extract_parser.set_defaults(handler=code2vec_extract_features)

    add_repo2_args(extract_parser)

    # code2vec specific args
    extract_parser.add_argument('--max-length', type=int, default=5, help="Max path length.",
                                required=False)
    extract_parser.add_argument('--max-width', type=int, default=2, help="Max path width.",
                                required=False)
    extract_parser.add_argument('-o', '--output', type=str,
                                help="Output path for the Code2VecFeatures model", required=True)
    return parser


def main():
    parser = get_parser()

    args = parser.parse_args()

    try:
        handler = args.handler
    except AttributeError:
        def print_usage(_):
            parser.print_usage()

        handler = print_usage

    return handler(args)


if __name__ == "__main__":
    sys.exit(main())

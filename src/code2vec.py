import logging
import argparse
from uuid import uuid4

from extractors.paths import UastPathsBagExtractor
from sourced.ml.transformers import UastDeserializer, Uast2BagFeatures, create_uast_source, \
    UastRow2Document, Collector
from sourced.ml.utils.engine import pipeline_graph, pause
from sourced.ml.cmd.args import add_repo2_args

@pause
def code2vec(args):
    log = logging.getLogger("code2vec")
    session_name = "code2vec-%s" % uuid4()
    root, start_point = create_uast_source(args, session_name)

    res = start_point \
        .link(UastRow2Document()) \
        .link(UastDeserializer()) \
        .link(Uast2BagFeatures([UastPathsBagExtractor(args.max_length, args.max_width)])) \
        .link(Collector()) \
        .execute()

    # TODO: Add rest of data pipeline: extract distinct paths and terminal nodes for embedding mapping
    # TODO: Add transformer to write bags and vocabs to a model
    # TODO: Add ML pipeline

    pipeline_graph(args, log, root)


def main():
    parser = argparse.ArgumentParser()

    # sourced.engine args
    add_repo2_args(parser)

    # code2vec specific args
    parser.add_argument('-g', '--max_length', type=int, default=5, help="Max path length.",
                        required=False)
    parser.add_argument('-w', '--max_width', type=int, default=2, help="Max path width.",
                        required=False)

    args = parser.parse_args()

    code2vec(args)


if __name__ == '__main__':
    main()

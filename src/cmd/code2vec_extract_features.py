import logging
from uuid import uuid4

from extractors.paths import UastPathsBagExtractor
from transformers.vocabulary2id import Vocabulary2Id
from sourced.ml.transformers import UastDeserializer, Uast2BagFeatures, create_uast_source, \
    UastRow2Document, Moder
from sourced.ml.utils.engine import pipeline_graph, pause


@pause
def code2vec_extract_features(args):
    log = logging.getLogger("code2vec")
    session_name = "code2vec-%s" % uuid4()
    root, start_point = create_uast_source(args, session_name)

    res = start_point \
        .link(Moder("func")) \
        .link(UastRow2Document()) \
        .link(UastDeserializer()) \
        .link(Uast2BagFeatures([UastPathsBagExtractor(args.max_length, args.max_width)])) \
        .link(Vocabulary2Id(root.session.sparkContext, args.output)) \
        .execute()

    # TODO: Add rest of data pipeline: extract distinct paths and terminal nodes for embedding mapping
    # TODO: Add transformer to write bags and vocabs to a model
    # TODO: Add ML pipeline

    pipeline_graph(args, log, root)

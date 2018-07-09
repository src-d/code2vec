from algorithms.uast_to_bag_paths import Uast2BagOfPaths
from sourced.ml.extractors import BagsExtractor, register_extractor


@register_extractor
class UastPathsBagExtractor(BagsExtractor):
    NAME = "code2vec"
    NAMESPACE = "v."

    def __init__(self, max_length=5, max_width=5, **kwargs):
        super().__init__(**kwargs)
        self.uast2paths = Uast2BagOfPaths(max_length, max_width)

    def uast_to_bag(self, uast):
        return {str(path): 1 for path in self.uast2paths(uast)}

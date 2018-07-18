from algorithms.path_contexts import get_paths
from sourced.ml.utils import PickleableLogger
from collections import Counter

class Uast2BagOfPaths(PickleableLogger):
    """
    Converts a UAST to a bag of path contexts
    """

    def __init__(self, max_length=5, max_width=5):
        """
        :param max_length: of the extracted paths
        :param max_width: max width of the extracted paths (i.e., number of leaves between the start and end of the path)
        """
        super().__init__()
        self._max_length = max_length
        self._max_width = max_width

    def __call__(self, uast):
        """
        Converts a UAST to a weighed bag-of-path-contexts.
        The tokens are preprocessed by _token_parser.

        :param uast: The UAST root node.
        :return: list(tuple) list of paths context like (u, path, v) where u & v and the
        starting and ending leaf, and path is the list of nodes in their minimal distance path.
        """

        path_contexts = get_paths(uast, self._max_length, self._max_width)
        dict_of_paths = Counter(path_contexts)
        self._log.info("Extracted paths successfully")

        return dict_of_paths

    def _get_log_name(self):
        return self.__class__.__name__

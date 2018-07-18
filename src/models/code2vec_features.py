from modelforge import register_model, Model
from itertools import islice


@register_model
class Code2VecFeatures(Model):
    """
    Code2VecFeatures model - path contexts from source code.
    """
    NAME = "code2vec_features"

    def construct(self, value2index, path2index, value2freq, path2freq, path_contexts):
        self._value2index = value2index
        self._path2index = path2index
        self._value2freq = value2freq
        self._path2freq = path2freq

        self._path_contexts = path_contexts
        return self

    def _load_tree(self, tree):
        self.construct(value2index=tree["value2index"],
                       path2index=tree["path2index"],
                       value2freq=tree["value2freq"],
                       path2freq=tree["path2freq"],
                       path_contexts=tree["path_contexts"])

    @property
    def value2index(self):
        """
        Dict mapping value -> ID.
        """
        return self._value2index

    @property
    def path2index(self):
        """
        Dict mapping path -> ID.
        """
        return self._path2index

    @property
    def value2freq(self):
        """
         Dict mapping value -> frequency.
        """
        return self._value2freq

    @property
    def path2freq(self):
        """
         Dict mapping path -> frequency.
        """
        return self._path2freq

    @property
    def path_contexts(self):
        """
        List with the processed source code identifiers.
        """
        return self._path_contexts

    def value2index_items(self):
        """
        Returns the tuples belonging to value -> index mapping.
        """
        return self._value2index.items()

    def path2index_items(self):
        """
        Returns the tuples belonging to path -> index mapping.
        """
        return self._path2index.items()

    def value2freq_items(self):
        """
        Returns the tuples belonging to value -> freq mapping.
        """
        return self._value2freq.items()

    def path2freq_items(self):
        """
        Returns the tuples belonging to path -> freq mapping.
        """
        return self._path2freq.items()

    def _generate_tree(self):
        return {"value2index": self._value2index,
                "path2index": self._path2index,
                "value2freq": self._value2freq,
                "path2freq": self._path2freq,
                "path_contexts": self._path_contexts}

    def dump(self):
        return "Number of values: %s\n" \
               "Number of paths: %s\n" \
               "First 10 value -> ID: %s\n" \
               "First 10 path -> ID: %s\n" \
               "First 10 value -> frequency: %s\n" \
               "First 10 path -> frequency: %s" % \
               (len(self._value2index_freq),
                len(self.path2index_freq),
                list(islice(self._value2index, 10)),
                list(islice(self._path2index, 10)),
                list(islice(self._value2freq, 10)),
                list(islice(self._path2freq, 10)))

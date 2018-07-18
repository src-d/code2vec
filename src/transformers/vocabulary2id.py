import operator

from pyspark import RDD, Row
from models.code2vec_features import Code2VecFeatures

from ast import literal_eval as make_tuple
from sourced.ml.transformers import Transformer


class Vocabulary2Id(Transformer):
    def __init__(self, sc, output: str, **kwargs):
        super().__init__(**kwargs)
        self.output = output
        self.sc = sc

    def __call__(self, rows: RDD):
        value2index, path2index, value2freq, path2freq = self.build_vocabularies(rows)

        doc2path_contexts = self.build_doc2pc(value2index, path2index, rows)

        doc2path_contexts = doc2path_contexts.collect()

        Code2VecFeatures().construct(value2index=value2index,
                                     path2index=path2index,
                                     value2freq=value2freq,
                                     path2freq=path2freq,
                                     path_contexts=doc2path_contexts).save(
            self.output)

    @staticmethod
    def _unstringify_path_context(row):
        """
        Takes a row containing ((pc, doc), freq) and returns a tuple (u, path, v)
        (removes namespace prefix v.)
        """
        return make_tuple(row[0][0][2:])

    def build_vocabularies(self, rows: RDD):
        """
        Process rows to gather values and paths with their frequencies.
        :param rows: row structure is ((key, doc), val) where:
            * key: str with the path context
            * doc: file name
            * val: number of occurrences of key in doc
        """

        def _flatten_row(row: Row):
            # 2: removes the namespace v. from the string to parse it as tuple
            k = Vocabulary2Id._unstringify_path_context(row)
            return [(k[0], 1), (k[1], 1), (k[2], 1)]

        rows = rows \
            .flatMap(_flatten_row) \
            .reduceByKey(operator.add) \
            .persist()

        values = rows.filter(lambda x: type(x[0]) == str).collect()
        paths = rows.filter(lambda x: type(x[0]) == tuple).collect()

        value2index = {w: id for id, (w, _) in enumerate(values)}
        path2index = {w: id for id, (w, _) in enumerate(paths)}
        value2freq = {w: freq for _, (w, freq) in enumerate(values)}
        path2freq = {w: freq for _, (w, freq) in enumerate(paths)}

        rows.unpersist()

        return value2index, path2index, value2freq, path2freq

    def build_doc2pc(self, value2index: dict, path2index: dict, rows: RDD):
        """
        Process rows and build elements (doc, [path_context_1, path_context_2, ...])
        :param value2index_freq: value -> id
        :param path2index_freq: path -> id
        """

        bc_value2index = self.sc.broadcast(value2index)
        bc_path2index = self.sc.broadcast(path2index)

        def _doc2pc(row: Row):
            (u, path, v), doc = Vocabulary2Id._unstringify_path_context(row), row[0][1]

            return doc, (bc_value2index.value[u], bc_path2index.value[path],
                         bc_value2index.value[v])

        rows = rows \
            .map(_doc2pc) \
            .distinct() \
            .combineByKey(lambda value: [value],
                          lambda x, value: x + [value],
                          lambda x, y: x + y)

        bc_value2index.unpersist(blocking=True)
        bc_path2index.unpersist(blocking=True)

        return rows

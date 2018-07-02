from collections import OrderedDict
from typing import List, Tuple, Dict

import bblfsh
import json


class ExtNode(object):
    """
    Extended Node used for efficiently extract paths from a tree structure

    bn, depth, numeration: are initialized during tree top-down traversal
    children: during the recursive return call
    log_parents: annotated in a separate traversal

    """

    def __init__(self, base_node: bblfsh.Node, depth: int, numeration: int=-1, children=(),
                 log_parents=()):
        """

        :param base_node: original tree node
        :param depth: depth of the node in the tree
        :param numeration: if node is a leave indicates the position from left to right
        (0-indexed), otherwise it's -1
        :param children: list of the extended children of 'bn'
        :param log_parents: list of the log_parents used to compute the least
        common ancestor (lca)
        """
        self.bn = base_node
        self.depth = depth
        self.numeration = numeration
        self.children = children
        self.log_parents = log_parents

    @property
    def token(self):
        """
        :rtype: defines which is the token given depending on the base node
        """
        if type(self.bn) == bblfsh.Node:
            return self.bn.internal_type

    @staticmethod
    def extend_node(node: bblfsh.Node, depth: int, num: int, leaves: List)\
            -> Tuple:
        """
        Transforms a tree of nodes to ExtNode which holds information required to create
        paths (i.e., depth, leaf number, and log_parents) and returns a list of containing all leaves.
        Log_parents are not annotated in this traversal.
        :param node: node to transform
        :param depth: current depth of traversal (0=based)
        :param num: number of leaves already numbered (i.e., # to assign to next leaf)
        :param leaves: list of seen leaves
        :return: current node as ExtNode and 'num'
        """
        if len(node.children) == 0:
            ext_node = ExtNode(node, depth, num)
            leaves.append(ext_node)
            return ext_node, num + 1
        else:
            ext_node = ExtNode(node, depth, -1)
            new_children = [None] * len(node.children)
            for i, child in enumerate(node.children):
                new_children[i], num = ExtNode.extend_node(child, depth + 1, num, leaves)

            ext_node.children = new_children

            return ext_node, num

    def annotate_log_parents(self, parents: List):
        """
        Adds the log_parents attribute to each node
        :param self: current node to annotate
        :param parents: list of current node's parents until the root
        """
        if len(parents) > 0:
            self.log_parents = [parents[i] for i in
                                [(2 ** i) - 1 for i in range(0, len(parents)) if
                                 2 ** i < len(parents)]]
        for i, child in enumerate(self.children):
            child.annotate_log_parents([self] + parents)

    def _as_dict(self) -> OrderedDict:
        # custom base representation depending on the base node
        base_repr = [('token', 'N/A')]
        if isinstance(type(self.bn), bblfsh.Node.__class__):
            base_repr = [("token", self.bn.token), ("internal_type", self.bn.internal_type)]

        ext_repr = [("depth", self.depth), ("numeration", self.numeration)]
        if len(self.children) > 0:
            # if node has children
            children = [n._as_dict() for n in self.children]
            ext_repr = [("depth", self.depth), ("numeration", self.numeration),
                        ("children", children)]

        return OrderedDict(base_repr + ext_repr)

    @staticmethod
    def extend_tree(root: bblfsh.Node) -> Tuple:
        """
        Transforms a tree of nodes type(node) to ExtNode which holds information required to create
        paths (i.e., depth, leaf number, and log_parents) and returns a list of containing all leaves
        :param root: root of the tree to extend
        :return: extended tree and the list of its leaves
        """
        ext_tree = None
        leaves = []
        if len(root.children) > 0:
            ext_tree, _ = ExtNode.extend_node(root, 0, 0, leaves)
            ext_tree.annotate_log_parents([ext_tree])

        return ext_tree, leaves

    def to_json(self) -> str:
        """ Return a JSON representation of this node and all children. """
        return json.dumps(self._as_dict(), indent=4, separators=(',', ': '))

    def __repr__(self) -> str:
        return self.to_json()

    def __str__(self) -> str:
        return self.to_json()

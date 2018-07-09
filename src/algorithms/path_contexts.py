from algorithms.structures.extended_node import ExtNode

import bblfsh

UP = "UP"
DOWN = "DOWN"


def node_to_internal_type(node: bblfsh.Node):
    """
    Use the internal_type property of a node as its final path representation
    :param node: base_node
    :return: node's internal_type or the string itself (in case its UP/DOWN token or a leaf)
    """
    if type(node) == str:
        return node
    return node.internal_type


def node_to_roles(node: bblfsh.Node):
    """
    Converte bblfsh roles of a node to a unique string representation
    :param node: base_node
    :return: node's roles or the string's hash (in case its UP/DOWN token or a leaf)
    """
    return " | ".join(bblfsh.role_name(r) for r in sorted(node.roles))


def lca(u: ExtNode, v: ExtNode):
    """
    Computes least common ancestor of 2 nodes using log_parents and depth
    :param u: origin node
    :param v: destiny node
    :return: least commo ancestor
    """
    if u.depth < v.depth:
        u, v = v, u

    for i in range(len(u.log_parents), -1, -1):
        if len(u.log_parents) > i and u.log_parents[i].depth >= v.depth:
            u = u.log_parents[i]

    if u == v:
        return u

    for i in range(len(u.log_parents), -1, -1):
        if u == v:
            break
        if len(u.log_parents) > i and len(v.log_parents) > i and u.log_parents[i] != v.log_parents[
            i]:
            u = u.log_parents[i]
            v = v.log_parents[i]

    return v.log_parents[0]


def distance(u: ExtNode, v: ExtNode, ancestor: ExtNode):
    """
    Computes distance of the path from u to v using the lca node as:
        d(u,v) = d(root, u) + d(root, v) - 2 * d(root, lca)
    :param u:
    :param v:
    :param ancestor:
    :return:
    """
    dru = u.depth
    drv = v.depth
    drlca = ancestor.depth

    return dru + drv - 2 * drlca


def get_path(u: ExtNode, v: ExtNode, ancestor: ExtNode, leaf_token,
             up_symbol=UP, down_symbol=DOWN):
    """
    Returns the path from u to v separated by up an down symbols.
    The path is formed by the original base nodes.
    :param u: start node
    :param v: end node
    :param ancestor: least common ancestor of u and v
    :param leaf_token: how to get leaf token out of start/end nodes
    :param up_symbol: symbol indicating next token is parent of the previous
    :param down_symbol: symbol indicating next token is a child of the previous
    :return:
    """
    path = []

    start, end = leaf_token(u), leaf_token(v)

    while u != ancestor:
        path.append(u.bn)
        path.append(up_symbol)
        u = u.log_parents[0]

    path.append(ancestor.bn)

    aux_path = []

    while v != ancestor:
        aux_path.append(v.bn)
        aux_path.append(down_symbol)
        v = v.log_parents[0]

    path = path + aux_path[::-1]

    return start, tuple(path), end


# dirty hardcoding to avoid getting paths with comments as start/end
def is_noop_line(node):
    return node.bn.internal_type == 'NoopLine' or node.bn.internal_type == 'SameLineNoops'


def get_paths(uast: bblfsh.Node, max_length: int, max_width: int,
              token_extractor=node_to_internal_type, leaf_token=lambda node: node.bn.token):
    """
    Creates a list of all the paths given the max_length and max_width restrictions.
    :param uast_file: file containing a bblfsh UAST as string and binary-coded
    :param max_length:
    :param max_width:
    :param token_extractor: function to transform a node into a single string token
    :param leaf_token: get leaves token as a different node
    :return: list(tuple) list of paths context like (u, path, v) where u & v and the starting and
     ending leaf, and path is the list of nodes in their minimal distance path.
    """

    tree, leaves = ExtNode.extend_tree(uast)

    paths = []
    if len(leaves) < 2:
        return []

    for i in range(len(leaves)):
        for j in range(i + 1, min(i + max_width, len(leaves))):
            u, v = leaves[i], leaves[j]
            # TODO decide where to filter comments and maybe decouple from bblfsh
            if not is_noop_line(u) and not is_noop_line(v):
                ancestor = lca(u, v)
                d = distance(u, v, ancestor)
                if d <= max_length:
                    u, path, v = get_path(u, v, ancestor, leaf_token=leaf_token)
                    # convert nodes to its desired representation
                    paths.append((u, tuple([token_extractor(p) for p in path]), v))

    return paths

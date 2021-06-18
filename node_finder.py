import networkx as nx


# Return all neighbors excluding old (already known) ones (supplied in a list)
def find_new_neighbors(node, known, nx_graph):
    discovered = []

    neighbors = nx.neighbors(nx_graph, node)
    for i in list(neighbors):
        if i in known:
            continue
        else:
            discovered.append(str(i))

    return discovered


# Find the leaf nodes => Walk through tree til you can't walk no more
def find_leaf_nodes(node, nx_graph):
    # TODO: read this maybe for more efficiency
    # https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.chains.chain_decomposition.html#networkx.algorithms.chains.chain_decomposition
    touched = [node]
    to_search = [node]
    leaves = []

    while len(to_search) > 0:
        for i in list(to_search):
            to_search.remove(i)
            touched.append(str(i))
            neighbors = find_new_neighbors(i, touched, nx_graph)
            if len(neighbors) == 0:
                leaves.append(str(i))
            else:
                for j in neighbors:
                    to_search.append(j)

    return leaves

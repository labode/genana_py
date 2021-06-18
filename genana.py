import networkx as nx
import math
import sys
import nrrd_writer
import dot_writer
import csv_writer
from node_finder import find_new_neighbors, find_leaf_nodes


def read_graph(file):
    # Read graph from .dot file using pydot and turn it into a networkx graph
    dot_graph = nx.drawing.nx_pydot.read_dot(file)

    return dot_graph


def generation_analysis(node, nx_graph):
    gen = 1
    visited = [node]
    nodes = [node]

    while len(nodes) != 0:
        nn = []
        for i in nodes:
            visited.append(i)
            neighbors = find_new_neighbors(i, visited, nx_graph)
            for j in neighbors:
                print("Edge between " + str(i) + " and " + str(j) + " has gen " + str(gen))
                nx_graph[str(i)][str(j)][0]['Gen'] = gen
                nn.append(j)
        nodes = nn
        gen += 1

    return graph


def order_analysis(node, nx_graph):
    pos = find_leaf_nodes(node, nx_graph)
    visited = []
    order = 1

    # Only ascend from one point, if we have already visited n-1 of its neighbours; otherwise try other points first
    # We are done, when we reach the root node
    while len(pos) != 1 or pos[0] != node:
        add = []
        rm = []
        for i in pos:
            neighbors = list(nx.neighbors(graph, i))
            visited.append(i)

            rm_n = []
            for j in neighbors:
                if j in visited:
                    if j not in pos:
                        rm_n.append(j)
            for k in rm_n:
                neighbors.remove(k)

            if len(list(neighbors)) == 1:
                print("The edge between node " + str(i) + " and " + str(neighbors[0]) + " has order " + str(order))
                nx_graph[str(i)][str(neighbors[0])][0]['Ord'] = order
                rm.append(i)
                add.append(neighbors[0])

        for i in add:
            if i not in pos:
                pos.append(i)

        for i in rm:
            pos.remove(i)
            if i not in visited:
                visited.append(i)

        order += 1

    return nx_graph


# Just like order, but after gen 1 only increment generation by one when two equal generations meet
def strahler_order(node, nx_graph):
    positions = find_leaf_nodes(node, nx_graph)
    visited = []

    # Only ascend from one point, if we have already visited n-1 of its neighbours; otherwise try other points first
    # We are done, when we reach the root node
    while len(positions) != 1 or positions[0] != node:
        add = []
        rm = []
        for position in positions:
            neighbors = list(nx.neighbors(graph, position))
            visited.append(position)

            rm_n = []
            for j in neighbors:
                if j in visited:
                    if j not in positions:
                        rm_n.append(j)
            for k in rm_n:
                neighbors.remove(k)

            if len(list(neighbors)) == 1:
                # Get neighbours of our node
                bordering = list(nx.neighbors(nx_graph, position))

                # Get their orders
                orders = []
                for point in bordering:
                    # Try block is needed, as we can not access a label, if it has not been assigned yet
                    # => would throw an error when starting at leaf nodes
                    try:
                        orders.append(nx_graph[str(position)][str(point)][0]['Str_Ord'])
                    except KeyError:
                        continue

                # If we have no existing orders, we start at 1 (position is a leaf node)
                if len(orders) == 0:
                    order = 1
                # If there is only one previous order, there is no increase, we assign the previous order
                elif len(orders) == 1:
                    # Get their order
                    order = orders[0]
                # If we have multiple incoming nodes, he have to check for a possible increase
                else:
                    # Order values in array in descending order
                    orders.sort()
                    orders = orders[::-1]
                    # If we have two equal orders, we increase the order by one
                    if orders[0] == orders[1]:
                        order = orders[0] + 1
                    # If we have dissimilar orders, we continue with the highest one
                    else:
                        order = orders[0]

                # Write new order into graph
                nx_graph[str(position)][str(neighbors[0])][0]['Str_Ord'] = order

                print(
                    "The edge between node "
                    + str(position) + " and "
                    + str(neighbors[0])
                    + " has strahler order " + str(order)
                )
                rm.append(position)
                add.append(neighbors[0])

        for i in add:
            if i not in positions:
                positions.append(i)

        for i in rm:
            positions.remove(i)
            if i not in visited:
                visited.append(i)

    return nx_graph


# just like genana, but every edge gets its unique id instead of a generation
# to be used for external grouping according to properties of the graph segments
# TODO: probably very over engineered
def give_id(node, nx_graph):
    unique_id = 1
    visited = [node]
    nodes = [node]

    while len(nodes) != 0:
        nn = []
        for i in nodes:
            visited.append(i)
            neighbors = find_new_neighbors(i, visited, nx_graph)
            for j in neighbors:
                print("Edge between " + str(i) + " and " + str(j) + " has id " + str(unique_id))
                nx_graph[str(i)][str(j)][0]['Id'] = unique_id
                nn.append(j)
                unique_id += 1
        nodes = nn

    return nx_graph


def calculate_length(nx_graph, size):

    # get all edges
    edges = list(nx.edges(graph))

    for edge in edges:
        pos_arr = []

        # Get the coordinates of the starting point of the edge
        node_0 = graph.node[str(edge[0])]['spatial_node']
        node_0 = node_0.replace('"', '')
        coords = node_0.split(' ')
        pos_arr.append(coords)

        # Get all coordinates along the edge between start and end point
        edge_points = graph[str(edge[0])][str(edge[1])][0]['spatial_edge']
        # TODO: The return looks like a json array, but using a json parser does not work
        # As this is a pretty simple string cleanup we do it by hand to save time
        to_replace = ['"', '[', ']', '{', '}']
        for j in to_replace:
            edge_points = edge_points.replace(j, '')

        # As we potentially get multiple coordinates, we need to separate them
        edge_coords = edge_points.split(',')

        # Now we have a list with three values as each entry. We split them again, to get an array of 3d coordinates
        for j in edge_coords:
            coords = j.split(' ')
            pos_arr.append(coords)

        # Get the coordinates of the end point of the edge
        node_1 = graph.node[str(edge[1])]['spatial_node']
        node_1 = node_1.replace('"', '')
        coords = node_1.split(' ')
        pos_arr.append(coords)

        # Now that we have all coordinates our edge consists of, we can calculate the overall length
        length = 0
        start = []
        for pos in pos_arr:
            # When two nodes border each other, the edge has no coordinates (length = 0)
            # So if the array we receive is empty, we can just move on to the next one
            if pos[0] == '':
                continue
            else:
                # When we have a starting point, we can begin to calculate distances
                if len(start) != 0:
                    length += math.sqrt((int(start[0]) - int(pos[0])) ** 2
                                        + (int(start[1]) - int(pos[1])) ** 2
                                        + (int(start[2]) - int(pos[2])) ** 2)

                start = [pos[0], pos[1], pos[2]]

        nx_graph[str(edge[0])][str(edge[1])][0]['Length'] = round(length * float(size), 4)

    return nx_graph


if __name__ == '__main__':
    try:
        dotfile = sys.argv[1]
        output = sys.argv[2]
        analysis_type = sys.argv[3]
        root_node = sys.argv[4]

        dim_x = sys.argv[5]
        dim_y = sys.argv[6]
        dim_z = sys.argv[7]

        dims = [int(dim_x), int(dim_y), int(dim_z)]

        off_x = sys.argv[8]
        off_y = sys.argv[9]
        off_z = sys.argv[10]

        off = [int(off_x), int(off_y), int(off_z)]

    except IndexError:
        sys.exit('Missing parameters \nPlease supply: dotfile, output_filename, analysis_type (0-4), root_node,'
                 'x dim, y dim, z dim, x offset, y offset, z offset')

    try:
        voxel_size = sys.argv[11]
    except IndexError:
        voxel_size = 1
        print('No voxel size supplied, 1 will be used for .nrrd header and length calculations')

    # Color map is optional
    try:
        color_map = sys.argv[12]
    except IndexError:
        color_map = ''

    # TODO: Make writing of .dot (, .png) and .nrrd independently available?

    graph = read_graph(dotfile)

    if int(analysis_type) == 0:
        graph_w_gens = generation_analysis(root_node, graph)
        dot_writer.write(graph_w_gens, output, root_node, False, 'Gen', color_map)
        nrrd_writer.write(graph_w_gens, dims, off, voxel_size, output, 'Gen')
    elif int(analysis_type) == 1:
        graph_w_ord = order_analysis(root_node, graph)
        dot_writer.write(graph_w_ord, output, root_node, False, 'Ord', color_map)
        nrrd_writer.write(graph_w_ord, dims, off, voxel_size, output, 'Ord')
    elif int(analysis_type) == 2:
        graph_w_str_ord = strahler_order(root_node, graph)
        dot_writer.write(graph_w_str_ord, output, root_node, True, 'Str_Ord', color_map)
        nrrd_writer.write(graph_w_str_ord, dims, off, voxel_size, output, 'Str_Ord')
    elif int(analysis_type) == 3:
        graph_w_ids = give_id(root_node, graph)
        dot_writer.write(graph_w_ids, output, root_node, False, 'Id', color_map)
        nrrd_writer.write(graph_w_ids, dims, off, voxel_size, output, 'Id')
    # Run all analysis types consecutively and write results to .csv
    elif int(analysis_type) == 4:
        graph_w_ids = give_id(root_node, graph)
        graph_w_gens = generation_analysis(root_node, graph_w_ids)
        graph_w_ord = order_analysis(root_node, graph_w_gens)
        graph_w_str_ord = strahler_order(root_node, graph_w_ord)
        # TODO: We now request the voxel size from the user, so we could use it for the length calculation!
        graph_w_length = calculate_length(graph_w_str_ord, voxel_size)
        csv_writer.write(graph_w_length, output, ['Id', 'Gen', 'Ord', 'Str_Ord', 'Length'])
    else:
        print("Analysis type not supported")

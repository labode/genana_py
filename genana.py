import networkx as nx
import math
import argparse
import nrrd_writer
import dot_writer
import csv_writer
from node_finder import find_new_neighbors, find_leaf_nodes


def read_graph(file):
    # Read graph from .dot file and turn it into a networkx graph
    # https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pydot.read_dot.html
    dot_graph = nx.Graph(nx.drawing.nx_pydot.read_dot(file))

    return dot_graph


def generation_analysis(node, nx_graph):
    gen = 1
    visited = []
    nodes = [node]

    while len(nodes) != 0:
        nn = []
        for i in nodes:
            visited.append(i)
            neighbors = find_new_neighbors(i, visited, nx_graph)
            for j in neighbors:
                print("Edge between " + str(i) + " and " + str(j) + " has gen " + str(gen))
                nx_graph[str(i)][str(j)]['Gen'] = gen
                if j in nodes:
                    continue
                else:
                    nn.append(j)
        nodes = nn
        gen += 1

    return nx_graph


def order_analysis(node, nx_graph, strahler=False):
    positions = find_leaf_nodes(node, nx_graph)
    visited = []
    previous = []
    deadlock = False
    if strahler:
        label = 'Str_Ord'
    else:
        label = 'Ord'

    # Only ascend from one point, if we have already visited n-1 of its neighbours; otherwise try other points first
    # We are done, when we have nowhere left to go
    while len(positions) > 0:
        nodes_to_add = []
        nodes_to_remove = []

        if positions == previous:
            print('Deadlock detected')
            deadlock = True
            # okay, we did not manage to ascend in the last round thus, we will have to either solve the underlying problem or abort
            # Hypothesis: There is a connection between the positions we are currently standing on and until that is solved, we can not continue to new positions
            # Find the connection
            i = 0
            j = 1
            length = len(positions)
            solved = False
            # Here we walk through all possible connections between our current positions
            while length > i and not solved:
                neighbors = list(nx.neighbors(nx_graph, positions[i]))
                while length > j:
                    if positions[j] in neighbors:
                        print('There is a connection between position ' + str(positions[i]) + ' and position ' + str(positions[j]))
                        print('Solving...')
                        # Assign an order to that connection
                        orders_i = get_orders(nx_graph, positions[i], label)
                        orders_j = get_orders(nx_graph, positions[j], label)
                        new_order_i = determine_order(orders_i, strahler)
                        new_order_j = determine_order(orders_j, strahler)
                        # Identify higher order and assign it...
                        if new_order_i >= new_order_j:
                            new_order = new_order_i
                        else:
                            new_order = new_order_j
                        nx_graph = assign_order(nx_graph, positions[i], positions[j], new_order, label)

                        # exit both loops
                        solved = True
                        break

                    j += 1
                i += 1

            # Continue with the normal routine. Either that was the sole problem or we solve the next one next time...
            if not solved:
                exit('Deadlock could not be solved. Exiting.')

        previous = positions.copy()

        for position in positions:
            if not deadlock:
                if position not in visited:
                    visited.append(position)

            neighbors = list(nx.neighbors(nx_graph, position))

            if position not in visited:
                visited.append(position)

            rm_n = []
            for neighbor in neighbors:
                if neighbor in visited:
                    if neighbor not in positions:
                        rm_n.append(neighbor)
            for k in rm_n:
                neighbors.remove(k)

            if deadlock:
                offenders = positions.copy()
                offenders.remove(position)
                for offender in offenders:
                    neighbors.remove(offender)

            if len(list(neighbors)) == 1:
                orders = get_orders(nx_graph, position, label)
                new_order = determine_order(orders, strahler)

                nx_graph = assign_order(nx_graph, position, neighbors[0], new_order, label)

                nodes_to_remove.append(position)
                nodes_to_add.append(neighbors[0])

        for i in nodes_to_add:
            if i not in positions and i != node:
                positions.append(i)

        for i in nodes_to_remove:
            positions.remove(i)
            if i not in visited:
                visited.append(i)

        deadlock = False

    return nx_graph


# just like genana, but every edge gets its unique id instead of a generation
# to be used for external grouping according to properties of the graph segments
# TODO: probably very over engineered
def give_id(node, nx_graph):
    unique_id = 1
    visited = []
    nodes = [node]

    while len(nodes) != 0:
        nn = []
        for i in nodes:
            visited.append(i)
            neighbors = find_new_neighbors(i, visited, nx_graph)
            for j in neighbors:
                print("Edge between " + str(i) + " and " + str(j) + " has id " + str(unique_id))
                nx_graph[str(i)][str(j)]['Id'] = unique_id
                unique_id += 1
                if j in nodes:
                    continue
                else:
                    nn.append(j)
        nodes = nn

    return nx_graph


def get_orders(nx_graph, position, label):
    neighbours = list(nx.neighbors(nx_graph, position))

    # Get their orders
    orders = []
    for neighbour in neighbours:
        # Try block is needed, as we can not access a label, if it has not been assigned yet
        # => would throw an error when starting at leaf nodes
        try:
            orders.append(nx_graph[str(position)][str(neighbour)][label])
        except KeyError:
            continue

    return orders


def determine_order(orders, strahler = False):
    # If we have no existing orders, we start at 1 (position is a leaf node); identical for strahler and regular
    if len(orders) == 0:
        order = 1
    else:
        # Here we have to act depending on the different order metrics
        if strahler:
            # If there is only one previous order, there is no increase, we assign the previous order
            if len(orders) == 1:
                # Get their order
                order = orders[0]
            # If we have multiple incoming nodes, we have to check for a possible increase
            else:
                # Here we attribute either the highest incoming order or of two equal orders come in, we increment by one
                # Order values in array in descending order
                orders.sort()
                orders = orders[::-1]
                # If we have two equal orders, we increase the order by one
                if orders[0] == orders[1]:
                    order = orders[0] + 1
                # If we have dissimilar orders, we continue with the highest one
                else:
                    order = orders[0]
        else:
            # Otherwise, the highest incoming order is increased by 1
            orders.sort()
            orders = orders[::-1]
            order = orders[0] + 1

    return order


def assign_order(nx_graph, position_0, position_1, order, label):
    # Write new order into graph
    nx_graph[str(position_0)][str(position_1)][label] = order

    # Provide information for the user
    print(
        'The edge between node '
        + str(position_0) + ' and '
        + str(position_1)
        + ' has ' + label + ' ' + str(order)
    )

    return nx_graph


def calculate_length(nx_graph, size):

    # get all edges
    edges = list(nx.edges(nx_graph))

    for edge in edges:
        pos_arr = []

        # Get the coordinates of the starting point of the edge
        node_0 = nx_graph.node[str(edge[0])]['spatial_node']
        node_0 = node_0.replace('"', '')
        coords = node_0.split(' ')
        pos_arr.append(coords)

        # Get all coordinates along the edge between start and end point
        edge_points = nx_graph[str(edge[0])][str(edge[1])]['spatial_edge']
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
        node_1 = nx_graph.node[str(edge[1])]['spatial_node']
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

        nx_graph[str(edge[0])][str(edge[1])]['Length'] = round(length * float(size), 4)

    return nx_graph

# TODO: Possible extension: Add function to calculate path length from every leaf node to the root node?

# TODO: Possible extension: Calculate cumulated sizes for strahler order
#  => connected segments of the same order are counted as one segment
#  Caution! counting should be done from the leaf nodes up, checking each step,
#  that the distance to the root node gets smaller. Otherwise we might walk into a bordering branch of the same order


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyzes a .dot graph')
    # Mandatory arguments
    parser.add_argument('input_file', action='store', type=str, help='.dot file to analyze')
    parser.add_argument('analysis_type', choices=['gen', 'ord', 'str_ord', 'id', 'global'],
                        help='Analysis you wish to perform. Options: Generations, Orders, Strahler orders, Ids '
                             'or a global analysis performing all of them')
    parser.add_argument('root_node', action='store', type=str, help='Root node of the graph')
    parser.add_argument('dim_x', action='store', type=int, help='Volume image dimension x')
    parser.add_argument('dim_y', action='store', type=int, help='Volume image dimension y')
    parser.add_argument('dim_z', action='store', type=int, help='Volume image dimension z')
    # Note: Float is used, as type conversions, etc. can lead to offset values of e.g. 1.15999999999 in file headers
    parser.add_argument('--offset_x', action='store', type=float, default=0, required=False,
                        help='Image offset in x dimension; If not supplied, 0 is used')
    parser.add_argument('--offset_y', action='store', type=float, default=0, required=False,
                        help='Image offset in y dimension; If not supplied, 0 is used')
    parser.add_argument('--offset_z', action='store', type=float, default=0, required=False,
                        help='Image offset in z dimension; If not supplied, 0 is used')
    # Optional arguments
    parser.add_argument('-v', '--voxel_size', action='store', type=float, default=1, required=False,
                        help='Voxel edge length; If not supplied, 1 is used; only isometric voxels are supported')
    parser.add_argument('-o', '--output_file', action='store', type=str, default='analysis',
                        required=False, help='Name of output file; If not supplied, '
                                             'analysis[.dot|.png|.nrrd|.csv] is used')
    parser.add_argument('-c', '--color_map', action='store', type=str, required=False, help='Path to color map')

    args = parser.parse_args()

    # Basic information
    input_file = args.input_file
    root_node = args.root_node
    analysis_type = args.analysis_type

    # Sizing
    dim_x = args.dim_x
    dim_y = args.dim_y
    dim_z = args.dim_z

    off_x = args.offset_x
    off_y = args.offset_y
    off_z = args.offset_z

    voxel_size = args.voxel_size

    # Misc. optional arguments
    output = args.output_file
    color_map = args.color_map

    # Preparation of the size data for further use
    dims = [int(dim_x), int(dim_y), int(dim_z)]
    off = [float(off_x), float(off_y), float(off_z)]

    # TODO: Make writing of .dot (, .png) and .nrrd independently available?

    print('Reading graph')
    graph = read_graph(input_file)

    if analysis_type == 'gen':
        print('Performing Generation analysis')
        graph_w_gens = generation_analysis(root_node, graph)
        print('Writing graph to ' + output + '.dot and ' + output + '.png')
        dot_writer.write(graph_w_gens, output, root_node, False, 'Gen', color_map)
        print('Writing .nrrd to ' + output + '.nrrd')
        nrrd_writer.write(graph_w_gens, dims, off, voxel_size, output, 'Gen')
    elif analysis_type == 'ord':
        print('Performing Order analysis')
        graph_w_ord = order_analysis(root_node, graph)
        print('Writing graph to ' + output + '.dot and ' + output + '.png')
        dot_writer.write(graph_w_ord, output, root_node, False, 'Ord', color_map)
        print('Writing .nrrd to ' + output + '.nrrd')
        nrrd_writer.write(graph_w_ord, dims, off, voxel_size, output, 'Ord')
    elif analysis_type == 'str_ord':
        print('Performing Strahler order analysis')
        graph_w_str_ord = order_analysis(root_node, graph, True)
        print('Writing graph to ' + output + '.dot and ' + output + '.png')
        dot_writer.write(graph_w_str_ord, output, root_node, True, 'Str_Ord', color_map)
        print('Writing .nrrd to ' + output + '.nrrd')
        nrrd_writer.write(graph_w_str_ord, dims, off, voxel_size, output, 'Str_Ord')
    elif analysis_type == 'id':
        print('Performing Id analysis')
        graph_w_ids = give_id(root_node, graph)
        print('Writing graph to ' + output + '.dot and ' + output + '.png')
        dot_writer.write(graph_w_ids, output, root_node, False, 'Id', color_map)
        print('Writing .nrrd to ' + output + '.nrrd')
        nrrd_writer.write(graph_w_ids, dims, off, voxel_size, output, 'Id')
    # Run all analysis types consecutively and write results to .csv
    else:  # The only analysis_type possible is now 'global'
        print('Performing global analysis')
        graph_w_ids = give_id(root_node, graph)
        graph_w_gens = generation_analysis(root_node, graph_w_ids)
        graph_w_ord = order_analysis(root_node, graph_w_gens)
        graph_w_str_ord = order_analysis(root_node, graph_w_ord, True)
        print('Calculating length')
        graph_w_length = calculate_length(graph_w_str_ord, voxel_size)
        print('Writing .csv to ' + output + '.csv')
        csv_writer.write(graph_w_length, output, ['Id', 'Gen', 'Ord', 'Str_Ord', 'Length'])

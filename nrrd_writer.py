import numpy as np
import nrrd
import pydot


def write(dot_graph, dims, edges, target_file):
    # Read the (input!) graph (again...), as it contains the edge coordinates we need to write the .nrrd
    # We need to do this, as the coordinates do not seem to be accessible from the networkx graph
    # TODO: Look at networkx again to make sure there is no way to access these
    graphs = pydot.graph_from_dot_file(dot_graph)
    graph = graphs[0]

    # Initialize array in the needed size
    array = np.zeros(dims, int)

    # Now the easy part: Get the coordinates of all edges
    # and write the label id in the corresponding position in the array
    for i in edges:
        # Array for all coordinates of this edge
        pos_arr = []

        # Get the coordinates of the starting point of the edge
        node_0 = graph.get_node(str(i[0])).__getitem__(0).get('spatial_node')
        node_0 = node_0.replace('"', '')
        coords = node_0.split(' ')
        pos_arr.append(coords)

        # Get the coordinates of the end point of the edge
        node_1 = graph.get_node(str(i[1])).__getitem__(0).get('spatial_node')
        node_1 = node_1.replace('"', '')
        coords = node_1.split(' ')
        pos_arr.append(coords)

        # Get all coordinates along the edge between start and end point
        edge = graph.get_edge(str(i[0]), str(i[1])).__getitem__(0).get('spatial_edge')
        # TODO: The return looks like a json array, but using a json parser does not work
        # As this is a pretty simple string cleanup we do it by hand to safe time
        to_replace = ['"', '[', ']', '{', '}']
        for j in to_replace:
            edge = edge.replace(j, '')

        # As we potentially get multiple coordinates, we need to separate them
        edge_coords = edge.split(',')

        # Now we have a list with three values as each entry. We split them again, to get an array of 3d coordinates
        for j in edge_coords:
            coords = j.split(' ')
            pos_arr.append(coords)

        # Now that we have all coordinates our edge consists of, we can set these to the edge label in our array
        for j in pos_arr:
            array[int(j[0]), int(j[1]), int(j[2])] = i[2]

    # Set filename to write into
    filename = str(target_file) + ".nrrd"

    # Define header values (see https://pynrrd.readthedocs.io/en/latest/examples.html)
    # TODO: Precision in space directions correct? Let user supply value somewhere? Parse from .mha?
    header = {'kinds': ['domain', 'domain', 'domain'],
              'space': 'left-posterior-superior',
              'space directions':
                  np.array([[7.0003299999999991, 0, 0], [0, 7.0003299999999991, 0], [0, 0, 7.0003299999999991]]),
              'encoding': 'raw'}
    # write our array into a .nrrd file
    nrrd.write(filename, array, header)

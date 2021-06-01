import numpy as np
import networkx as nx
import nrrd


def write(graph, dims, target_file, label='Gen'):

    # Initialize array in the needed size
    if label == 'Id':
        # While our number of generations/Orders is far below 256, ids go well above that
        # So in this case we need more storage space
        array = np.zeros(dims, dtype=np.ushort)
    else:
        array = np.zeros(dims, dtype=np.ubyte)

    # Now the easy part: Get the coordinates of all edges
    # and write the label id in the corresponding position in the array
    edges = list(nx.edges(graph))

    for edge in edges:
        # Array for all coordinates of this edge
        pos_arr = []

        # Get the coordinates of the starting point of the edge
        node_0 = graph.node[str(edge[0])]['spatial_node']
        node_0 = node_0.replace('"', '')
        coords = node_0.split(' ')
        pos_arr.append(coords)

        # Get the coordinates of the end point of the edge
        node_1 = graph.node[str(edge[1])]['spatial_node']
        node_1 = node_1.replace('"', '')
        coords = node_1.split(' ')
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

        # Now that we have all coordinates our edge consists of, we can set these to the edge label in our array
        for j in pos_arr:
            # When two nodes border each other, the edge has no coordinates (length = 0)
            # So if the array we receive is empty, we can just move on to the next one
            if j[0] == '':
                continue
            else:
                if label == 'Id':
                    array[int(j[0]), int(j[1]), int(j[2])] = np.ushort(int(graph[edge[0]][edge[1]][0][label]))
                else:
                    array[int(j[0]), int(j[1]), int(j[2])] = np.ubyte(int(graph[edge[0]][edge[1]][0][label]))

    # Set filename to write into
    filename = str(target_file) + ".nrrd"

    # Define header values (see https://pynrrd.readthedocs.io/en/latest/examples.html)
    # TODO: Precision in space directions correct? Let user supply value somewhere? Parse from .mha?
    header = {'kinds': ['domain', 'domain', 'domain'],
              'space': 'left-posterior-superior',
              'space origin':
                  np.array([0, 0, 660]),
              'space directions':
                  np.array([[4.4000000000000004, 0, 0], [0, 4.4000000000000004, 0], [0, 0, 4.4000000000000004]]),
              'encoding': 'raw'}

    # write our array into a .nrrd file
    nrrd.write(filename, array, header)

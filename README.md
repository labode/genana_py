# Generation analysis toolkit
This is a collection of tools for the analysis of graph branching. It currently supports Generations [1], Orders [2], Strahler Orders [3] and ID assignment.
Built to work on GraphViz output from https://github.com/phcerdan/SGEXT

## How does it work?
- Reads supplied .dot graph into networkx representation
- Walks through the graph, assigning labels to edges according to one or more of the classification metrics
- Outputs either a labeled graph for a specific metric (.dot file, optional: .png 2D rendering, .nrrd 3D volume file) or the analysis results of all assignment methods as a single .csv file

## Warning!
This tool is aimed at the analysis of dichotomous branching structures (i.e. starting from the root node, at every 
branching point the tree should split into two or more subtrees, that are **not** interconnected). 
If that is not the case, results might not be what the user expects. Generations may increase in ways that are not expected, but the program will return results.
For (Strahler-) orders such interconnections may lead to a deadlock situation in the algorithm. The program will warn about this and try to fix it, but may not be successful and will abort without results.
Again, even if the program succeeds, order attribution might not be as expected, some edges might not even be caught at all.

## Requirements
Required packages are listed in requirements.txt and can be installed using pip as follows:\
`pip3 install -r requirements.txt`

## Input
### Mandatory
- .dot graph containing nodes, edges and coordinate labels (graph **must** be a (rooted) tree i.e. may **not** contain any parallel edges/circular paths)
- Analysis mode (see below)
- Root node of the supplied graph
- When the nrrd option is used: Volume size
- When the nrrd option is used, the supplied graph **must** contain spatial information for nodes and edges

### Optional
- When the nrrd option is used: Volume offset (for .nrrd header)
- Output filename (defaults to analysis[.dot|.png|.nrrd|.csv])
- Voxel edge length (only symmetrical voxels are supported) for .nrrd header and length calculation (default = 1)
- .csv containing RGB values (comma separated, one RGB color per line) for coloring the output graph 


## Output
- .dot graph (for gen/ord/str_ord/id)
- Optional (when --png option is used) .png image of graph (for gen/ord/str_ord/id)
- Optional (when nrrd option is used) .nrrd representation of graph (can be stretched back over initial volume image thinned by SGEXT) (for gen/ord/str_ord/id)
- .csv containing graph data (for global)

## Usage
### Modes
- gen = Generation analysis (Output = .dot, .png, .nrrd) 
- ord = Order (Output = .dot, .png, .nrrd)
- str_ord = Strahler Order (Output = .dot, .png, .nrrd)
- id = ID assignment (Output = .dot, .png, .nrrd)
- global = Comparative analysis (Does all the classification methods plus edge length calculation, outputs results as .csv)

### Argument order
`python3 genana.py input_file {gen,ord,str_ord,id,global} root_node nrrd dim_x dim_y dim_z`

For help and additional information run `python3 genana.py -h`

### Example
For an order analysis of the file graph.dot, root node label = 0, volume size = 100 * 100 * 100 voxels, offset = 5, 5, 5 voxels, voxel size = 2 um, output filename = test_run, .png output is requested, no extra color map is provided

`python3 genana.py graph.dot ord 0 nrrd 100 100 100 --offset_x 5 --offset_y 5 --offset_z 5 -v 2 -o test_run --png`

[1] Weibel, E.R., 1963. Geometric and dimensional airway models of conductive, transitory and respiratory zones of the human lung, in: Morphometry of the Human Lung. Springer Berlin Heidelberg, pp. 136-142.\
[2] Horsfield, K., 1984. Axial pathways compared with complete data in morphological studies of the lung. Respiration Physiology 55, 317-324.\
[3] Strahler, A.N., 1957. Quantitative analysis of watershed geomorphology. Eos, Transactions American Geophysical Union 38, 913-920.

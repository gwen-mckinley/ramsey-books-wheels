"""
Example of verifying Ramsey lower bound construction, for R(W5, W9).

Uses SageMath to verify the correctness of the provided lower bound
construction for the Ramsey number R(W5, W9).

Authorship:
    This code was written by Gwen McKinley, in support of the paper
    "Small Ramsey numbers for books, wheels, and generalizations" by
    Bernard Lidický, Gwen McKinley, Florian Pfender, and Steven Van
    Overberghe.
"""
from sage.all import Graph, graphs, matrix  # type: ignore

# Define graph to be checked.
M = matrix(
    [
        [0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1],
        [0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0],
        [0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0],
        [0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0],
        [0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 1],
        [0, 1, 1, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0],
        [1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1],
        [1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1],
        [0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0],
        [1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],
        [1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1],
        [1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1],
        [0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1],
        [0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],
    ]
)

G = Graph(M, format="adjacency_matrix")
# or if G is given as graph6-string, use e.g.:
# G = Graph(r"PIL{eMI^Jqp[gXkp_|zxOaww")
print("\nAdjacency matrix of graph G:")

print(M)
print(f"\nOrder of G: {G.order()}")


# Define monochromatic subgraphs to be checked.
color_0_order = 5
color_1_order = 9

color_0_subgraph = graphs.WheelGraph(color_0_order)
color_1_subgraph = graphs.WheelGraph(color_1_order)

# Use SageMath to determine if forbidden subgraphs are present.
bad_present_0 = color_0_subgraph.is_subgraph(
    G.complement(), induced=False, up_to_isomorphism=True
)
bad_present_1 = color_1_subgraph.is_subgraph(
    G, induced=False, up_to_isomorphism=True
)

print(
    f"G contains a copy of the wheel W_{color_0_order} in color 0: ",
    bad_present_0,
)
print(
    f"G contains a copy of the wheel W_{color_1_order} in color 1: ",
    bad_present_1,
)

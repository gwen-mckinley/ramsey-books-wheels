"""
Example of verifying Ramsey lower bound construction, for R(B2, B8).

Uses SageMath to verify the correctness of the provided lower bound
construction for the Ramsey number R(B2, B8).

Authorship:
    This code was written by Gwen McKinley, in support of the paper
    "Small Ramsey numbers for books, wheels, and generalizations" by
    Bernard Lidický, Gwen McKinley, Florian Pfender, and Steven Van
    Overberghe.
"""
from sage.all import Graph, matrix  # type: ignore


def book(k: int) -> Graph:
    """
    Creates a copy of B_k (i.e., a book with k+2 vertices).

    Args:
        k: the number of "pages" in the book to be created.

    Returns:
        A copy of the book B_k as a SageMath "Graph" object. Note: this
        book has k+2 vertices, not k vertices.
    """
    adj_dict = {0: list(range(1, k + 2)), 1: list(range(2, k + 2))}

    return Graph(adj_dict)


# Define graph to be checked.
M = matrix(
    [
        [0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 1, 0, 0, 1],
        [1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1],
        [1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1, 1],
        [0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0],
        [1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        [0, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 1],
        [1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1],
        [1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0],
        [0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0],
        [0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1],
        [1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1],
        [1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1],
        [0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0],
        [1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 0],
        [1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0],
        [1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1],
        [0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1],
        [0, 0, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0],
        [1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0],
    ]
)

G = Graph(M, format="adjacency_matrix")
# or if G is given as graph6-string, use e.g.:
# G = Graph(r"SXgcISrdSaJQBJs_jp@CWFOV?q}HWOPbc")
print("\nAdjacency matrix of graph G:")

print(M)
print(f"\nOrder of G: {G.order()}")


# Define monochromatic subgraphs to be checked.
k_0 = 2
k_1 = 8

color_0_order = k_0 + 2
color_1_order = k_1 + 2

color_0_subgraph = book(k_0)
color_1_subgraph = book(k_1)

# Use SageMath to determine if forbidden subgraphs are present.
bad_present_0 = color_0_subgraph.is_subgraph(
    G.complement(), induced=False, up_to_isomorphism=True
)
bad_present_1 = color_1_subgraph.is_subgraph(
    G, induced=False, up_to_isomorphism=True
)

print(f"G contains a copy of the book B_{k_0} in color 0: ", bad_present_0)
print(f"G contains a copy of the book B_{k_1} in color 1: ", bad_present_1)

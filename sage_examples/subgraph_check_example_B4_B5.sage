"""
Example of verifying Ramsey lower bound construction, for R(B4, B5).

Uses SageMath to verify the correctness of the provided lower bound
construction for the Ramsey number R(B4, B5).

Authorship:
    This code was written by Gwen McKinley, in support of the paper
    "Small Ramsey numbers for books, wheels, and generalizations" by
    Bernard Lidický, Gwen McKinley, and Florian Pfender.
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
        [0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1],
        [0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0],
        [1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0],
        [1, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 1, 0],
        [0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1],
        [0, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0],
        [0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0],
        [1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1],
        [1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1],
        [0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1],
        [1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1],
        [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1],
        [1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1],
        [0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, 1, 1, 0, 1],
        [1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0],
        [0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0],
        [1, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0],
        [1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
    ]
)

G = Graph(M, format="adjacency_matrix")
print("\nAdjacency matrix of graph G:")

print(M)
print(f"\nOrder of G: {G.order()}")


# Define monochromatic subgraphs to be checked.
color_0_order = 6
color_1_order = 7

color_0_subgraph = book(color_0_order)
color_1_subgraph = book(color_1_order)


print(
    f"G contains a copy of the book B_{color_0_order -2} in color 0: "
    f"{color_0_subgraph.is_subgraph(G.complement(), up_to_isomorphism = True)}"
)
print(
    f"G contains a copy of the book B_{color_1_order -2} in color 1: "
    f"{color_1_subgraph.is_subgraph(G, up_to_isomorphism = True)}"
)

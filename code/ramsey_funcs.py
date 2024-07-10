"""
Contains various helper functions for the RamseyGraph class.

Includes most of the underlying "machinery" for the RamseyGraph class,
including scoring/subgraph counting functions, and various functions
used in initializing RamseyGraph instances.

Authorship:
    This code was written by Gwen McKinley, in support of the paper
    "Small Ramsey numbers for books, wheels, and generalizations" by
    Bernard Lidický, Gwen McKinley, and Florian Pfender.
"""

import math
from functools import cache
from itertools import combinations
from typing import Any, Callable, TypeVar

import numpy as np


def common_neighbors(
    neighbors: np.ndarray, num_verts: int, num_colors: int
) -> np.ndarray:
    """
    Finds the common neighbors of each pair of vertices.

    Args:
        neighbors: An array storing the neighborhood of each
            vertex of an edge-colored graph in each color.
        num_verts: The number of vertices in the graph.
        num_colors: The number of possible edge-colors.

    Returns:
        An array storing the set of common neighbors of each pair of
        vertices of the graph, in each color. Indexed by colors and
        vertices: the entry at indices [c, i, j] is the set of common
        neighbors of vertex i and vertex j in color c.
    """
    common_nbhds = np.empty((num_colors, num_verts, num_verts), dtype=object)

    for i, j in combinations(range(num_verts), 2):
        for color in range(num_colors):
            common_nbhds[color, i, j] = neighbors[color, i].intersection(
                neighbors[color, j]
            )
            # Populate the array symmetrically for vertex pairs -- note
            # that since sets are mutable, updating the array later on
            # for i,j will cause an update for j,i as well. This is
            # convenient, and means we never have to worry about the
            # order of pairs of vertices.
            common_nbhds[color, j, i] = common_nbhds[color, i, j]

    return common_nbhds


def count_books(
    adj_matrix: np.ndarray,
    common_neighbors: np.ndarray,
    num_verts: int,
    bad_sizes: list[int],
    **_,
) -> int:
    """
    Counts monochromatic "books" in an edge-colored graph.

    Args:
        adj_matrix: The adjacency matrix of an edge-colored graph.
            (entries = edge-colors)
        common_neighbors: An array storing the set of common
            neighbors of each pair of vertices in the graph, in each
            color.
        num_verts: The number of vertices in the graph.
        bad_sizes: The size of books being counted in each color.

    Returns:
        The number of monochromatic books in the graph, with sizes
        specified by "bad_sizes." For example, if bad_sizes = [4,5],
        it will count the number of 4-vertex books in color 0, plus
        the number of 5-vertex books in color 1.
    """
    num_books = 0

    # Choose a "spine" edge (u, v).
    for u, v in combinations(range(num_verts), 2):
        color = adj_matrix[u, v]
        # Choose the remaining "pages" of the book from among common
        # neighbors of u and v.
        num_common_nbrs = len(common_neighbors[color, u, v])
        books_on_edge = my_comb(num_common_nbrs, bad_sizes[color] - 2)
        num_books += books_on_edge

    return num_books


def count_books_change(
    common_neighbors: np.ndarray,
    edge_change: tuple[tuple, int, int],
    bad_sizes: list[int],
    **_,
) -> int:
    """
    Score change function for "books."

    Args:
        common_neighbors: An array storing the common neighbors of
            each pair of vertices in an edge-colored graph, in each
            color.
        edge_change: A tuple of the form (edge, new_color, old_color).
        bad_sizes: The size of books being counted in each color.

    Returns:
        The change in the number of number of monochromatic books in the
        graph that would result from changing the specified edge from
        "old_color" to "new_color."
    """
    (u, v) = edge_change[0]
    new_color = edge_change[1]
    old_color = edge_change[2]

    new_size = bad_sizes[new_color]
    old_size = bad_sizes[old_color]

    new_nbrs = common_neighbors[new_color, u, v]
    old_nbrs = common_neighbors[old_color, u, v]

    # Score change from books with (u,v) as the spine.
    delta = my_comb(len(new_nbrs), new_size - 2)
    delta -= my_comb(len(old_nbrs), old_size - 2)

    # Count new books with (u,v) incident to a "page."
    for w in new_nbrs:
        # Choose one of u, v to form the spine with w, and the other
        # will be the "page" vertex.
        for spine_vtx in u, v:
            # Count new books with (spine_vtx,w) as the "spine."
            num_other_pages = len(common_neighbors[new_color, spine_vtx, w])
            delta += my_comb(num_other_pages, new_size - 3)

    # Count old books with (u,v) incident to a "page."
    for w in old_nbrs:
        # Choose one of u, v to form the spine with w, and the other
        # will be the "page" vertex.
        for spine_vtx in u, v:
            # Count old books with (spine_vtx,w) as the "spine." Note
            # that since u, v, and w are all adjacent in "old_color"
            # (i.e., the current color of the graph), the remaining
            # vertex not in (spine_vtx,w) is already counted in the
            # common neighborhood of spine_vtx and w, so we must take
            # care not to double-count it as a "page." This is the
            # reason we subtract 1 in "num_other_pages."
            num_other_pages = (
                len(common_neighbors[old_color, spine_vtx, w]) - 1
            )
            delta -= my_comb(num_other_pages, old_size - 3)

    return delta


def count_cycles_restricted(
    adj_matrix: np.ndarray,
    cycle_length: int,
    color: int,
    possible_vtxs: set,
    neighbors: np.ndarray,
) -> int:
    num_cycles = 0
    """
    Counts cycles induced on a given set of vertices.

    Args:
        adj_matrix: The adjacency matrix of an edge-colored graph.
            (entries = edge colors)
        cycle_length: The length of cycles to be counted.
        color: The edge-color of the cycles to be counted.
        possible_vtxs: A subset of the vertices of the graph.
        neighbors: An array storing the neighborhood of each vertex
            in the graph, in each color.


    Returns:
        The number of cycles in the graph (of length "cycle_length" and
        edge-color "color") induced on the set "possible_vtxs."
    """

    # Make a copy to avoid mutating the set outside the function call.
    possible_vtxs_copy = set(possible_vtxs)

    while len(possible_vtxs_copy) >= cycle_length - 1:
        # Fix a vertex in the cycle, to avoid rotation symmetry.
        vtx = possible_vtxs_copy.pop()

        # Choose the neighbors of the first vertex, in a canonical order
        # to avoid reflection symmetry.
        for s, t in combinations(
            possible_vtxs_copy.intersection(neighbors[color, vtx]), 2
        ):
            # Count ways to commplete the cycle.
            num_cycles += count_paths_s_to_t(
                s=s,
                t=t,
                color=color,
                possible_vtxs=possible_vtxs_copy.difference({s, t}),
                adj_matrix=adj_matrix,
                neighbors=neighbors,
                num_internal_vtxs=cycle_length - 3,
            )

    return num_cycles


def count_paths_s_t_middle(  # noqa: PLR0913
    s: int,
    t: int,
    internal_vtxs: set,
    color: int,
    neighbors: np.ndarray,
    adj_matrix: np.ndarray,
    num_internal_vtxs: int,
) -> int:
    """
    Counts paths from s to t with a given set of internal vertices.

    Args:
        s: A vertex in the graph (starting point).
        t: A vertex in the graph (ending point).
        internal_vtxs: A subset of the vertices of the graph.
        color: The edge-color of the paths to be counted.
        adj_matrix: The adjacency matrix of an edge-colored graph.
            (entries = edge colors)
        neighbors: An array storing the neighborhood of each vertex
            in the graph, in each color.
        num_internal_vertices: The number of internal vertices in the
            paths to be counted.


    Returns:
        The number of monochromatic paths (of color "color") from s to t
        in the graph, with precisely the set "internal_vtxs" as the
        internal vertices (in *some* order).
    """
    # If there are no internal vertices, we just need to test whether s
    # and t are adjacent (a "path" between them is just an edge).
    if num_internal_vtxs == 0:
        return adj_matrix[s, t] == color

    else:
        total_paths = 0
        # Assign a vertex to be the "last" internal vertex (i.e., to be
        # adjacent to t on the path), then recurse: count the (slightly
        # shorter) paths from s to that guy.
        for last_vtx in internal_vtxs.intersection(neighbors[color, t]):
            total_paths += count_paths_s_t_middle(
                s=s,
                t=last_vtx,
                internal_vtxs=internal_vtxs.difference({last_vtx}),
                color=color,
                neighbors=neighbors,
                adj_matrix=adj_matrix,
                num_internal_vtxs=num_internal_vtxs - 1,
            )

        return total_paths


def count_paths_s_to_t(  # noqa: PLR0913
    s: int,
    t: int,
    color: int,
    possible_vtxs: set,
    adj_matrix: np.ndarray,
    neighbors: np.ndarray,
    num_internal_vtxs: int,
) -> int:
    """
    Counts paths from s to t induced on a given set of vertices.

    Args:
        s: A vertex in the graph (starting point).
        t: A vertex in the graph (ending point).
        color: The edge-color of the paths to be counted.
        possible_vtxs: A subset of the vertices of the graph.
        adj_matrix: The adjacency matrix of an edge-colored graph.
            (entries = edge colors)
        neighbors: An array storing the neighborhood of each vertex
            in the graph, in each color.
        num_internal_vertices: The number of internal vertices of the
            paths to be counted.


    Returns:
        The number of monochromatic paths (of color "color") from s to t
        in the graph, having "num_internal_vtxs" internal vertices, all
        of which belong to the set "possible_vtxs."
    """
    total_paths = 0

    # Break down the number of paths from s to t according to the set of
    # internal vertices on the path. (Note that more than one path can
    # have the same set of internal vertices, in different orders.)
    for internal_vtxs in combinations(possible_vtxs, num_internal_vtxs):
        total_paths += count_paths_s_t_middle(
            s=s,
            t=t,
            internal_vtxs=set(internal_vtxs),
            color=color,
            neighbors=neighbors,
            adj_matrix=adj_matrix,
            num_internal_vtxs=num_internal_vtxs,
        )

    return total_paths


def count_wheels(
    adj_matrix: np.ndarray,
    neighbors: np.ndarray,
    num_verts: int,
    num_colors: int,
    bad_sizes: list[int],
    **_,
) -> int:
    """
    Counts monochromatic "wheels" in an edge-colored graph.

    Args:
        adj_matrix: The adjacency matrix of an edge-colored graph.
            (entries = edge-colors)
        neighbors: An array storing the neighborhood of each
            vertex in the graph, in each color.
        num_verts: The number of vertices in the graph.
        bad_sizes: The sizes of wheels being counted in each color.
            Assumes wheels of size 5 or more (otherwise wheels =
            cliques), and will overcount due to symmetry for wheels of
            size 4 or less.

    Returns:
        The number of monochromatic wheels in the graph, with sizes
        specified by "bad_sizes." For example, if bad_sizes = [5,6],
        it will count the number of 5-vertex wheels in color 0, plus
        the number of 6-vertex wheels in color 1.
    """
    num_wheels = 0

    for center_vtx in range(num_verts):
        for color in range(num_colors):
            # For a given "center vertex" and a given edge color, the
            # number of wheels is simply equal the number of cycles in
            # the neighborhood of that center vertex.
            num_wheels += count_cycles_restricted(
                adj_matrix=adj_matrix,
                cycle_length=bad_sizes[color] - 1,
                color=color,
                possible_vtxs=neighbors[color, center_vtx],
                neighbors=neighbors,
            )

    return num_wheels


def count_wheels_change(
    adj_matrix: np.ndarray,
    neighbors: np.ndarray,
    common_neighbors: np.ndarray,
    edge_change: tuple[tuple, int, int],
    bad_sizes: list[int],
    **_,
) -> int:
    """
    Score change function for "wheels."

    Args:
        adj_matrix: The adjacency matrix of an edge-colored graph.
            (entries = edge-colors)
        neighbors: An array storing the neighborhood of each
            vertex in the graph, in each color.
        common_neighbors: An array storing the common neighbors of
            each pair of vertices in an edge-colored graph, in each
            color.
        edge_change: A tuple of the form (edge, new_color, old_color).
        bad_sizes: The size of wheels being counted in each color.

    Returns:
        The change in the number of number of monochromatic wheels in
        the graph that would result from changing the specified edge
        from "old_color" to "new_color."
    """
    (u, v) = edge_change[0]
    new_color = edge_change[1]
    old_color = edge_change[2]

    new_size = bad_sizes[new_color]
    old_size = bad_sizes[old_color]

    new_kwargs = {
        "color": new_color,
        "adj_matrix": adj_matrix,
        "neighbors": neighbors,
    }
    old_kwargs = {
        "color": old_color,
        "adj_matrix": adj_matrix,
        "neighbors": neighbors,
    }

    delta = 0

    # Count new wheels where (u,v) is on the "rim."
    for center_vtx in common_neighbors[new_color, u, v]:
        delta += count_paths_s_to_t(
            s=u,
            t=v,
            possible_vtxs=neighbors[new_color, center_vtx].difference({u, v}),
            num_internal_vtxs=new_size - 3,
            **new_kwargs,
        )

    # Count old wheels where (u,v) is on the "rim."
    for center_vtx in common_neighbors[old_color, u, v]:
        delta -= count_paths_s_to_t(
            s=u,
            t=v,
            possible_vtxs=neighbors[old_color, center_vtx].difference({u, v}),
            num_internal_vtxs=old_size - 3,
            **old_kwargs,
        )

    # Count new wheels where u or v is the center vertex.
    for center_vtx in u, v:
        # Choose the two "rim vertices" that adjoin both u and v.
        for s, t in combinations(common_neighbors[new_color, u, v], 2):
            # Count ways to complete the "rim."
            delta += count_paths_s_to_t(
                s=s,
                t=t,
                possible_vtxs=neighbors[new_color, center_vtx].difference(
                    {s, t}
                ),
                num_internal_vtxs=new_size - 4,
                **new_kwargs,
            )

    # Count old wheels where u or v is the center vertex.
    for center_vtx in u, v:
        # Choose the two "rim vertices" that adjoin both u and v.
        for s, t in combinations(common_neighbors[old_color, u, v], 2):
            # Count ways to complete the "rim."
            delta -= count_paths_s_to_t(
                s=s,
                t=t,
                possible_vtxs=neighbors[old_color, center_vtx].difference(
                    {u, v, s, t}
                ),
                num_internal_vtxs=old_size - 4,
                **old_kwargs,
            )

    return delta


def hash_adj_matrix(adj_matrix: np.ndarray, num_verts: int) -> int:
    """
    Hash function for adjacency matrix of an edge-colored graph.

    This is a custom hash function to allow quick updating if an edge of
    the graph is edited (instead of having to re-hash the entire
    graph/adjacency matrix). It computes the hash of the graph as the
    bitwise XOR of hashes of the individual edges (defined by indices
    and color).

    Args:
        adj_matrix: The adjacency matrix of an edge-colored graph.
            (entries = edge-colors)
        num_verts: The number of vertices in the graph

    Returns:
        A hash of the adjacency matrix.
    """
    total_hash = 0
    for i, j in combinations(range(num_verts), 2):
        edge_color = ((i, j), adj_matrix[i, j])
        total_hash ^= hash(edge_color)

    return total_hash


@cache
def my_comb(n: int, k: int) -> int:
    """Speeds up math.comb (binomial coefficient function) by caching"""

    return math.comb(n, k)


def neighbors(
    adj_matrix: np.ndarray, num_verts: int, num_colors: int
) -> np.ndarray:
    """
    Finds the neighbors of each vertex in an edge-colored graph.

    Args:
        adj_matrix: The adjacency matrix of an edge-colored graph.
            (entries = edge-colors)
        num_verts: The number of vertices in the graph.
        num_colors: The number of possible edge-colors.

    Returns:
        An array storing the set of neighbors of each vertex of the
        graph in each color. Indexed by colors and vertices: the entry
        at indices [c, v] is the set of neighbors of vertex v in color
        c.
    """
    # Initialize each neighborhood in each color to be an empty set
    # (taking some care to ensure they are not the *same* set, and can
    # be edited independently).
    neighbors = np.array(
        [set() for _ in range(num_colors * num_verts)]
    ).reshape((num_colors, num_verts))

    # Populate neighborhoods from adjacency matrix.
    for i, j in combinations(range(num_verts), 2):
        color = adj_matrix[i, j]
        neighbors[color, i].add(j)
        neighbors[color, j].add(i)

    return neighbors


def rand_adj_matrix(num_verts: int, num_colors: int) -> np.ndarray:
    """
    Generates the adjacency matrix of a random edge-colored graph.

    Args:
        num_verts: The number of vertices in the graph.
        num_colors: The number of possible edge-colors.

    Returns:
        A matrix of dimension (num_verts)*(num_verts), with zeros along
        the diagonal, and all other entries chosen uniformly at random
        from {0,1,2, ... ,num_colors-1}.
    """
    adj_matrix = np.zeros((num_verts, num_verts), dtype=int)

    for i, j in combinations(range(num_verts), 2):
        adj_matrix[i, j] = np.random.choice(range(num_colors))
        adj_matrix[j, i] = adj_matrix[i, j]

    return adj_matrix


# Declare a type variable for use in the next function.
graph_instance = TypeVar("graph_instance")


def rand_graph(
    num_verts: int,
    num_colors: int,
    graph_class: Callable[..., graph_instance],
    **kwargs: dict[str, Any],
) -> graph_instance:
    """
    Generates a random edge-colored graph.

    Args:
        num_verts: The number of vertices in the graph.
        num_colors: The number of possible edge colors.
        graph_class: The class of the graph to be generated. (We will
            always use the "RamseyGraph" class.)
        kwargs: Any other arguments used to initialize an instance of
            the class "graph_class".

    Returns:
        A uniformly random edge-coloring of the complete graph on
        "num_verts" vertices, represented as an instance of the class
        "graph_class."
    """
    adj_matrix = rand_adj_matrix(num_verts=num_verts, num_colors=num_colors)
    graph = graph_class(
        adj_matrix=adj_matrix,
        **kwargs,
    )

    return graph


def valid_moves(adj_matrix: np.ndarray, num_colors: int) -> list[tuple]:
    """
    Creates a list of valid moves.

    Args:
        The adjacency matrix of an edge-colored graph.
            (entries = edge-colors)
        num_colors: The number of possible edge colors.

    Returns:
        A list of all possible edits to the edge coloring, each stored
        as a tuple of the form "(edge, new_color, current_color)."
    """
    num_verts = adj_matrix.shape[0]

    valid_moves = []

    for i, j in combinations(range(num_verts), 2):
        # For edge (i,j) include moves to any color other than its
        # current color.
        valid_moves += [
            ((i, j), color, adj_matrix[i, j])
            for color in range(num_colors)
            if color != adj_matrix[i, j]
        ]

    return valid_moves

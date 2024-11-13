"""
Contains the RamseyGraph class.

Authorship:
    This code was written by Gwen McKinley, in support of the paper
    "Small Ramsey numbers for books, wheels, and generalizations" by
    Bernard Lidický, Gwen McKinley, Florian Pfender, and Steven Van
    Overberghe.
"""

import sys
from typing import Any

import numpy as np

from ramsey_funcs import (
    common_neighbors,
    count_books,
    count_books_change,
    count_wheels,
    count_wheels_change,
    hash_adj_matrix,
    neighbors,
    valid_moves,
)

# Do not truncate large matrices when printing.
np.set_printoptions(threshold=sys.maxsize)
np.set_printoptions(linewidth=sys.maxsize)


class RamseyGraph:
    """
    An edge-colored complete graph.

    This class gives a representation of edge-colored graphs, and
    provides support for local search methods to discover colorings
    avoiding monochromatic "books" or "wheels" of specified sizes.

    Attributes:
        adj_matrix (array of ints): The adjacency matrix of the
            edge-colored graph (entries = edge-colors).

        bad_sizes (list[int]): The number of vertices in the subgraphs
            to be counted/avoided in each color. For example,
            bad_subgraph = 'books' and bad_sizes = [4,5] means we are
            trying to avoid books with 4 vertices in color 0, and books
            with 5 vertices in color 1.

        bad_subgraph (str):Either 'books' or 'wheels.'

        common_neighbors (array of sets): An array storing the set of
            common neighbors of each pair of vertices of the graph, in
            each color. Indexed by colors and vertices:
            common_neighbors[c, i, j] is the set of common neighbors of
            vertex i and vertex j in color c.

        hash (int): A hash of the graph. Computed in such a way that it
            can be quickly updated when an edge of the graph is edited.

        neighbors (array of sets): An array storing the set of neighbors
            of each vertex of the graph in each color. Indexed by colors
            and vertices: neighbors[c, v] is the set of neighbors of
            vertex v in color c.

        num_verts (int): The number of vertices in the graph.

        num_colors (int): The number of possible edge-colors.

        valid_moves (list): A list of all possible edits to the edge
            coloring, each stored as a tuple of the form
            "(edge, new_color, current_color)."
    """

    def __init__(
        self,
        adj_matrix: np.ndarray,
        bad_sizes: list[int],
        bad_subgraph: str,
        **_,
    ) -> None:
        if bad_subgraph not in ["books", "wheels"]:
            raise ValueError('Bad subraph must be "books" or "wheels".')
        elif bad_subgraph == "books" and min(bad_sizes) < 4:  # noqa: PLR2004
            raise ValueError(
                "Book with fewer than 4 vertices specified (which is a clique)"
                '. Scoring functions assume "true books" and will overcount'
                " books of order less than 4 due to symmetry."
            )
        elif bad_subgraph == "wheels" and min(bad_sizes) < 5:  # noqa: PLR2004
            raise ValueError(
                "Wheel with fewer than 5 vertices specified, (which is a"
                ' clique). Scoring functions assume "true wheels" and will'
                " overcount wheels of order less than 5 due to symmetry."
            )

        self.adj_matrix = adj_matrix
        self.bad_sizes = bad_sizes
        self.bad_subgraph = bad_subgraph

        self.num_verts = adj_matrix.shape[0]
        self.num_colors = len(bad_sizes)

        self.valid_moves = valid_moves(self.adj_matrix, self.num_colors)

        self.neighbors = neighbors(
            adj_matrix=self.adj_matrix,
            num_verts=self.num_verts,
            num_colors=self.num_colors,
        )

        self.common_neighbors = common_neighbors(
            neighbors=self.neighbors,
            num_verts=self.num_verts,
            num_colors=self.num_colors,
        )

        self.hash = hash_adj_matrix(
            adj_matrix=self.adj_matrix, num_verts=self.num_verts
        )

    def __str__(self):
        """Pretty formatting for adjacency matrix.

        Returns the adjacency matrix of the edge-colored graph as a
        string in a simple, readable format that, in the case of
        2-edge-coloring, can be copy-pasted as a graph adjacency matrix
        directly into Sage.
        """
        return str(np.array2string(self.adj_matrix, separator=","))

    # Represent the graph by its adjacency matrix for debugging, etc.
    __repr__ = __str__

    def __hash__(self) -> int:
        return self.hash

    def score(self) -> int:
        """
        Counts monochromatic copies of the "bad subgraphs."

        Returns:
            The number of monochromatic copies of the bad sugraphs in
            our edge-colored graph.

        Example: if self.bad_sizes = [4,5] and self.bad_sugraph =
            'books', it will return the number of 4-vertex books in
            color 0, plus the number of 5-vertex books in color 1.
        """
        if self.bad_subgraph == "books":
            score_func = count_books
        elif self.bad_subgraph == "wheels":
            score_func = count_wheels
        else:
            pass

        score = score_func(
            adj_matrix=self.adj_matrix,
            neighbors=self.neighbors,
            common_neighbors=self.common_neighbors,
            num_colors=self.num_colors,
            num_verts=self.num_verts,
            bad_sizes=self.bad_sizes,
        )
        return score

    def move_score(self, edge_change: tuple[tuple, int, int]) -> int:
        """
        Score change function.

        Returns:
            The change in the number of monochromatic "bad subgraphs"
            that would result from making the specified edge change to
            our edge-colored graph. Does *not* actually perform this
            change (i.e., the original graph is untouched).
        """
        if self.bad_subgraph == "books":
            move_score_func = count_books_change
        elif self.bad_subgraph == "wheels":
            move_score_func = count_wheels_change

        move_score = move_score_func(
            adj_matrix=self.adj_matrix,
            neighbors=self.neighbors,
            common_neighbors=self.common_neighbors,
            edge_change=edge_change,
            bad_sizes=self.bad_sizes,
        )
        return move_score

    def hash_after_move(self, edge_change: tuple[tuple, int, int]) -> int:
        """
        Computes updated graph hash from editing one edge.

        Args:
            edge_change: A tuple of the form
                (edge, new_color, old_color).

        Returns:
            The hash of the graph that would result from making the
            specified change to the current graph. Does *not* actually
            perform this change (i.e., the original graph is untouched).
        """
        edge = edge_change[0]
        new_color = edge_change[1]
        old_color = edge_change[2]

        # The hash of the graph is defined as the bitwise XOR of the
        # individual edge/color pairs, so it can be updated in this way.
        hash_after_move = (
            self.hash ^ hash((edge, old_color)) ^ hash((edge, new_color))
        )

        return hash_after_move

    def make_move(self, edge_change: tuple[tuple, int, int]) -> None:
        """
        Changes the color of one edge.

        Updates the adjacency matrix of the graph, as well as other
        auxillary data (lists of neighbors, the graph's hash, etc.).

        Args:
            edge_change: A tuple of the form
                (edge, new_color, old_color).

        Returns:
            None
        """
        edge = edge_change[0]
        new_color = edge_change[1]
        old_color = edge_change[2]

        # Make move -- remember to keep the adjacency matrix symmetric!
        self.adj_matrix[edge] = new_color
        self.adj_matrix[edge[::-1]] = new_color

        # Update possible moves -- the current color is now "new_color",
        # and we can now move to any *other* color.
        for color in [c for c in range(self.num_colors) if c != old_color]:
            self.valid_moves.remove((edge, color, old_color))
        for color in [c for c in range(self.num_colors) if c != new_color]:
            self.valid_moves.append((edge, color, new_color))

        self.hash = self.hash_after_move(edge_change)

        # Update "self.neighbors" and "self.common_neighbors".
        self.neighbor_update(edge, new_color, old_color)

    def neighbor_update(
        self, edge: tuple[int, int], new_color: int, old_color: int
    ) -> None:
        """
        Updates "neighbors" and "common_neighbors" after an edge change.

        Args:
            edge: A tuple of vertices (u,v).
            new_color: The new color of the edge (u,v).
            old_color: The former color of the edge (u,v).

        Returns:
            None
        """
        (u, v) = edge

        # Vertices u,v are no longer adjacent in old_color.
        self.neighbors[old_color, u].remove(v)  # type: ignore
        self.neighbors[old_color, v].remove(u)  # type: ignore

        # Prune common neighbors in old_color. This step is easiest to
        # understand if you draw a small sketch, and label vertices u,
        # v, and w.
        for w in self.neighbors[old_color, u]:
            self.common_neighbors[old_color, v, w].remove(u)  # type: ignore

        for w in self.neighbors[old_color, v]:
            self.common_neighbors[old_color, u, w].remove(v)  # type: ignore

        # Add common neighbors in new_color. Again, this is easiset to
        # understand by drawing a picture.
        for w in self.neighbors[new_color, u]:
            self.common_neighbors[new_color, v, w].add(u)  # type: ignore

        for w in self.neighbors[new_color, v]:
            self.common_neighbors[new_color, u, w].add(v)  # type: ignore

        # Vertices u,v are now adjacent in new_color.
        self.neighbors[new_color, u].add(v)  # type: ignore
        self.neighbors[new_color, v].add(u)  # type: ignore

    def save(self, **kwargs: dict[str, Any]) -> None:
        """
        Saves the adjacency matrix of the graph as a text file.

        Args:
            kwargs (optional): Any additional labeled parameters/
                information to be saved along with the graph
                (for example, problem or search parameters like
                "random_seed = 0").

        Returns:
            None
        """

        file_name = (
            "./final_adj_matrix_"
            + self.bad_subgraph
            + "_"
            + str(self.bad_sizes)
            + "_"
            + str(self.num_verts)
            + "vertices_"
            # Random number included in case multiple constructions are
            # found for the same problem parameters -- this way all the
            # constructions should be saved.
            + str(np.random.random())
            + ".txt"
        )
        try:
            with open(file_name, "x") as file:
                file.write(str(self) + "\n")

                for label, info in kwargs.items():
                    file.write(f"\n{label} = {info}")
        # Re-running the code with the same random seed will produce the
        # same construction multiple times. This ensures that the
        # construction will be successfully saved exactly once, but that
        # no error will be raised if we try to save it twice.
        except FileExistsError:
            pass

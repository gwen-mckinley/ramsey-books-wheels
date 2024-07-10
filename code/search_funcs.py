"""
Contains local search functions for Ramsey lower bound constructions.

Contains an implementation of tabu search, as well as a wrapper function
"climb_until_success" that can repeatedly run *any* local search
algorithm until a score of 0 is obtained, as well as a wrapper function
"parallel_search" to run multiple instances of "climb_until_success" in
parallel.

Authorship:
    This code was written by Gwen McKinley, in support of the paper
    "Small Ramsey numbers for books, wheels, and generalizations" by
    Bernard Lidický, Gwen McKinley, and Florian Pfender.
"""

import math
import multiprocessing
from typing import Callable

import numpy as np

from ramsey_class import RamseyGraph
from ramsey_funcs import rand_graph


def tabu_nolimit(
    graph: RamseyGraph,
    print_bests: bool = True,
    process_number: int | None = None,
) -> tuple[RamseyGraph, dict[str, int]]:
    """
    Tabu search with infinite tabu tenure and no restarts.

    Performs tabu search starting from a given graph, until a
    graph with score 0 is found. Has a few main features:

        - Infinite tabu tenure: we store a set with the hashes of *each*
            graph visited during the search, and never step to a graph
            whose hash appears in that set.
        - No restarts: we end the search only if a graph of score 0 is
            found, and never restart at a new graph.
        - Tiebreaking: when we have the option of stepping to multiple
            different graphs with the same score, we choose from among
            them uniformly at random.

    Args:
        graph: An edge-colored graph.
        print_bests: If True, prints the adjacency matrix of each graph
            attaining a new minimum score during the search.
        process_number: A number used to identify the search if multiple
            search instances are being run in parallel.

    Returns:
        A tuple containing:

        - graph (RamseyGraph): The final graph constructed/discovered
            by the tabu search.
        - info (dict): A dictionary auxillary information about the
            search. Has keys "steps" (the total number of steps taken by
            the tabu search to find the final construction), and "score"
            (the score of the final graph produced -- should always be
            0, since there are no restarts). If the optional argument
            "process_number" is used, this is also included.
    """
    visited = {graph.hash}
    current_score = graph.score()
    best_score = math.inf
    steps = 0

    while True:
        best_delta = math.inf
        best_moves = []
        # Check every possible move, rejecting any in the tabu set, and
        # making a list of the best-scoring moves.
        for move in graph.valid_moves:
            if graph.hash_after_move(move) in visited:
                continue
            else:
                delta = graph.move_score(move)
                if delta == best_delta:
                    best_moves.append(move)
                elif delta < best_delta:
                    best_delta = delta
                    best_moves = [move]

        # Choose the move with the best score, breaking ties randomly.
        move_index = np.random.randint(len(best_moves))
        move = best_moves[move_index]

        # Actually make the step: update tabu list, graph, etc.
        visited.add(graph.hash_after_move(move))
        graph.make_move(move)
        current_score += best_delta
        steps += 1

        if current_score < best_score:
            best_score = current_score
            if print_bests:
                # Keep the printouts clear and tidy if multiple
                # processes are running in parallel.
                if process_number is not None:
                    print(
                        f"\n(Search #{process_number}) New record "
                        f"score of {best_score} at step {steps} for this "
                        "graph:"
                    )
                else:
                    print(
                        f"\nNew record score of {best_score} at step {steps} "
                        "for this graph:"
                    )
            print(graph)

        if current_score == 0:
            info = {"steps": steps, "score": 0}

            if process_number is not None:
                print(f"\nSearch #{process_number} finished.", end="")
                info["process_number"] = process_number

            return graph, info


def search_until_success(
    one_search: Callable,
    build_graph_params: dict,
    search_params: dict,
    seed: int | None = None,
    save_final_graph: bool = False,
) -> RamseyGraph:
    """
    Runs local search until a graph with score 0 is obtained.

    This function takes *any* local search algorithm, and runs it
    repeatedly, re-starting from a random graph each time, until a
    graph of score 0 is achieved. Note: if it is used as a wrapper for
    "tabu_nolimit", it will actually only run one search, as
    "tabu_nolimit" terminates only if a graph of score 0 is found.
    However, this wrapper function gives more flexibility for trying
    out other local search methods that may get stuck at local minima.

    Args:
        one_search: A local search function (e.g. tabu search). Should
            return a graph and a dictionary "info" recording the graph's
            score and the number of steps taken to find it.
        build_graph_params: A dictionary of keyword arguments used to
            initialize the starting graph in the local search, an
            instance of the "RamseyGraph" class.
        search_params: A dictionary containing any parameters used by
            "one_search".
        seed: Optional random seed value.
        save_final_graph: If True, the adjacency matrix of the final
            graph constructed will be saved in a .txt file, along with
            some auxillary information (problem parameters, etc.).

    Returns:
        A graph with score 0.
    """

    if seed is not None:
        np.random.seed(seed)

    record_score = math.inf
    total_steps = 0

    # Note: if "tabu_nolimit" is used for "one_search", only one
    # iteration of this while loop will be run (as "tabu_nolimit" always
    # outputs a graph with score 0).
    while record_score > 0:
        # Start at a random graph, and run local search algorithm.
        graph = rand_graph(**build_graph_params)
        graph, info = one_search(graph=graph, **search_params)
        current_score = info["score"]
        total_steps += info["steps"]

        # Keep track of best-scoring constructions found.
        if current_score < record_score:
            record_score = current_score
            if current_score == 0:
                print("\nFinal graph:")
            else:
                print(
                    f"\nNew record score of {record_score} for this graph:\n"
                )
            print(graph)

    # Save final construction (with score 0) as a text file.
    if save_final_graph:
        graph.save(
            search_function_used=one_search.__name__,
            build_graph_params=build_graph_params,
            search_params=search_params,
            seed_for_search_until_success=seed,
            total_steps=total_steps,
        )

    return graph


def parallel_search(  # noqa: PLR0913
    num_threads: int,
    one_search: Callable,
    build_graph_params: dict,
    search_params: dict,
    seed: int | None = None,
    save_final_graph: bool = False,
) -> None:
    """
    Runs local search on multiple threads.

    This function parallelizes "search_until_success": it creates
    mutliple processes, and in each one, takes a local search algorithm,
    and runs it repeatedly, re-starting from a random graph each time,
    until a graph of score 0 is achieved. As in "search_until_success",
    if it is used as a wrapper for "tabu_nolimit", it will only run it
    once in each process, as "tabu_nolimit" terminates only if a graph
    of score 0 is found.

    Args:
        one_search: A local search function (e.g. tabu search). Should
            return a graph and a dictionary "info" recording the graph's
            score and the number of steps taken to find it.
        build_graph_params: A dictionary of keyword arguments used to
            initialize the starting graph in the local search, an
            instance of the "RamseyGraph" class.
        search_params: A dictionary containing any parameters used by
            "one_search".
        seed: Optional random seed value.
        save_final_graph: If True, the adjacency matrix of the final
            graph constructed by each process will be saved in a .txt
            file, along with some auxillary information (problem
            parameters, etc.).

    Returns:
        None.
    """
    # Generate "master seed" if no seed is specified by the user.
    if seed is None:
        seed = np.random.randint(2**31)

    np.random.seed(seed)
    # Generate a seed for each thread, starting from the "master seed".
    # It is not important for these seeds to be random per se, but an
    # unstructured choice here helps ensure that different values of the
    # "master seed" will generally give different seeds for each thread.
    process_seeds = [np.random.randint(2**31) for _ in range(num_threads)]

    processes = []

    for i in range(num_threads):
        # Label the processes to make printouts more clear and tidy.
        search_params["process_number"] = i
        processes.append(
            multiprocessing.Process(
                target=search_until_success,
                args=(
                    one_search,
                    build_graph_params,
                    dict(search_params),
                    process_seeds[i],
                    save_final_graph,
                ),
            )
        )

    for p in processes:
        p.start()

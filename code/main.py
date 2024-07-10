"""
Runs tabu search to find Ramsey lower bound constructions.

Uses tabu search to find an edge-colored graph avoiding monochromatic
copies of either "books" or "wheels." Problem parameters are set from
the command line. All constructions are given as adjacency matrices,
where the entries correspond to edge-colors (and always with 0s along
the diagonal).

Example:
    Enter the following on the command line to find the adjacency matrix
    of a 14-vertex graph with no 5-vertex wheels in color 0 and no
    7-vertex wheels in color 1:

        python main.py -n 14 -b wheels -k 5 7

To see a full list of optional parameters, print options, etc., enter
the following on the command line:

    python main.py --help


Authorship:
    This code was written by Gwen McKinley, in support of the paper
    "Small Ramsey numbers for books, wheels, and generalizations" by
    Bernard Lidický, Gwen McKinley, and Florian Pfender.
"""
import argparse
import sys

import ramsey_class
from search_funcs import parallel_search, search_until_success, tabu_nolimit

# Get problem parameters and optional arguments from command line.
parser = argparse.ArgumentParser(
    description="Use tabu search to find an edge-colored graph avoiding "
    "monochromatic copies of the specified subgraphs. \n\nExample:"
    "\n\tpython main.py -n 14 -b wheels -k 5 7\n\n"
    "This will find the adjacency matrix of a 14-vertex graph with no "
    "5-vertex wheels in color 0 and no 7-vertex wheels in color 1.",
    formatter_class=argparse.RawTextHelpFormatter,
)
parser.add_argument(
    "-n",
    "--num_vertices",
    type=int,
    required=True,
    help="The number of vertices in the edge-colored graph to be constructed.",
)
parser.add_argument(
    "-b",
    "--bad_subgraph",
    type=str,
    required=True,
    help='The "bad" monochromatic subgraphs. Can be "books" or "wheels".',
)
parser.add_argument(
    "-k",
    "--bad_sizes",
    type=int,
    nargs="+",
    required=True,
    help='The number of vertices in the "bad" monochromatic subgraphs for '
    'each color. E.g., if "4 5" is entered here, this forbids 4-vertex '
    "subgraphs in color 0 and 5-vertex subgraphs in color 1. Note: the "
    "book B_i has i+2 vertices, so for books, the previous example would "
    "exclude copies of B_2 in color 0 and copies of B_3 in color 1.",
)
parser.add_argument(
    "-p",
    "--num_parallel_threads",
    type=int,
    default=1,
    help="Number of searches to run in parallel (default = 1).",
)
parser.add_argument(
    "-r" "--random_seed", type=int, help="Optional random seed value."
)
parser.add_argument(
    "-q",
    "--quiet",
    action="store_true",
    help="Print only the final construction of the search, and not the "
    'intermediate "record values."',
)
parser.add_argument(
    "-s",
    "--save",
    action="store_true",
    help="Save final construction in a .txt file.",
)

try:
    args = parser.parse_args()
except SystemExit as err:
    # Display help message if there is an error parsing command line
    # arguments (generally if arguments are missing or entered
    # incorrectly.)
    if err.code != 0:
        print("\n\n----------- Help text ------------")
        parser.print_help()
    sys.exit(0)

# Set parameters for tabu search.
build_graph_params = {
    "num_verts": args.num_vertices,
    "bad_sizes": args.bad_sizes,
    "bad_subgraph": args.bad_subgraph,
    "num_colors": len(args.bad_sizes),
    "graph_class": ramsey_class.RamseyGraph,
}
tabu_params = {
    "print_bests": not args.quiet,
}

# Run tabu search.
if args.num_parallel_threads == 1:
    search_until_success(
        one_search=tabu_nolimit,
        build_graph_params=build_graph_params,
        search_params=tabu_params,
        seed=args.r__random_seed,
        save_final_graph=args.save,
    )
else:
    parallel_search(
        num_threads=args.num_parallel_threads,
        one_search=tabu_nolimit,
        build_graph_params=build_graph_params,
        search_params=tabu_params,
        seed=args.r__random_seed,
        save_final_graph=args.save,
    )

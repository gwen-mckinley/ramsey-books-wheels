# About this repository
This repository contains code supporting the paper "Small Ramsey numbers for books, wheels, and generalizations" by Bernard Lidický, Gwen McKinley, and Florian Pfender. This code was used to find the lower bound constructions in the paper for *books* and *wheels*. For code related to the upper bounds, see [https://lidicky.name/pub/gr/](https://lidicky.name/pub/gr/).

Copyright (c) 2024 Gweneth McKinley. This code is released under a Creative Commons Attribution 4.0 license.

## Contents:

* Python code used to find Ramsey lower bound constructions for *books* and *wheels* via tabu search. 
* Constructions from the paper, along the number of steps taken by tabu search to find them, and the random seeds used.
* Examples showing how to verify the constructions using [SageMath](https://www.sagemath.org/).

## Usage:

To run the tabu search, download all the files in the "code" folder to a directory, and from that directory, enter the following command:

```
python main.py -n <num_vertices> -b <bad_subgraph> -k <bad_sizes> 
```

For example, to find the adjacency matrix of a 14-vertex graph with no 5-vertex wheels in color 0 and no 7-vertex wheels in color 1, enter the command:

```
python main.py -n 14 -b wheels -k 5 7
```

**Important note:** the parameter ``k`` always refers to the number of *vertices* in the "forbidden subgraph." The wheel $W_k$ has $k$ vertices, but the book $`B_k`$ has $`k+2`$ vertices. So for example, to find an 18-vertex graph with no $`B_4`$ in color 0 and no $`B_5`$ in in color 1, we would enter:

```
python main.py -n 18 -b books -k 6 7
```

For a full list of options (parallel search, random seed, saving the final construction to a file), type:

```
python main.py --help
```

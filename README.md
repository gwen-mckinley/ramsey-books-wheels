# About this repository
This repository contains code supporting the paper "Small Ramsey numbers for books, wheels, and generalizations" by Bernard Lidický, Gwen McKinley, Florian Pfender, and Steven Van Overberghe. This code was used to find lower bound constructions in the paper for *books* and *wheels*, as well as some upper bounds via "bottom-up generation". For code related to the upper bounds found with flag algebras, see [https://lidicky.name/pub/gr/](https://lidicky.name/pub/gr/).

**Link to paper:** https://arxiv.org/abs/2407.07285

Copyright (c) 2024 Gweneth McKinley. This code is released under a Creative Commons Attribution 4.0 license.

## Contents:

`bottom-up`

* Plugin for `geng` that was used to generate all (B2,B8)-graphs.
* A list of all extremal (W5,W9)-graphs.
* Lists of all (W5,W7)-graphs for every order, in graph6 format.

`polycirculant`
    
* Lower bound constructions coming from polycirculant graphs, specified in graph6 format. For more information on this graph encoding, see: https://users.cecs.anu.edu.au/~bdm/data/formats.html

`tabu`

* Python code used to find Ramsey lower bound constructions for *books* and *wheels* via tabu search. 
* Constructions found using tabu search, along the number of steps taken to find them, and the random seeds used.
* Examples showing how to verify the constructions using [SageMath](https://www.sagemath.org/).

## Usage:

To run the tabu search, download all the files in the "code" folder to a directory, and from that directory, enter the following command:

```
python main.py -n <num_vertices> -b <bad_subgraph> -k <bad_sizes> 
```

For example, to find the adjacency matrix of a 17-vertex graph with no 5-vertex wheels in color 0 and no 9-vertex wheels in color 1, enter the command:

```
python main.py -n 17 -b wheels -k 5 9
```

**Important note:** the parameter ``k`` always refers to the number of *vertices* in the "forbidden subgraph." The wheel $W_k$ has $k$ vertices, but the book $B_k$ has $k+2$ vertices. So for example, to find a 20-vertex graph with no $B_2$ in color 0 and no $B_8$ in in color 1, we would enter:

```
python main.py -n 20 -b books -k 4 10
```

For a full list of options (parallel search, random seed, saving the final construction to a file), type:

```
python main.py --help
```

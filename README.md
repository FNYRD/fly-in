*This project has been created as part of the 42 curriculum by jericard.*

# Fly-in

## Description

Fly-in is a drone routing simulator. Given a map that describes a set of
connected zones (a graph) and a number of drones that all start at the same
hub, the program computes how to move every drone to the destination hub in as
few simulation turns as possible, while respecting the movement and capacity
rules of the map.

Each zone has a type that affects how expensive it is to enter, a maximum
number of drones it can hold at once, and each connection has its own capacity
limit. Drones move simultaneously, one step per turn, and may wait when a move
is not possible. The simulation advances turn by turn until every drone has
reached the destination, printing the movements of each turn.

The project is written in pure Python, is fully object-oriented, uses no
external graph libraries, and complies with `flake8` and `mypy --strict`.

## Instructions

This project uses a `Makefile` that manages a local virtual environment
(`.fly_in`) and all dependencies.

### Requirements

- Python 3
- The dependencies listed in `requirements.txt` (installed automatically by
  `make install`): `pygame`, `flake8`, `mypy`, `pytest`, `build`.

### Installation

```sh
make install
```

Creates the `.fly_in` virtual environment and installs every dependency into
it.

### Running

```sh
make run
```

Launches the program. A menu asks whether to run the **terminal** simulation
(`1`) or the **pygame** visualization (`2`). You are then prompted to choose a
difficulty level and a map from the `maps/` directory.

### Other Makefile rules

| Rule               | Description                                           |
| ------------------ | ----------------------------------------------------- |
| `make test`        | Run the test suite with `pytest`.                     |
| `make lint`        | Run `flake8` and `mypy` with the subject's flags.     |
| `make lint-strict` | Run `flake8` and `mypy --strict`.                     |
| `make debug`       | Run the program under `pdb`.                          |
| `make clean`       | Remove `__pycache__`, `.mypy_cache` and other caches. |

## Resources

### References

- [Dijkstra's Shortest Path Algorithm — GeeksforGeeks](https://www.geeksforgeeks.org/dsa/dijkstras-shortest-path-algorithm-greedy-algo-7/)
- [Algoritmo de la ruta más corta de Dijkstra: introducción gráfica — freeCodeCamp](https://www.freecodecamp.org/espanol/news/algoritmo-de-la-ruta-mas-corta-de-dijkstra-introduccion-grafica/)
- [Dijkstra's Algorithm (video)](https://www.youtube.com/watch?v=_B5cx-WD5EA)
- [Dijkstra's Algorithm (video)](https://www.youtube.com/watch?v=EFg3u_E6eHU)
- [Introduction to Pygame — GeeksforGeeks](https://www.geeksforgeeks.org/python/introduction-to-pygame/)

### Use of AI

AI was used as a tutor and reviewer, not as a code generator. All the project
code and pseudocode was written by the student; the AI's role was to validate
the reasoning behind each design decision, resolve conceptual blockers, and
keep the work on track.

Concretely, AI was used for:

- **Design discussion:** validating the class structure (graph model, parser,
  pathfinding, simulation) and the turn-aware adaptation of Dijkstra before any
  code was written.
- **Debugging and review:** reviewing the student's code statically to catch
  type errors, edge cases, and logic bugs (for example, the circular-import
  issue and the per-turn reservation bookkeeping).
- **Tests:** generating the `pytest` test code from cases defined together with
  the student.
- **Documentation:** helping draft the docstrings and this README.

## Algorithm

The core problem is routing many drones through a shared graph without
exceeding zone or connection capacities, while minimizing the number of turns.
The solution combines a **turn-aware Dijkstra** for pathfinding with a
**sequential reservation system** in the simulation.

### Graph model

The map is represented with three classes:

- `Zone` — a node with coordinates, a type (`normal`, `priority`, `restricted`,
  `blocked`), a color, and a `max_drones` capacity.
- `Connection` — a bidirectional edge between two zones with its own
  `max_link_capacity`.
- `Graph` — holds every zone and connection.

No external graph library is used; the graph is traversed directly through each
zone's list of connections.

### Turn-aware Dijkstra

A classic shortest-path search finds *a* route, but it ignores the fact that
zones and connections fill up over time. To handle this, the search state is
not just a zone but the pair **`(zone, turn)`**, where the turn equals the
accumulated cost of reaching that zone. This lets the algorithm reason about
*where a drone is at each specific turn*, which is exactly what capacity
constraints depend on.

Key ideas:

- **Movement cost = turns.** Entering a `normal` or `priority` zone costs 1
  turn; a `restricted` zone costs 2 (the drone occupies the connection during
  the transit and must arrive the next turn); `blocked` zones are never
  expanded.
- **Priority zones** are preferred by a `penalty` tie-breaker: among states with
  the same cost, priority zones are explored first, so an equal-cost route
  through a priority zone wins.
- **Capacity awareness.** Before expanding a neighbor, the search consults a
  `reservations` table (`reservations[turn][name] = count`) that records how
  many drones already occupy each zone and connection at each turn. If the
  target would exceed its capacity at that turn, the move is rejected. The start
  and end hubs are exempt (all drones share them).
- **Waiting.** If every neighbor of a state is blocked or full, the search adds
  a *wait edge* `(zone, T) → (zone, T+1)`, keeping the drone in place for one
  turn instead of letting the state die. A wait is represented in the path by
  repeating the same zone.
- **Move budget.** To guarantee termination on impossible maps, the search
  tracks a budget of moves beyond the last reserved turn; if it is exhausted
  without reaching the end, the destination is reported as unreachable.

The result is a path (`List[Zone | Connection]`) from start to end, with the
transit `Connection` inserted for each restricted segment.

### Simulation and reservations

Routing and execution are two separate phases. **Planning** (pathfinding) is
done one drone at a time, before the simulation runs — no drone moves during
this phase, paths are just computed. **Execution** is the turn-by-turn
simulation that produces the output, where all drones advance **simultaneously**:
each printed turn shows the position of every active drone at that same turn.

Sequential planning is exactly what makes conflict-free simultaneous execution
possible: because each drone is planned knowing where the others will be at
every turn (the `(zone, turn)` state), the routes are already coordinated, so
when they run at the same time none collide or exceed capacity.

Drones are routed **one at a time**, in order (`D1, D2, …`):

- `D1` is routed against an empty reservation table (it sees a free map).
- Each subsequent drone is routed against the accumulated reservations of all
  previously routed drones, so it naturally spreads onto alternative paths and
  waits when needed to avoid conflicts and deadlocks.

After a drone's path is computed, the simulation walks it turn by turn and adds
its occupancy to the shared `reservations` table. A drone reserves a zone only
for the turns its path places it there: the turn it leaves a zone, it no longer
counts against that zone's capacity — this implements the subject's rule that
*"drones moving out free up capacity for that same turn."*

Finally, the simulation builds a per-turn log and prints one line per turn, with
each drone's movement (`D<ID>-<zone>` or `D<ID>-<connection>` for a restricted
transit), omitting drones that wait or have already arrived.

## Visual Representation

Beyond the terminal output, the project includes a **pygame** visualization
(`view.py`) that plays back the simulation graphically and makes the routing
decisions easy to follow.

Features:

- **Map selection menus.** On launch, the user picks a difficulty level and a
  map (scanned dynamically from `maps/`), then a playback mode.
- **Playback modes.** *Manual* — step through turns with the left/right arrow
  keys; *automatic* — turns advance on their own (0.5 s each). `ESC` returns to
  the menu.
- **Adaptive layout.** Map coordinates are scaled to pixels dynamically: the
  window size, zone radius and margins adjust to the map's coordinate range so
  every map, small or large, fits on screen.
- **Zones and connections.** Zones are drawn as colored circles (using the
  map's color metadata, or gray by default) labelled with their name;
  connections are lines between them.
- **Drones.** Each drone is drawn as a quadcopter (four rotors, arms and body)
  in its own color, labelled with its ID. Its position per turn is the zone
  center, or the midpoint of a connection while in transit through a restricted
  zone.
- **Turn indicator.** The current turn number and map name are shown on screen.

How it enhances the user experience: the graphical playback turns the abstract
per-turn text log into something the reviewer can *watch* — drones spreading
across parallel paths, waiting when a zone is full, and pausing mid-connection
during restricted transits — which makes the algorithm's behavior far easier to
understand and verify than reading movement lines alone.

## Example input and expected output

A map file lists the number of drones, the hubs (with coordinates and optional
metadata), and the connections between them. For example,
`maps/easy/01_linear_path.txt`:

```
# Easy Level 1: Simple linear path
nb_drones: 2

start_hub: start 0 0 [color=green]
hub: waypoint1 1 0 [color=blue]
hub: waypoint2 2 0 [color=blue]
end_hub: goal 3 0 [color=red]

connection: start-waypoint1
connection: waypoint1-waypoint2
connection: waypoint2-goal
```

Running the terminal simulation on this map produces one line per turn, listing
each drone that moves (`D<ID>-<zone>`), until every drone reaches the goal:

```
Total turns 4

D1-waypoint1
D1-waypoint2 D2-waypoint1
D1-goal D2-waypoint2
D2-goal
```

The two drones start together at `start`; `D2` stays one turn behind `D1`
because each zone holds only one drone at a time (the default capacity), so it
waits at `start` for the first turn instead of colliding.

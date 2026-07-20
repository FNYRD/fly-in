import os
from typing import List, Dict
import pytest

from parser import Parser
from graph import Graph
from zone import Zone
from connection import Connection
from drone import Drone
from simulation import Simulation

TEST_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture
def simulation() -> Simulation:
    folder: str = "extra"
    blocked: str = "for_blocked_tests.txt"
    normal: str = "for_normla_tests.txt"
    map_: str = normal
    sim: Simulation
    graph: Graph
    drones: List[Drone]
    route: str = ""
    route = os.path.join(TEST_DIR, "..", "maps", folder,
                            map_)
    graph, drones = Parser(route).manufacturing()
    sim = Simulation(graph, drones)
    sim.simulating()
    return sim


def test_capacity_respected(simulation: Simulation) -> None:
    """This test checks if at an especific turn the whole drone's
    loaded in an especific zone or connection don't exceeds the its capacity"""
    sim = simulation
    zone_limits: Dict[str, int] = {
        z.name: z.max_drones for z in sim.graph.zones.values()
    }
    conn_limits: Dict[str, int] = {
        c.name: c.max_link_capacity for c in sim.graph.connections
    }
    max_turns = max(len(d.path) for d in sim.drones)
    for turn in range(0, max_turns):
        zone_count: Dict[str, int] = {}
        conn_count: Dict[str, int] = {}
        for drone in sim.drones:
            if turn >= len(drone.path):
                continue
            pos = drone.path[turn]
            if turn != 0 and (isinstance(pos, Zone) and
                              isinstance(drone.path[turn - 1], Zone)
                              ):
                if drone.path[turn] != drone.path[turn - 1]:
                    conn = pos.get_connection(drone.path[turn - 1])
                    if conn is not None:
                        conn_count[conn.name] = (
                            conn_count.get(conn.name, 0) + 1)                    
            if isinstance(pos, Zone):
                zone_count[pos.name] = (
                    zone_count.get(pos.name, 0) + 1)
            elif isinstance(pos, Connection):
                conn_count[pos.name] = (
                    conn_count.get(pos.name, 0) + 1)
        for name, count in zone_count.items():
            if name in zone_limits and sim.graph.zones[name].relevant:
                assert count >= zone_limits[name], (f"T{turn}: start or goal zone"
                                                    "cannot handle multiple drones at the same time!"
                                                    )
                continue
            if name in zone_limits:
                assert count <= zone_limits[name], (
                    f"T{turn}: zone '{name}' has {count} drones, "
                    f"max is {zone_limits[name]}")
        for name, count in conn_count.items():
            if name in conn_limits:
                assert count <= conn_limits[name], (
                    f"T{turn}: connection '{name}' has {count} "
                    f"drones, max is {conn_limits[name]}")


def test_all_drones_reach_end(simulation: Simulation) -> None:
    """This test will traverse the drone's path and varify
    if their last zone in its path it's the end zone """
    sim = simulation
    for drone in sim.drones:
        last = drone.path[-1]
        assert isinstance(last, Zone), (
            f"{drone.id}: last position is a Connection, "
            f"not a Zone")
        assert last.relevant == "end_hub", (
            f"{drone.id}: ended at '{last.name}', "
            f"not at end_hub")


def test_paths_are_valid(simulation: Simulation) -> None:
    """This function tests that two continuous zones have a real
    connection between them and that when a drone stays at a connetion
    it's because the next zone is type restricted"""
    sim = simulation
    for drone in sim.drones:
        for i in range(1, len(drone.path)):
            prev = drone.path[i - 1]
            current = drone.path[i]
            if prev == current:
                continue
            if isinstance(prev, Zone) and isinstance(current, Zone):
                conn = prev.get_connection(current)
                assert conn is not None, (
                    f"{drone.id} T{i}: no connection between "
                    f"'{prev.name}' and '{current.name}'")
            elif (isinstance(prev, Zone)
                  and isinstance(current, Connection)):
                other = current.get_otherside_zone(prev)
                assert other is not None and other.zone_type == "restricted", (
                    f"{drone.id} T{i}: '{prev.name}' is not part "
                    f"of connection '{current.name} or wrong restricted zone {other.zone_type if isinstance(other, Zone) else 'Error verifying zone'}'")
            elif (isinstance(prev, Connection)
                  and isinstance(current, Zone)):
                other = prev.get_otherside_zone(current)
                assert other is not None and current.zone_type == "restricted", (
                    f"{drone.id} T{i}: '{current.name}' is not "
                    f"part of connection '{prev.name} or wrong restricted zone {current.zone_type}'")
            else:
                pytest.fail(
                    f"{drone.id} T{i}: two consecutive "
                    f"Connections in path")



# ============================================================
# Movement costs
# ============================================================

def _link(graph: Graph, zone1: Zone, zone2: Zone) -> Connection:
    """Build a connection and register it in the graph and both zones."""
    conn = Connection(zone1, zone2)
    graph.add_connection(conn)
    zone1.add_connection(conn)
    zone2.add_connection(conn)
    return conn


def _run_graph(graph: Graph, n_drones: int = 1) -> Simulation:
    """Run a simulation over a hand built graph."""
    drones = [Drone(f"D{i}") for i in range(1, n_drones + 1)]
    sim = Simulation(graph, drones)
    sim.simulating()
    return sim


def test_movement_cost_normal() -> None:
    """A normal zone costs 1 turn: start and end are adjacent in
    the path, with no connection in between."""
    graph = Graph()
    start = Zone("start", 0, 0, relevant="start_hub")
    end = Zone("end", 1, 0, relevant="end_hub")
    for zone in (start, end):
        graph.add_zone(zone)
    _link(graph, start, end)

    path = _run_graph(graph).drones[0].path
    assert len(path) == 2, (
        f"normal zone: path has {len(path)} steps, expected 2")
    assert path == [start, end], (
        f"normal zone: unexpected path {[p.name for p in path]}")


def test_movement_cost_restricted() -> None:
    """A restricted zone costs 2 turns: the connection is inserted
    in the path as the transit turn before arriving."""
    graph = Graph()
    start = Zone("start", 0, 0, relevant="start_hub")
    middle = Zone("middle", 1, 0, zone_type="restricted")
    end = Zone("end", 2, 0, relevant="end_hub")
    for zone in (start, middle, end):
        graph.add_zone(zone)
    conn = _link(graph, start, middle)
    _link(graph, middle, end)

    path = _run_graph(graph).drones[0].path
    assert len(path) == 4, (
        f"restricted zone: path has {len(path)} steps, expected 4 "
        f"(start, transit, restricted, end)")
    assert path == [start, conn, middle, end], (
        f"restricted zone: unexpected path {[p.name for p in path]}")


def test_movement_cost_priority_preferred() -> None:
    """Both routes cost the same, so the tie break must send the
    drone through the priority zone."""
    graph = Graph()
    start = Zone("start", 0, 0, relevant="start_hub")
    fast = Zone("fast", 1, 1, zone_type="priority")
    slow = Zone("slow", 1, -1)
    end = Zone("end", 2, 0, relevant="end_hub")
    for zone in (start, fast, slow, end):
        graph.add_zone(zone)
    _link(graph, start, fast)
    _link(graph, start, slow)
    _link(graph, fast, end)
    _link(graph, slow, end)

    path = _run_graph(graph).drones[0].path
    assert len(path) == 3, (
        f"priority zone: path has {len(path)} steps, expected 3")
    assert path[1] == fast, (
        f"priority zone: drone went through '{path[1].name}', "
        f"expected the priority zone 'fast'")


def test_movement_cost_blocked_is_unreachable() -> None:
    """A blocked zone is inaccessible: if it is the only route to
    the end, the algorithm reports the end as unreachable."""
    graph = Graph()
    start = Zone("start", 0, 0, relevant="start_hub")
    wall = Zone("wall", 1, 0, zone_type="blocked")
    end = Zone("end", 2, 0, relevant="end_hub")
    for zone in (start, wall, end):
        graph.add_zone(zone)
    _link(graph, start, wall)
    _link(graph, wall, end)

    with pytest.raises(ValueError):
        _run_graph(graph)


# ============================================================
# Connection capacity
# ============================================================

def test_connection_capacity() -> None:
    """A connection with max_link_capacity 3 lets three drones
    traverse it at the same turn, so none of them has to wait and
    all three share the very same path."""
    graph = Graph()
    start = Zone("start", 0, 0, relevant="start_hub")
    end = Zone("end", 1, 0, relevant="end_hub")
    for zone in (start, end):
        graph.add_zone(zone)
    conn = Connection(start, end, max_link_capacity=3)
    graph.add_connection(conn)
    start.add_connection(conn)
    end.add_connection(conn)

    sim = _run_graph(graph, 3)
    for drone in sim.drones:
        assert drone.path == [start, end], (
            f"{drone.id}: expected a direct move with no waiting, "
            f"got {[p.name for p in drone.path]}")


# ============================================================
# Output format
# ============================================================

def test_output_format() -> None:
    """On a linear map with default capacity 1 the three drones are
    forced to queue. Each output line must name every drone at most
    once, a waiting drone must be omitted instead of repeated from
    the previous line, and D3 must be the last one to arrive."""
    graph = Graph()
    start = Zone("start", 0, 0, relevant="start_hub")
    middle = Zone("middle", 1, 0)
    end = Zone("end", 2, 0, relevant="end_hub")
    for zone in (start, middle, end):
        graph.add_zone(zone)
    _link(graph, start, middle)
    _link(graph, middle, end)

    logs = _run_graph(graph, 3).logs
    for turn, line in enumerate(logs):
        ids = [entry.split("-")[0] for entry in line]
        assert len(ids) == len(set(ids)), (
            f"T{turn}: a drone is printed more than once in {line}")
    for turn in range(1, len(logs)):
        repeated = set(logs[turn]) & set(logs[turn - 1])
        assert not repeated, (
            f"T{turn}: {repeated} already appeared on the previous "
            f"line, a waiting drone must be omitted")
    assert logs[-1] == ["D3-end"], (
        f"the last line should be D3 arriving alone, got {logs[-1]}")


# ============================================================
# Benchmark tests
# ============================================================

def _run_map(folder: str, filename: str) -> Simulation:
    route = os.path.join(TEST_DIR, "..", "maps", folder, filename)
    graph, drones = Parser(route).manufacturing()
    sim = Simulation(graph, drones)
    sim.simulating()
    return sim


# Easy — < 10 turns
def test_benchmark_linear_path() -> None:
    sim = _run_map("easy", "01_linear_path.txt")
    assert len(sim.logs) <= 6, (
        f"linear_path: {len(sim.logs)} turns, target <= 6")


def test_benchmark_simple_fork() -> None:
    sim = _run_map("easy", "02_simple_fork.txt")
    assert len(sim.logs) <= 8, (
        f"simple_fork: {len(sim.logs)} turns, target <= 8")


def test_benchmark_basic_capacity() -> None:
    sim = _run_map("easy", "03_basic_capacity.txt")
    assert len(sim.logs) <= 6, (
        f"basic_capacity: {len(sim.logs)} turns, target <= 6")


# Medium — 10-30 turns
def test_benchmark_dead_end_trap() -> None:
    sim = _run_map("medium", "01_dead_end_trap.txt")
    assert len(sim.logs) <= 12, (
        f"dead_end_trap: {len(sim.logs)} turns, target <= 12")


def test_benchmark_circular_loop() -> None:
    sim = _run_map("medium", "02_circular_loop.txt")
    assert len(sim.logs) <= 15, (
        f"circular_loop: {len(sim.logs)} turns, target <= 15")


def test_benchmark_priority_puzzle() -> None:
    sim = _run_map("medium", "03_priority_puzzle.txt")
    assert len(sim.logs) <= 12, (
        f"priority_puzzle: {len(sim.logs)} turns, target <= 12")


# Hard — < 60 turns
def test_benchmark_maze_nightmare() -> None:
    sim = _run_map("hard", "01_maze_nightmare.txt")
    assert len(sim.logs) <= 30, (
        f"maze_nightmare: {len(sim.logs)} turns, target <= 30")


def test_benchmark_capacity_hell() -> None:
    sim = _run_map("hard", "02_capacity_hell.txt")
    assert len(sim.logs) <= 35, (
        f"capacity_hell: {len(sim.logs)} turns, target <= 35")


def test_benchmark_ultimate_challenge() -> None:
    sim = _run_map("hard", "03_ultimate_challenge.txt")
    assert len(sim.logs) <= 45, (
        f"ultimate_challenge: {len(sim.logs)} turns, target <= 45")


# Challenger (bonus)
def test_benchmark_impossible_dream() -> None:
    sim = _run_map("challenger", "01_the_impossible_dream.txt")
    assert len(sim.logs) < 45, (
        f"impossible_dream: {len(sim.logs)} turns, target < 45")

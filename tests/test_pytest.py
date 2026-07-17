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
    map_: str = "for_blocked_tests.txt"
    try:
        route = os.path.join(TEST_DIR, "..", "maps", folder,
                            map_)
        graph, drones = Parser(route).manufacturing()
        sim = Simulation(graph, drones)
        sim.simulating()
        return sim
    except (ValueError, FileNotFoundError, RuntimeError) as e:
        print(f"Error: {e}")
    except FileNotFoundError:
        print("File route doesn't exits")


def test_capacity_respected(simulation: Simulation) -> None:
    """This test checks if at an especific turn the whole drone's
    load in an especific zone or connection don't exceeds the its capacity"""
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

def test_no_blocked_zones(simulation: Simulation) -> None:
    """This test checks that blocked zones aren't inaccessibles
    cases when the only path to reach the end vertex it's a
    blocked zone, the algorithm will raise and unreachable end
    node using ValueError"""
    sim = simulation
    for drone in sim.drones:
        for i, pos in enumerate(drone.path):
            if isinstance(pos, Zone):
                assert pos.zone_type != "blocked", (
                    f"{drone.id} T{i}: is in blocked zone "
                    f"'{pos.name}'")

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

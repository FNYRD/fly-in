import os
from typing import List

import pytest

from clases.parser.parser import Parser
from clases.graph.graph import Graph
from clases.drone.drone import Drone
from clases.simulation.simulation import Simulation

TEST_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture
def simulation() -> Simulation:
    route = os.path.join(TEST_DIR, "maps/easy", "01_linear_path.txt")
    drones: List[Drone] = []
    graph: Graph
    graph, drones = Parser(route).manufacturing()
    sim = Simulation(graph, drones)
    sim.simulating()
    return sim


def test_all_drones_reach_end(simulation: Simulation) -> None:
    assert len(simulation.logs) > 0

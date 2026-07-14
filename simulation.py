from connection import Connection
from zone import Zone
from drone import Drone
from graph import Graph
from dijkstra import Dijkstra
from typing import Dict, List, Union, Optional


class Simulation:
    def __init__(self, graph: Graph, drones: List[Drone]) -> None:
        self.graph: Graph = graph
        self.drones: List[Drone] = drones
        self.reservations: Union[Dict[int, Dict[str, int]], None] = {}
        self.start: Union[Zone, None] = next(
            (start for start in self.graph.zones.values()
             if start.relevant == "start_hub"), None)
        self.end: Union[Zone, None] = next(
            (start for start in self.graph.zones.values()
             if start.relevant == "end_hub"), None)
        self.logs: List[List[str]] = []

    def calculating_reservations(self,
                                 path: List[Union[Zone, Connection]]) -> None:
        n_reserves: int = 0
        connection_name: Optional[Connection]
        current: Union[Zone, Connection]
        prev: Union[Zone, Connection]
        for i in range(1, len(path)):
            if self.reservations is not None:
                n_reserves = self.reservations.get(
                    (i), {}).get(path[i].name, 0)
                if n_reserves == 0 and i not in self.reservations:
                    self.reservations[i] = {path[i].name: 1}
                elif n_reserves == 0 and i in self.reservations:
                    self.reservations[i][path[i].name] = 1
                else:
                    self.reservations[i][path[i].name] += 1
                current = path[i]
                prev = path[i - 1]
                if current != prev:
                    if (isinstance(current, Zone)
                            and current.zone_type != "restricted"):
                        if isinstance(prev, Zone):
                            connection_name = prev.get_connection(current)
                            if connection_name is not None:
                                n_reserves = (
                                    self.reservations.get(
                                        (i), {}).get(connection_name.name, 0))
                                if (n_reserves == 0
                                        and i not in self.reservations):
                                    self.reservations[i] = {
                                        connection_name.name: 1}
                                elif (n_reserves == 0
                                      and i in self.reservations):
                                    (self.reservations[i]
                                     [connection_name.name]) = 1
                                else:
                                    (self.reservations[i]
                                     [connection_name.name]) += 1
                            else:
                                raise RuntimeError(
                                    "The order calculated by dijkstra() "
                                    "is wrong. Two consecutives zones without "
                                    "connection")

    def populate_logs(self, drone: Drone,
                      path: List[Union[Zone, Connection]]) -> None:
        entry: str = ""
        for i in range(1, len(path)):
            if path[i - 1] == path[i]:
                continue
            entry = drone.id + "-" + drone.path[i].name
            if i > len(self.logs):
                self.logs.append([entry])
            else:
                self.logs[i - 1].append(entry)

    def simulating(self) -> None:
        path: List[Union[Zone, Connection]] = []
        if self.start and self.end:
            path = Dijkstra(self.graph, self.start, self.end).dijkstra()
            self.calculating_reservations(path)
            self.drones[0].add_path(path)
            self.populate_logs(self.drones[0], path)
            for drone in self.drones:
                if drone.id == "D1":
                    continue
                path = Dijkstra(self.graph, self.start,
                                self.end, self.reservations).dijkstra()
                drone.add_path(path)
                drone.add_reservation(self.reservations)
                self.calculating_reservations(path)
                self.populate_logs(drone, path)

    def output(self) -> None:
        for logs in self.logs:
            for log in logs:
                print(log, end=" ")
            print()

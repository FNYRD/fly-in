from clases.graph.zone import Zone
from clases.graph.graph import Graph
from clases.graph.connection import Connection
from typing import Dict, Union, List, Set, Tuple
import heapq


class Dijkstra:
    def __init__(self, graph: Graph, start: Zone, end: Zone,
                 reservations: Union[Dict[int, Dict[str, int]], None] = None) -> None:
        self.graph: Graph = graph
        self.start: Zone = start
        self.end: Zone = end
        self.reservations: Union[Dict[int,
                                      Dict[str, int]], None] = reservations

    def rebuild(self, after: Tuple[Zone, int],
                previous: Dict[Tuple[Zone, int],
                               Tuple[Zone, int]]) -> List[Union[Zone, Connection]]:
        path: List[Union[Zone, Connection]] = []
        unpacked_after: Union[Zone, Connection]
        unpacked_before: Union[Zone, Connection]
        unpacked_after, _ = after
        path.append(unpacked_after)
        before: Union[Tuple[Zone, int], None] = None
        while 1:
            unpacked_after, _ = after
            before = previous.get(after)
            if before:
                unpacked_before, _ = before
                if unpacked_after.zone_type == "restricted":
                    for conn in unpacked_after.connections:
                        if conn.get_otherside_zone(unpacked_after) == unpacked_before:
                            path.append(conn)
                            break
                path.append(unpacked_before)
                if unpacked_before == self.start:
                    break
                after = before
        path.reverse()
        return path

    @staticmethod
    def penalty(zone: Zone) -> int:
        if zone.zone_type == "priority":
            return 0
        return 1

    @staticmethod
    def real_cost(zone: Zone) -> int:
        if zone.zone_type in ["normal", "priority"]:
            return 1
        return 2

    def dijkstra(self) -> List[Union[Zone, Connection]]:
        poped: Zone = Zone("none", 0, 0)
        poped_tuple: Tuple[int, int, Zone]
        neighbor: Union[Zone, None] = None
        cost: int = 0
        accumulated_cost: int = 0
        distances: Dict[Tuple[Zone, int], int] = {}
        previous: Dict[Tuple[Zone, int], Tuple[Zone, int]] = {}
        visited: Set[Tuple[Zone, int]] = set()
        priority: List[Tuple[int, int, Zone]] = []

        heapq.heappush(priority, (0, self.penalty(self.start), self.start))
        distances[self.start, 0] = 0

        while priority:
            poped_tuple = heapq.heappop(priority)
            cost, _, poped = poped_tuple
            if (poped, cost) in visited:
                continue
            visited.add((poped, cost))
            for conn in poped.connections:
                neighbor = conn.get_otherside_zone(poped)
                if not neighbor or neighbor.zone_type == "blocked":
                    continue
                accumulated_cost = cost + self.real_cost(neighbor)
                if (self.reservations and not neighbor.relevant and
                    (self.reservations.get(accumulated_cost, {}).get(neighbor.name, 0) + 1 >
                     neighbor.max_drones)):
                    continue
                if (self.reservations and
                    (self.reservations.get((accumulated_cost - 1
                                            if neighbor.zone_type == "restricted"
                                            else accumulated_cost),
                                           {}).get(conn.name, 0) + 1 >
                        conn.max_link_capacity)):
                    continue
                if (neighbor, accumulated_cost) not in distances:
                    distances[(neighbor, accumulated_cost)] = accumulated_cost
                    heapq.heappush(
                        priority, ((accumulated_cost),
                                   self.penalty(neighbor), neighbor))
                    previous[(neighbor, accumulated_cost)] = (poped, cost)
            if poped == self.end:
                break

        if poped != self.end:
            raise ValueError("Unreacheble end node")
        return self.rebuild((poped, cost), previous)

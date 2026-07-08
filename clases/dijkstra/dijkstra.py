from clases.graph.zone import Zone
from clases.graph.graph import Graph
from clases.graph.connection import Connection
from typing import Dict, Union, List, Set, Tuple
import heapq


class Dijkstra:
    def __init__(self, graph: Graph, start: Zone, end: Zone,
                 reservations: Union[Dict[int, Dict[str, int]],
                                     None] = None) -> None:
        self.graph: Graph = graph
        self.start: Zone = start
        self.end: Zone = end
        self.reservations: Union[Dict[int,
                                      Dict[str, int]], None] = reservations
        self.max_turn: int = (max(reservations.keys(), default=0)
                              if reservations else 0)
        self.max_moves: int = len(self.graph.zones)

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
                        if (conn.get_otherside_zone(unpacked_after)
                                == unpacked_before):
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

    def congested_area(self, accumulated_cost: int,
                       neighbor: Zone, conn: Connection) -> bool:
        conn_turn = (accumulated_cost - 1
                     if neighbor.zone_type == "restricted"
                     else accumulated_cost)
        if (self.reservations and
                (self.reservations.get(conn_turn, {}).get(conn.name, 0) + 1 >
                 conn.max_link_capacity)):
            return True
        if (self.reservations and not neighbor.relevant and
                (self.reservations.get(accumulated_cost, {}).get(
                    neighbor.name, 0) + 1 > neighbor.max_drones)):
            return True
        return False

    def dijkstra(self) -> List[Union[Zone, Connection]]:
        poped: Zone = Zone("none", 0, 0)
        poped_tuple: Tuple[int, int, Zone]
        neighbor: Union[Zone, None] = None
        cost: int = 0
        accumulated_cost: int = 0
        distances: Set[Tuple[Zone, int]] = set()
        previous: Dict[Tuple[Zone, int], Tuple[Zone, int]] = {}
        visited: Set[Tuple[Zone, int]] = set()
        priority: List[Tuple[int, int, Zone]] = []
        last_cost: int = 0
        pushed: int = 0

        heapq.heappush(priority, (0, self.penalty(self.start), self.start))
        distances.add((self.start, 0))

        while priority:
            poped_tuple = heapq.heappop(priority)
            cost, _, poped = poped_tuple
            if (poped, cost) in visited:
                continue
            if cost > self.max_turn and cost > last_cost:
                last_cost = cost
                self.max_moves -= 1
            if self.max_moves < 1:
                raise ValueError("Error calculating the algorithm moves")
            visited.add((poped, cost))
            pushed = 0
            for conn in poped.connections:
                neighbor = conn.get_otherside_zone(poped)
                if not neighbor or neighbor.zone_type == "blocked":
                    continue
                accumulated_cost = cost + self.real_cost(neighbor)
                if (self.congested_area(accumulated_cost, neighbor, conn)):
                    continue
                if (neighbor, accumulated_cost) not in distances:
                    distances.add((neighbor, accumulated_cost))
                    heapq.heappush(
                        priority, ((accumulated_cost),
                                   self.penalty(neighbor), neighbor))
                    pushed += 1
                    previous[(neighbor, accumulated_cost)] = (poped, cost)
            if pushed == 0:
                heapq.heappush(priority, (cost + 1,
                                          self.penalty(poped), poped))
                previous[(poped, cost + 1)] = (poped, cost)
            if poped == self.end:
                break

        if poped != self.end:
            raise ValueError("Unreacheble end node")
        return self.rebuild((poped, cost), previous)

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from clases.graph.connection import Connection
from typing import Union, List, Optional


class Zone:
    def __init__(self, name: str, x: int, y: int, max_drones: int = 1,
                 zone_type: str = "normal", color: Union[str, None] = None,
                 relevant: Union[str, None] = None):
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.zone_type: str = zone_type
        self.connections: List[Connection] = []
        self.max_drones: int = max_drones
        self.drone_count: int = 0
        self.color: Union[str, None] = color
        self.relevant: Union[str, None] = relevant

    def add_connection(self, connection: Connection) -> None:
        if connection not in self.connections:
            self.connections.append(connection)

    def get_connection(self, zone_asked: Zone) -> Optional[Connection]:
        for conn in self.connections:
            if conn.get_otherside_zone(self) == zone_asked:
                return conn
        return None

    def drone_in(self) -> None:
        if self.drone_count < self.max_drones:
            self.drone_count += 1

    def drone_out(self) -> None:
        if self.drone_count > 0:
            self.drone_count -= 1

    def is_full(self) -> bool:
        return self.drone_count >= self.max_drones

    def __lt__(self, other: Zone) -> bool:
        return self.name < other.name

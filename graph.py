from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from connection import Connection
    from zone import Zone
from typing import Dict, List


class Graph:
    def __init__(self) -> None:
        self.zones: Dict[str, Zone] = {}
        self.connections: List[Connection] = []

    def add_zone(self, zone: Zone) -> None:
        if zone.name not in self.zones:
            self.zones[zone.name] = zone

    def add_connection(self, connection: Connection) -> None:
        if connection not in self.connections:
            self.connections.append(connection)

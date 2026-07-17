from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from connection import Connection
    from zone import Zone
from typing import Dict, List


class Graph:
    """Container for zones and connections forming the navigation graph."""

    def __init__(self) -> None:
        """Initialize an empty graph."""
        self.zones: Dict[str, Zone] = {}
        self.connections: List[Connection] = []

    def add_zone(self, zone: Zone) -> None:
        """Add a zone to the graph if not already present.

        Args:
            zone (Zone): The zone to add.
        """
        if zone.name not in self.zones:
            self.zones[zone.name] = zone

    def add_connection(self, connection: Connection) -> None:
        """Add a connection to the graph if not already present.

        Args:
            connection (Connection): The connection to add.
        """
        if connection not in self.connections:
            self.connections.append(connection)

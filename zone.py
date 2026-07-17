from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from connection import Connection
from typing import Union, List, Optional


class Zone:
    """Represents a zone (node) in the navigation graph."""

    def __init__(self, name: str, x: int, y: int, max_drones: int = 1,
                 zone_type: str = "normal", color: Union[str, None] = None,
                 relevant: Union[str, None] = None):
        """Initialize a zone with its properties.

        Args:
            name (str): Unique zone identifier.
            x (int): X coordinate on the map.
            y (int): Y coordinate on the map.
            max_drones (int, optional): Max simultaneous drones. Defaults to 1.
            zone_type (str, optional): Zone type (normal, priority,
                restricted, blocked). Defaults to "normal".
            color (Union[str, None], optional): Display color.
            Defaults to None.
            relevant (Union[str, None], optional): "start_hub" or "end_hub"
                if applicable. Defaults to None.
        """
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.zone_type: str = zone_type
        self.connections: List[Connection] = []
        self.max_drones: int = max_drones
        self.color: Union[str, None] = color
        self.relevant: Union[str, None] = relevant

    def add_connection(self, connection: Connection) -> None:
        """Add a connection to this zone if not already present.

        Args:
            connection (Connection): The connection to add.
        """
        if connection not in self.connections:
            self.connections.append(connection)

    def get_connection(self, zone_asked: Zone) -> Optional[Connection]:
        """Find the connection linking this zone to another.

        Args:
            zone_asked (Zone): The target zone to find a connection to.

        Returns:
            Optional[Connection]: The connection if found, None otherwise.
        """
        for conn in self.connections:
            if conn.get_otherside_zone(self) == zone_asked:
                return conn
        return None

    def __lt__(self, other: Zone) -> bool:
        """Compare zones by name for heap ordering.

        Args:
            other (Zone): The zone to compare against.

        Returns:
            bool: True if this zone's name is alphabetically first.
        """
        return self.name < other.name

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from zone import Zone
from typing import Union


class Connection:
    """Represents a bidirectional link between two zones in the graph."""

    def __init__(self, zone1: Zone, zone2:
                 Zone, max_link_capacity: int = 1) -> None:
        """Initialize a connection between two zones.

        Args:
            zone1 (Zone): First zone of the connection.
            zone2 (Zone): Second zone of the connection.
            max_link_capacity (int, optional): Max drones that can
                traverse this connection simultaneously. Defaults to 1.
        """
        self.zone1: Zone = zone1
        self.zone2: Zone = zone2
        self.name: str = zone1.name + "-" + zone2.name
        self.max_link_capacity: int = max_link_capacity

    def get_otherside_zone(self, zone: Zone) -> Union[Zone, None]:
        """Return the zone on the other side of this connection.

        Args:
            zone (Zone): The known zone in the connection.

        Returns:
            Union[Zone, None]: The opposite zone, or None if zone
                is not part of this connection.
        """
        if zone == self.zone1:
            return self.zone2
        if zone == self.zone2:
            return self.zone1
        return None

from typing import List, Dict, Union
from zone import Zone
from connection import Connection


class Drone:
    """Represents a drone navigating through the zone graph."""

    def __init__(self, id: str) -> None:
        """Initialize a drone with its identifier.

        Args:
            id (str): Unique drone identifier (e.g. "D1", "D2").
        """
        self.id: str = id
        self.path: List[Union[Zone, Connection]] = []
        self.reservations: Union[Dict[int, Dict[str, int]], None] = {}
        self.is_active: bool = True

    def add_path(self, path: List[Union[Zone, Connection]]) -> None:
        """Set the drone's movement path.

        Args:
            path (List[Union[Zone, Connection]]): Ordered sequence of
                zones and connections representing the drone's route.
        """
        if len(path) > 0:
            self.path = path

    def add_reservation(self, reservations:
                        Union[Dict[int, Dict[str, int]], None]) -> None:
        """Store the global reservation state for this drone's pathfinding.

        Args:
            reservations (Union[Dict[int, Dict[str, int]], None]):
                Per-turn occupancy map {turn: {zone/conn name: count}}.
        """
        if reservations and len(reservations) > 0:
            self.reservations = reservations

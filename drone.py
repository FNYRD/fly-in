from typing import List, Dict, Union
from zone import Zone
from connection import Connection


class Drone:
    def __init__(self, id: str) -> None:
        self.id: str = id
        self.path: List[Union[Zone, Connection]] = []
        self.reservations: Union[Dict[int, Dict[str, int]], None] = {}
        self.is_active: bool = True

    def add_path(self, path: List[Union[Zone, Connection]]) -> None:
        if len(path) > 0:
            self.path = path

    def add_reservation(self, reservations:
                        Union[Dict[int, Dict[str, int]], None]) -> None:
        if reservations and len(reservations) > 0:
            self.reservations = reservations

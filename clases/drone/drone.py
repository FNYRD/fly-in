from typing import List, Dict, Union
from clases.graph.zone import Zone
from clases.graph.connection import Connection


class Drone:
    def __init__(self, id: str) -> None:
        self.id: str = id
        self.path: List[Union[Zone, Connection]] = []
        self.reservations: Dict[int, Dict[str, Dict[str, int]]] = {}
        self.is_active: bool = True

    def get_position(self, turn: int) -> Union[Zone, Connection, None]:
        if self.is_active and turn > 0 and turn <= len(self.path):
            return self.path[turn - 1]
        return None

    def deactive(self) -> None:
        self.is_active = False

    def add_path(self, path: List[Union[Zone, Connection]]) -> None:
        if len(path) > 0:
            self.path = path

    def add_reservation(self, reservations: Dict[int, Dict[str, Dict[str, int]]]) -> None:
        if len(reservations) > 0:
            self.reservations = reservations

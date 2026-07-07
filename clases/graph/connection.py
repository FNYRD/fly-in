from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from clases.graph.zone import Zone
from typing import Union


class Connection:
    def __init__(self, zone1: Zone, zone2: Zone, max_link_capacity: int = 1) -> None:
        self.zone1: Zone = zone1
        self.zone2: Zone = zone2
        self.name: str = zone1.name + "-" + zone2.name
        self.max_link_capacity: int = max_link_capacity
        self.drone_count: int = 0

    def drone_in(self) -> None:
        if self.drone_count < self.max_link_capacity:
            self.drone_count += 1

    def drone_out(self) -> None:
        if self.drone_count > 0:
            self.drone_count -= 1

    def is_full(self) -> bool:
        return self.drone_count >= self.max_link_capacity

    def get_otherside_zone(self, zone: Zone) -> Union[Zone, None]:
        if zone == self.zone1:
            return self.zone2
        if zone == self.zone2:
            return self.zone1
        return None

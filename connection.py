from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from zone import Zone
from typing import Union


class Connection:
    def __init__(self, zone1: Zone, zone2:
                 Zone, max_link_capacity: int = 1) -> None:
        self.zone1: Zone = zone1
        self.zone2: Zone = zone2
        self.name: str = zone1.name + "-" + zone2.name
        self.max_link_capacity: int = max_link_capacity

    def get_otherside_zone(self, zone: Zone) -> Union[Zone, None]:
        if zone == self.zone1:
            return self.zone2
        if zone == self.zone2:
            return self.zone1
        return None

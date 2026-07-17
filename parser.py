from connection import Connection
from zone import Zone
from graph import Graph
from drone import Drone
from typing import List, Union, Tuple


class Parser:
    """Reads a map file and builds the graph and drone list."""

    def __init__(self, route: str) -> None:
        """Initialize the parser with the path to a map file.

        Args:
            route (str): Absolute path to the map file.
        """
        self.route: str = route
        self.graph: Graph = Graph()
        self.drones: List[Drone] = []
        self.start_end: List[str] = []

    def _parse_drones(self, line_processed: List[str]) -> None:
        """Parse the nb_drones line and create drone instances.

        Args:
            line_processed (List[str]): Tokenized line from the map file.

        Raises:
            ValueError: If drone count is already declared.
            ValueError: If the line format is invalid.
            ValueError: If the value is not a positive integer.
        """
        n_drones: int = 0
        if len(self.drones):
            raise ValueError(
                "Repeated Drone's number declaration")
        if len(line_processed) != 2:
            raise ValueError(
                "Wrong Drone's number declaration")
        if (not line_processed[1].isdigit()
                or (n_drones := int(line_processed[1])) < 1):
            raise ValueError(
                "Drone's number must be a digit greater than 1")
        for i in range(n_drones):
            self.drones.append(Drone("D" + str(i + 1)))

    def _parse_metadata(self, line_processed: List[str],
                        zone: Zone) -> None:
        """Parse bracket-enclosed metadata and apply it to a zone.

        Args:
            line_processed (List[str]): Tokenized metadata tokens.
            zone (Zone): The zone to apply metadata to.

        Raises:
            ValueError: If bracket format is invalid.
            ValueError: If a key or value is empty.
            ValueError: If zone type is not recognized.
            ValueError: If max_drones is not a positive integer.
            ValueError: If metadata key is unknown.
        """
        length: int = len(line_processed)
        data: list[str] = []
        available_zones: List[str] = [
            "normal", "blocked", "restricted", "priority"]
        if "[" != line_processed[0][0] or "]" != line_processed[-1][-1]:
            raise ValueError("Metada must follow this format [metadata=value]")
        line_processed[0] = line_processed[0][1:]
        line_processed[-1] = line_processed[-1][0:-1]
        for i in range(length):
            data = line_processed[i].split("=")
            if len(data) != 2 or data[0] == "" or data[1] == "":
                raise ValueError(f"Empty key or value in metadata:\n{data}")
            match data[0]:
                case "zone":
                    if data[1] not in available_zones:
                        raise ValueError(
                            f"{data[1]} it's not a valid Zone type")
                    zone.zone_type = data[1]
                case "color":
                    zone.color = data[1]
                case "max_drones":
                    if not data[1].isdigit() or int(data[1]) < 1:
                        raise ValueError(
                            "max_drones metadata must be greater than 0")
                    zone.max_drones = int(data[1])
                case _:
                    raise ValueError(
                        f"{data[0]} it's not a valid metadata type")

    def _parse_zones(self, line_processed: List[str]) -> None:
        """Parse a hub/start_hub/end_hub line and add the zone to the graph.

        Args:
            line_processed (List[str]): Tokenized line from the map file.

        Raises:
            ValueError: If the line has too few arguments.
            ValueError: If the zone name is duplicated.
            ValueError: If the zone name contains dashes.
            ValueError: If coordinates are not valid integers.
            ValueError: If start_hub or end_hub is duplicated.
            ValueError: If metadata is invalid.
        """
        temp_val: str = "1"
        length: int = len(line_processed)
        if length < 4:
            raise ValueError(
                f"This line doesn't have enough arguments:\n{line_processed}")
        if line_processed[1] in self.graph.zones:
            raise ValueError(f"Zone's {line_processed[1]}  duplicated")
        if '-' in line_processed[1]:
            raise ValueError("Dashes in the Zone's name are forbidden")
        for i in range(2, 4):
            if line_processed[i][0] == "-":
                temp_val = line_processed[i][1:]
                if not temp_val.isdigit():
                    raise ValueError("The Zone's coordinates must be digits")
            elif not line_processed[i].isdigit():
                raise ValueError("The Zone's coordinates must be digits")
        zone: Zone = Zone(line_processed[1], int(
            line_processed[2]), int(line_processed[3]))
        if (line_processed[0] == "start_hub:"
                or line_processed[0] == "end_hub:"):
            if line_processed[0] in self.start_end:
                raise ValueError(f"Zone {line_processed[0]} already exists")
            self.start_end.append(line_processed[0])
            zone.relevant = line_processed[0][:-1]
        if length > 4:
            self._parse_metadata(line_processed[4:], zone)
        self.graph.add_zone(zone)

    def _parse_connections(self, line_processed: List[str]) -> None:
        """Parse a connection line and link two zones.

        Args:
            line_processed (List[str]): Tokenized line from the map file.

        Raises:
            ValueError: If the line format is invalid.
            ValueError: If the connection name format is wrong.
            ValueError: If one or both zone names do not exist.
            ValueError: If the connection is duplicated.
            ValueError: If metadata format is invalid.
            ValueError: If bracket format is wrong.
            ValueError: If metadata key or value is invalid.
            ValueError: If max_link_capacity is not a positive integer.
        """
        length: int = len(line_processed)
        if length < 2 or length > 3:
            raise ValueError("Connection format error")
        arguments: List[str] = line_processed[1].split("-")
        if len(arguments) != 2:
            raise ValueError(f"Connection names error: {line_processed[1]}")
        z1: Union[Zone, None] = self.graph.zones.get(arguments[0])
        z2: Union[Zone, None] = self.graph.zones.get(arguments[1])
        if not z1 or not z2:
            raise ValueError(
                f"One or both zone names doesn't exists: {line_processed[1]}")
        for conn in z1.connections:
            if conn.get_otherside_zone(z1) == z2:
                raise ValueError(
                    f"this connection already exists!: {line_processed[1]}")
        connection: Connection = Connection(z1, z2)
        if length > 2:
            arguments = line_processed[2].split("=")
            if len(arguments) != 2:
                raise ValueError(f"Connection metadata error: {arguments}")
            if "[" != arguments[0][0] or "]" != arguments[-1][-1]:
                raise ValueError(f"Wrong metadata fromat: {line_processed[2]}")
            arguments[0] = arguments[0][1:]
            arguments[1] = arguments[1][:-1]
            if (arguments[0] != "max_link_capacity"
                    or not arguments[1].isdigit()):
                raise ValueError(f"Wrong metadata values: {line_processed[2]}")
            max_link_capacity: int = int(arguments[1])
            if max_link_capacity < 1:
                raise ValueError(
                    "max_link_capacity must be an positive integer")
            connection.max_link_capacity = max_link_capacity
        self.graph.add_connection(connection)
        z1.add_connection(connection)
        z2.add_connection(connection)

    def manufacturing(self) -> Tuple[Graph, List[Drone]]:
        """Read the map file and build the graph and drone list.

        Raises:
            ValueError: If nb_drones is not the first declaration.
            ValueError: If a hub type is unknown.
            ValueError: If a line type is unrecognized.
            ValueError: If start_hub or end_hub is missing.
            ValueError: If there are no connections.

        Returns:
            Tuple[Graph, List[Drone]]: The populated graph and
                list of drones ready for simulation.
        """
        line_processed: List[str]
        with open(self.route, 'r', encoding='utf-8') as file:
            for line in file:
                line_processed = line.strip().split()
                if not line_processed or line_processed[0].startswith("#"):
                    continue
                if len(self.drones) == 0 and line_processed[0] != "nb_drones:":
                    raise ValueError(
                        "Drone's number declaration must be "
                        "at the beginning of the file")
                elif line_processed[0] == "nb_drones:":
                    self._parse_drones(line_processed)
                elif "hub" in line_processed[0]:
                    if (line_processed[0]
                            not in ("hub:", "start_hub:", "end_hub:")):
                        raise ValueError(f"Unknown name: {line_processed[0]}")
                    self._parse_zones(line_processed)
                elif line_processed[0] == "connection:":
                    self._parse_connections(line_processed)
                else:
                    raise ValueError(f"Unknown line {line_processed}")
            if len(self.start_end) != 2:
                raise ValueError(
                    "It's mandatory being only one start and one end hub")
            if len(self.graph.connections) < 1:
                raise ValueError(
                    "without connections it's imposible to "
                    "reach the goal zone")
        return (self.graph, self.drones)

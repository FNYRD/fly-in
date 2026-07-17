#!/usr/bin/env python3
import os
from graph import Graph
from drone import Drone
from parser import Parser
from simulation import Simulation
from typing import List, Tuple
from view import View


class TerminalSim:
    """Terminal-based simulation runner with text menu and output."""
    def __init__(self) -> None:
        """Initialize the terminal simulation runner."""

    @staticmethod
    def _get_maps() -> Tuple[str, str, str, str]:
        """Prompt the user to select a difficulty level and map file.

        Raises:
            ValueError: If the selected level index is out of range.
            ValueError: If the selected map index is out of range.

        Returns:
            Tuple[str, str, str, str]: Project directory, maps directory,
                selected level, and selected map filename.
        """
        directory = os.path.dirname(os.path.abspath(__file__))
        maps_directory: str = os.path.join(directory, "maps")
        levels: List[str] = ["easy", "medium", "hard", "challenger", "extra"]
        print("\nDrone's Path finding:\nChoose one level:\n")
        for i in range(len(levels)):
            print(f"press {i + 1} for: {levels[i]}")
        print()
        index: int = int(input("response: "))
        if 0 < index <= len(levels):
            level: str = levels[index - 1]
        else:
            raise ValueError("Wrong option!")
        folder: str = os.path.join(maps_directory, level)
        files: List[str] = [file for file in sorted(
            os.listdir(folder)) if file.endswith(".txt")]
        print("Choose one map to solve:\n")
        for i in range(len(files)):
            print(f"press {i + 1} for: {files[i]}")
        print()
        index = int(input("response: "))
        if 0 < index <= len(files):
            file: str = files[index - 1]
        else:
            raise ValueError("Wrong option!")
        return directory, maps_directory, level, file

    def terminal_sim(self) -> None:
        """Entry point: select map, parse, simulate, and print output."""
        dictory: str = ""
        dir_map: str = ""
        level: str = ""
        map: str = ""
        dictory, dir_map, level, map = self._get_maps()
        route = os.path.join(dictory, dir_map, level, map)
        graph: Graph
        drones: List[Drone]
        graph, drones = Parser(route).manufacturing()
        sim: Simulation = Simulation(graph, drones)
        sim.simulating()
        print(f"Total turns {len(sim.logs)}\n")
        sim.output()


def menu() -> None:
    """Prompt user to choose terminal or pygame mode and run."""
    try:
        view: View = View()
        terminal: TerminalSim = TerminalSim()
        option: int = 0
        print("\nFor terminal simulation press: 1\n"
              "For pygame simulation press: 2")
        option = int(input("Choice: "))
        match option:
            case 1:
                terminal.terminal_sim()
            case 2:
                view.run()
    except (ValueError, FileNotFoundError, RuntimeError) as e:
        print(f"Error: {e}")
    except FileNotFoundError:
        print("File route doesn't exits")


if __name__ == "__main__":
    menu()

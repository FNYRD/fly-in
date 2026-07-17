#!/usr/bin/env python3
import pygame
from typing import Tuple, List, Dict, Union
from graph import Graph
from zone import Zone
from connection import Connection
from simulation import Simulation
from parser import Parser
from drone import Drone
import os


class View:
    """Pygame visualization for the Fly-In drone simulation."""

    COLORS: Dict[str, Tuple[int, int, int]] = {
        "green": (106, 153, 118),
        "blue": (100, 130, 168),
        "red": (178, 98, 93),
        "yellow": (194, 178, 115),
        "gray": (140, 140, 140),
        "black": (50, 50, 50),
        "brown": (150, 110, 80),
        "crimson": (165, 75, 75),
        "cyan": (100, 170, 170),
        "darkred": (140, 60, 60),
        "gold": (185, 165, 90),
        "lime": (130, 175, 100),
        "magenta": (160, 95, 145),
        "maroon": (120, 60, 65),
        "orange": (200, 140, 85),
        "purple": (130, 95, 160),
        "rainbow": (160, 130, 170),
        "violet": (140, 105, 165),
    }

    DRONE_COLORS: List[Tuple[int, int, int]] = [
        (255, 255, 255), (255, 200, 50), (50, 200, 255),
        (255, 100, 100), (100, 255, 100), (200, 150, 255),
        (255, 150, 50), (150, 255, 255), (255, 100, 200),
        (200, 255, 150), (100, 150, 255), (255, 220, 150),
        (180, 100, 255), (100, 255, 180), (255, 180, 180),
    ]

    def __init__(self) -> None:
        """Initialize pygame, screen dimensions, and background."""
        pygame.init()
        screen_info = pygame.display.Info()
        self.max_w: int = screen_info.current_w - \
            100  # type: ignore[attr-defined]
        self.max_h: int = screen_info.current_h - \
            100  # type: ignore[attr-defined]
        self.menu_w: int = min(800, self.max_w)
        self.menu_h: int = min(600, self.max_h)
        self.screen: pygame.Surface = pygame.display.set_mode(
            (self.menu_w, self.menu_h))
        pygame.display.set_caption("Fly-In")
        test_dir: str = os.path.dirname(os.path.abspath(__file__))
        self.maps_dir: str = os.path.join(test_dir, "maps")
        self.background: pygame.Surface = pygame.image.load("./views.jpg")

    def get_maps(self) -> List[Tuple[str, str]]:
        """Scan the maps directory and return display names with paths.

        Returns:
            List[Tuple[str, str]]: List of (display label, file path) pairs.
        """
        maps: List[Tuple[str, str]] = []
        for difficulty in ["easy", "medium", "hard", "challenger", "extra"]:
            folder: str = os.path.join(self.maps_dir, difficulty)
            if not os.path.isdir(folder):
                continue
            for f in sorted(os.listdir(folder)):
                if f.endswith(".txt"):
                    raw: str = os.path.splitext(f)[0]
                    label: str = raw.split("_", 1)[1] if "_" in raw else raw
                    display: str = f"[{difficulty}] {label}"
                    path: str = os.path.join(folder, f)
                    maps.append((display, path))
        return maps

    def menu_select_map(self, map_list: List[Tuple[str, str]]) -> str:
        """Display the map selection menu.

        Args:
            map_list (List[Tuple[str, str]]): Available maps.

        Returns:
            str: Path to the selected map file.
        """
        selected: int = 0
        title_font: pygame.font.Font = pygame.font.SysFont(None, 48)
        item_font: pygame.font.Font = pygame.font.SysFont(None, 32)
        clock: pygame.time.Clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(map_list)
                    elif event.key == pygame.K_UP:
                        selected = (selected - 1) % len(map_list)
                    elif event.key == pygame.K_RETURN:
                        return map_list[selected][1]

            bg: pygame.Surface = pygame.transform.scale(
                self.background, (self.menu_w, self.menu_h))
            self.screen.blit(bg, (0, 0))

            title: pygame.Surface = title_font.render(
                "Select Map", True, (255, 255, 255))
            self.screen.blit(
                title, (self.menu_w // 2 - title.get_width() // 2, 30))

            visible: int = min(len(map_list), (self.menu_h - 120) // 35)
            start: int = max(0, selected - visible // 2)
            start = min(start, max(0, len(map_list) - visible))

            for idx in range(start, min(start + visible, len(map_list))):
                color: Tuple[int, int, int] = (
                    (255, 255, 100) if idx == selected else (200, 200, 200))
                prefix: str = "> " if idx == selected else "  "
                label_surf: pygame.Surface = item_font.render(
                    prefix + map_list[idx][0], True, color)
                y_pos: int = 90 + (idx - start) * 35
                self.screen.blit(label_surf, (60, y_pos))

            hint: pygame.Surface = item_font.render(
                "Arrow keys to navigate, Enter to select",
                True, (150, 150, 150))
            self.screen.blit(
                hint,
                (self.menu_w // 2 - hint.get_width() // 2, self.menu_h - 40))

            pygame.display.flip()
            clock.tick(30)

    def menu_select_mode(self) -> str:
        """Display the playback mode selection menu.

        Returns:
            str: "manual" or "auto".
        """
        options: List[Tuple[str, str]] = [
            ("Manual", "manual"),
            ("Automatic", "auto"),
        ]
        selected: int = 0
        title_font: pygame.font.Font = pygame.font.SysFont(None, 48)
        item_font: pygame.font.Font = pygame.font.SysFont(None, 36)
        clock: pygame.time.Clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_DOWN, pygame.K_UP):
                        selected = 1 - selected
                    elif event.key == pygame.K_RETURN:
                        return options[selected][1]

            bg: pygame.Surface = pygame.transform.scale(
                self.background, (self.menu_w, self.menu_h))
            self.screen.blit(bg, (0, 0))

            title: pygame.Surface = title_font.render(
                "Playback Mode", True, (255, 255, 255))
            self.screen.blit(
                title, (self.menu_w // 2 - title.get_width() // 2, 150))

            for idx, (label, _) in enumerate(options):
                color: Tuple[int, int, int] = (
                    (255, 255, 100) if idx == selected else (200, 200, 200))
                prefix: str = "> " if idx == selected else "  "
                desc: str = (
                    "(Arrow keys)" if label == "Manual"
                    else "(0.5s per turn)")
                label_surf: pygame.Surface = item_font.render(
                    f"{prefix}{label}  {desc}", True, color)
                self.screen.blit(
                    label_surf,
                    (self.menu_w // 2 - label_surf.get_width() // 2,
                     250 + idx * 50))

            hint: pygame.Surface = item_font.render(
                "Arrow keys to switch, Enter to select",
                True, (150, 150, 150))
            self.screen.blit(
                hint,
                (self.menu_w // 2 - hint.get_width() // 2, self.menu_h - 40))

            pygame.display.flip()
            clock.tick(30)

    def run_simulation(self, route: str, mode: str) -> None:
        """Parse, simulate, and render the drone visualization.

        Args:
            route (str): Path to the map file.
            mode (str): "manual" or "auto" playback mode.
        """
        raw_name: str = os.path.splitext(os.path.basename(route))[0]
        map_name: str = (
            raw_name.split("_", 1)[1] if "_" in raw_name else raw_name)
        graph: Graph
        drones: List[Drone]
        graph, drones = Parser(route).manufacturing()
        sim: Simulation = Simulation(graph, drones)
        sim.simulating()

        xs: List[int] = [z.x for z in graph.zones.values()]
        ys: List[int] = [z.y for z in graph.zones.values()]
        min_x: int = min(xs)
        max_x: int = max(xs)
        min_y: int = min(ys)
        max_y: int = max(ys)

        initial_margin: int = 50
        w: int = max(800, initial_margin * 2
                     + max(max_x - min_x, 1) * 100)
        h: int = max(600, initial_margin * 2
                     + max(max_y - min_y, 1) * 100)

        initial_scale_x: float = (
            (w - initial_margin * 2) / max(max_x - min_x, 1))
        initial_scale_y: float = (
            (h - initial_margin * 2) / max(max_y - min_y, 1))
        radius: int = max(35, int(min(initial_scale_x, initial_scale_y) / 4))

        pixels_per_unit: int = max(100, int(radius * 3.5))
        margin_value: int = max(initial_margin, radius + 30)
        margin: int = margin_value * 2
        w = min(self.max_w, max(800, margin
                + max(max_x - min_x, 1) * pixels_per_unit))
        h = min(self.max_h, max(600, margin
                + max(max_y - min_y, 1) * pixels_per_unit))
        sim_scale: Tuple[int, int] = (w, h)

        scale_x: float = (w - margin) / max(max_x - min_x, 1)
        scale_y: float = (h - margin) / max(max_y - min_y, 1)
        radius = max(5, int(min(scale_x, scale_y) / 4))

        sim_screen: pygame.Surface = pygame.display.set_mode(sim_scale)
        bg: pygame.Surface = pygame.transform.scale(
            self.background, sim_scale)

        zone_pos: Dict[str, Tuple[float, float]] = {}
        for zone in graph.zones.values():
            px: float = (w / 2 if max_x == min_x
                         else margin_value + (zone.x - min_x) * scale_x)
            py: float = (h / 2 if max_y == min_y
                         else margin_value + (zone.y - min_y) * scale_y)
            zone_pos[zone.name] = (px, py)

        zone_labels: Dict[str, pygame.Surface] = {}
        for zone in graph.zones.values():
            font_size: int = max(10, int(radius * 1.2))
            font: pygame.font.Font = pygame.font.SysFont(None, font_size)
            label: pygame.Surface = font.render(
                zone.name, True, (255, 255, 255))
            while label.get_width() > radius * 1.8 and font_size > 10:
                font_size -= 1
                font = pygame.font.SysFont(None, font_size)
                label = font.render(zone.name, True, (255, 255, 255))
            zone_labels[zone.name] = label

        drone_radius: int = max(3, radius // 3)
        max_turn: int = max(len(d.path) for d in drones) - 1
        current_turn: int = 0
        turn_font: pygame.font.Font = pygame.font.SysFont(None, 30)
        id_font: pygame.font.Font = pygame.font.SysFont(
            None, max(14, drone_radius))
        line_w: int = max(3, radius // 4)
        clock: pygame.time.Clock = pygame.time.Clock()
        auto_timer: int = 0
        auto_interval: int = 500

        running: bool = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if mode == "manual":
                        if (event.key == pygame.K_RIGHT
                                and current_turn < max_turn):
                            current_turn += 1
                        elif (event.key == pygame.K_LEFT
                              and current_turn > 0):
                            current_turn -= 1

            if mode == "auto" and current_turn < max_turn:
                auto_timer += clock.get_time()
                if auto_timer >= auto_interval:
                    auto_timer = 0
                    current_turn += 1

            sim_screen.blit(bg, (0, 0))

            for conn in graph.connections:
                p1: Tuple[float, float] = zone_pos[conn.zone1.name]
                p2: Tuple[float, float] = zone_pos[conn.zone2.name]
                pygame.draw.line(
                    sim_screen, (200, 200, 200), p1, p2, line_w)

            for zone in graph.zones.values():
                pos: Tuple[float, float] = zone_pos[zone.name]
                if (zone.color is not None
                        and (zone.color in self.COLORS
                             or zone.color in pygame.color.THECOLORS)):
                    c: Union[Tuple[int, int, int], pygame.Color] = (
                        self.COLORS[zone.color] if zone.color in self.COLORS
                        else pygame.Color(zone.color))
                    pygame.draw.circle(sim_screen, c, pos, radius)
                else:
                    pygame.draw.circle(
                        sim_screen, self.COLORS["gray"], pos, radius)
                zl: pygame.Surface = zone_labels[zone.name]
                zl_rect: pygame.Rect = zl.get_rect(
                    center=(int(pos[0]), int(pos[1])))
                sim_screen.blit(zl, zl_rect)

            for i, drone in enumerate(drones):
                if current_turn >= len(drone.path):
                    continue
                step: Union[Zone, Connection] = drone.path[current_turn]
                dp: Tuple[float, float]
                if isinstance(step, Zone):
                    dp = zone_pos[step.name]
                elif isinstance(step, Connection):
                    p1 = zone_pos[step.zone1.name]
                    p2 = zone_pos[step.zone2.name]
                    dp = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
                else:
                    continue
                dc: Tuple[int, int, int] = (
                    self.DRONE_COLORS[i % len(self.DRONE_COLORS)])
                motor_r: int = max(2, drone_radius // 2)
                arm: int = drone_radius
                pygame.draw.line(
                    sim_screen, dc,
                    (dp[0] - arm, dp[1] - arm),
                    (dp[0] + arm, dp[1] + arm),
                    max(1, motor_r // 2))
                pygame.draw.line(
                    sim_screen, dc,
                    (dp[0] + arm, dp[1] - arm),
                    (dp[0] - arm, dp[1] + arm),
                    max(1, motor_r // 2))
                pygame.draw.circle(
                    sim_screen, dc,
                    (dp[0] - arm, dp[1] - arm), motor_r)
                pygame.draw.circle(
                    sim_screen, dc,
                    (dp[0] + arm, dp[1] - arm), motor_r)
                pygame.draw.circle(
                    sim_screen, dc,
                    (dp[0] - arm, dp[1] + arm), motor_r)
                pygame.draw.circle(
                    sim_screen, dc,
                    (dp[0] + arm, dp[1] + arm), motor_r)
                pygame.draw.circle(
                    sim_screen, dc, dp, max(1, motor_r // 2))
                id_label: pygame.Surface = id_font.render(
                    drone.id, True, dc)
                id_rect: pygame.Rect = id_label.get_rect(
                    midbottom=(dp[0], dp[1] - arm - 2))
                sim_screen.blit(id_label, id_rect)

            turn_label: pygame.Surface = turn_font.render(
                f"{map_name}  |  Turn {current_turn}/{max_turn}"
                f"  |  ESC = menu",
                True, (255, 255, 255))
            sim_screen.blit(turn_label, (10, 10))
            pygame.display.flip()
            clock.tick(60)

    def run(self) -> None:
        """Main loop: cycle through map selection, mode, and simulation."""
        map_list: List[Tuple[str, str]] = self.get_maps()
        while True:
            self.screen = pygame.display.set_mode(
                (self.menu_w, self.menu_h))
            selected_map: str = self.menu_select_map(map_list)
            selected_mode: str = self.menu_select_mode()
            self.run_simulation(selected_map, selected_mode)

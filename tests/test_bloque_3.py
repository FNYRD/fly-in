import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Union  # noqa: E402
from clases.graph.zone import Zone  # noqa: E402
from clases.graph.connection import Connection  # noqa: E402
from clases.graph.graph import Graph  # noqa: E402
from clases.parser.parser import Parser  # noqa: E402
from clases.dijkstra.dijkstra import Dijkstra  # noqa: E402

FILES_DIR: str = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "files_test")

EXPECTED_D1_PATH: List[str] = ["start", "start-roof", "roof", "goal"]


def route(filename: str) -> str:
    return os.path.join(FILES_DIR, filename)


def check(label: str, obtained: object, expected: object) -> None:
    status: str = "OK" if obtained == expected else "FAIL"
    print(f"  [{status}] {label}: obtenido={obtained!r} esperado={expected!r}")


def path_names(path: List[Union[Zone, Connection]]) -> List[str]:
    return [p.name for p in path]


# ============================================================
# 1. CREACIÓN DE Dijkstra (ligero — Parser/Graph ya validan antes)
# ============================================================
def run_creation_case() -> None:
    print("=" * 60)
    print("BLOQUE: CREACIÓN DE Dijkstra")
    print("=" * 60)

    graph = Graph()
    start = Zone("start", 0, 0, relevant="start_hub")
    end = Zone("end", 1, 1, relevant="end_hub")
    graph.add_zone(start)
    graph.add_zone(end)

    print("\n--- Sin reservations (default None) ---")
    d1 = Dijkstra(graph, start, end)
    check("max_turn (sin reservations)", d1.max_turn, 0)
    check("max_moves (= nº de zonas)", d1.max_moves, len(graph.zones))

    print("\n--- Con reservations no vacío ---")
    reservations: Dict[int, Dict[str, int]] = {5: {"x": 2}, 1: {"y": 1}}
    d2 = Dijkstra(graph, start, end, reservations)
    check("max_turn (= clave máxima)", d2.max_turn, 5)


# ============================================================
# 2. FLUJO REAL — Parser produce Graph/Drones (integración Bloque 1+2)
# ============================================================
def run_real_flow_case() -> None:
    print("\n" + "=" * 60)
    print("BLOQUE: FLUJO REAL (Parser -> Graph, Drones)")
    print("=" * 60)

    graph, drones = Parser(route("file_test_26.txt")).manufacturing()

    print("\n--- Verificación de objetos construidos ---")
    check("nº de drones", len(drones), 2)
    check("id primer drone", drones[0].id, "D1")
    check("id segundo drone", drones[1].id, "D2")
    check("nº de zonas", len(graph.zones), 4)
    check("nº de conexiones", len(graph.connections), 3)
    check("relevant de start", graph.zones["start"].relevant, "start_hub")
    check("relevant de goal", graph.zones["goal"].relevant, "end_hub")
    check("zone_type de roof", graph.zones["roof"].zone_type, "restricted")
    check("zone_type de dead", graph.zones["dead"].zone_type, "blocked")


# ============================================================
# 3. DIJKSTRA SIN CONGESTIÓN (caso D1) — mapa fácil, restricted y blocked
# ============================================================
def run_no_congestion_case() -> None:
    print("\n" + "=" * 60)
    print("BLOQUE: DIJKSTRA SIN CONGESTIÓN (D1)")
    print("=" * 60)

    graph, _ = Parser(route("file_test_26.txt")).manufacturing()
    start = graph.zones["start"]
    goal = graph.zones["goal"]

    path = Dijkstra(graph, start, goal).dijkstra()

    print("\n--- Path resultante (sin reservations) ---")
    print(f"  path: {path_names(path)}")
    check("longitud del path (turnos)", len(path), 4)
    check("orden del path", path_names(path), EXPECTED_D1_PATH)
    check("conexión intercalada es Connection",
          isinstance(path[1], Connection), True)
    check("zona 'dead' (blocked) no aparece en el path",
          "dead" in path_names(path), False)


# ============================================================
# 4. CONGESTIÓN DE ZONA (reservations a mano, caso D2)
#    Invariante: si D1 llegó, D2 también debe llegar (solo espera más).
# ============================================================
def run_zone_congestion_case() -> None:
    print("\n" + "=" * 60)
    print("BLOQUE: CONGESTIÓN DE ZONA (D2 espera 1 turno)")
    print("=" * 60)

    graph, _ = Parser(route("file_test_26.txt")).manufacturing()
    start = graph.zones["start"]
    goal = graph.zones["goal"]

    # D1 ya ocupó "roof" en el turno 2 (el turno en que D2 querría entrar)
    reservations: Dict[int, Dict[str, int]] = {2: {"roof": 1}}

    try:
        path = Dijkstra(graph, start, goal, reservations).dijkstra()
    except ValueError as e:
        print(f"  [FAIL] no debía lanzar (invariante D1->D2), lanzó: {e}")
        return

    print("\n--- Path resultante (D2, con 1 zona congestionada) ---")
    print(f"  path: {path_names(path)}")
    check("longitud del path (1 espera absorbida, turno 0 no cuenta)",
          len(path), 5)
    check("orden del path (misma ruta, 1 turno de espera absorbido)",
          path_names(path), ["start", "start", "start-roof", "roof", "goal"])


# ============================================================
# 5. CONGESTIÓN DE CONEXIÓN (max_link_capacity vía reservations)
# ============================================================
def run_connection_congestion_case() -> None:
    print("\n" + "=" * 60)
    print("BLOQUE: CONGESTIÓN DE CONEXIÓN (start-roof llena en tránsito)")
    print("=" * 60)

    graph, _ = Parser(route("file_test_26.txt")).manufacturing()
    start = graph.zones["start"]
    goal = graph.zones["goal"]

    # Conexión "start-roof" ocupada en el turno de tránsito real (turno 1)
    reservations: Dict[int, Dict[str, int]] = {1: {"start-roof": 1}}

    try:
        path = Dijkstra(graph, start, goal, reservations).dijkstra()
    except ValueError as e:
        print(f"  [FAIL] no debía lanzar, lanzó: {e}")
        return

    print("\n--- Path resultante (conexión congestionada 1 turno) ---")
    print(f"  path: {path_names(path)}")
    check("longitud del path (espera 1 turno antes de transitar)",
          len(path), 5)
    check("orden del path", path_names(path), ["start", "start", "start-roof", "roof", "goal"])


# ============================================================
# 6. PRECISIÓN DEL TURNO DE TRÁNSITO (conn_turn = accumulated_cost - 1)
# ============================================================
def run_conn_turn_precision_case() -> None:
    print("\n" + "=" * 60)
    print("BLOQUE: PRECISIÓN conn_turn EN ZONAS RESTRICTED")
    print("=" * 60)

    graph, _ = Parser(route("file_test_26.txt")).manufacturing()
    start = graph.zones["start"]
    goal = graph.zones["goal"]

    print("\n--- Caso A: reservations en el turno de TRÁNSITO (turno 1) ---")
    reservations_a: Dict[int, Dict[str, int]] = {1: {"start-roof": 1}}
    path_a = Dijkstra(graph, start, goal, reservations_a).dijkstra()
    print(f"  path: {path_names(path_a)}")
    check("SÍ debe detectar congestión (espera 1 turno)", len(path_a), 5)

    print("\n--- Caso B: reservations en el turno de LLEGADA (turno 2,"
          " clave equivocada para la conexión) ---")
    reservations_b: Dict[int, Dict[str, int]] = {2: {"start-roof": 1}}
    path_b = Dijkstra(graph, start, goal, reservations_b).dijkstra()
    print(f"  path: {path_names(path_b)}")
    check("NO debe detectar congestión (igual a D1 sin reservas)",
          len(path_b), 4)
    check("orden del path (idéntico a D1, sin esperas)",
          path_names(path_b), EXPECTED_D1_PATH)


# ============================================================
# 7. END ESTRUCTURALMENTE INALCANZABLE (sin congestión de por medio)
# ============================================================
def run_unreachable_end_case() -> None:
    print("\n" + "=" * 60)
    print("BLOQUE: END ESTRUCTURALMENTE INALCANZABLE")
    print("=" * 60)

    graph = Graph()
    start = Zone("s", 0, 0, relevant="start_hub")
    end = Zone("e", 1, 1, relevant="end_hub")
    graph.add_zone(start)
    graph.add_zone(end)
    # Sin conexiones entre ellas -> end aislado

    print("\n--- Grafo con 2 zonas, sin ninguna conexión ---")
    try:
        Dijkstra(graph, start, end).dijkstra()
        print("  [FAIL] esperado: ValueError | obtenido: ninguna excepción")
    except ValueError as e:
        print(f"  [OK] excepción capturada: {e}")


# ============================================================
# 8. STRESS — congestión en cascada (2+ turnos seguidos bloqueada)
#    Verifica que NO se lanza un falso "inalcanzable" (max_moves aguanta),
#    pero expone el HALLAZGO de esperas colapsadas en start (ver abajo).
# ============================================================
def run_cascading_congestion_stress_case() -> None:
    print("\n" + "=" * 60)
    print("BLOQUE: STRESS — CONGESTIÓN EN CASCADA (2 turnos seguidos)")
    print("=" * 60)

    graph, _ = Parser(route("file_test_26.txt")).manufacturing()
    start = graph.zones["start"]
    goal = graph.zones["goal"]

    # "roof" ocupada en 2 turnos consecutivos -> el dron espera 2 turnos
    reservations: Dict[int, Dict[str, int]] = {
        2: {"roof": 1}, 3: {"roof": 1},
    }

    try:
        path = Dijkstra(graph, start, goal, reservations).dijkstra()
    except ValueError as e:
        print(f"  [FAIL] no debía lanzar (congestión temporal, no"
              f" deadlock real), lanzó: {e}")
        return

    print("\n--- Path resultante (2 esperas seguidas en start) ---")
    print(f"  path: {path_names(path)}")
    print("  turnos reales calculados a mano (trazado del algoritmo): 6")
    print(f"  longitud del path devuelto: {len(path)}")
    check("¿longitud del path coincide con los turnos reales (6)?", len(path), 6)


# ============================================================
# 9. (Recomendado) DESEMPATE POR priority EN EL HEAP
# ============================================================
def run_priority_tiebreak_case() -> None:
    print("\n" + "=" * 60)
    print("BLOQUE: DESEMPATE POR priority (recomendado, no pedido)")
    print("=" * 60)

    graph = Graph()
    start = Zone("start", 0, 0, relevant="start_hub")
    p = Zone("p", 1, 1, zone_type="priority")
    n = Zone("n", 2, 2, zone_type="normal")
    goal = Zone("goal", 3, 3, relevant="end_hub")
    for z in (start, p, n, goal):
        graph.add_zone(z)

    conns = [
        Connection(start, p),
        Connection(start, n),
        Connection(p, goal),
        Connection(n, goal),
    ]
    for c in conns:
        c.zone1.add_connection(c)
        c.zone2.add_connection(c)
        graph.add_connection(c)

    path = Dijkstra(graph, start, goal).dijkstra()
    print(f"\n  path: {path_names(path)}")
    check("dos rutas de igual coste -> Dijkstra prefiere la priority ('p')",
          "p" in path_names(path), True)
    check("no debería pasar por la ruta normal ('n')",
          "n" in path_names(path), False)


def main() -> None:
    run_creation_case()
    run_real_flow_case()
    run_no_congestion_case()
    run_zone_congestion_case()
    run_connection_congestion_case()
    run_conn_turn_precision_case()
    run_unreachable_end_case()
    run_cascading_congestion_stress_case()
    run_priority_tiebreak_case()

    print("\n" + "=" * 60)
    print("Tests completados.")
    print("=" * 60)


if __name__ == "__main__":
    main()

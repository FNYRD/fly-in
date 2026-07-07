import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Tuple  # noqa: E402
from clases.parser.parser import Parser  # noqa: E402

FILES_DIR: str = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "files_test")

# Cada caso de error: (archivo, condición que debe romper)
FAILURE_CASES: List[Tuple[str, str]] = [
    ("file_test_0.txt", "Primera línea no es nb_drones"),
    ("file_test_1.txt", "Token tipo hub inválido (xhub:)"),
    ("file_test_2.txt", "Línea desconocida"),
    ("file_test_3.txt", "Falta start o end hub"),
    ("file_test_4.txt", "nb_drones declarado dos veces"),
    ("file_test_5.txt", "nb_drones sin número"),
    ("file_test_6.txt", "nb_drones no es dígito positivo"),
    ("file_test_7.txt", "Metadata de zona sin corchetes"),
    ("file_test_8.txt", "Par de metadata sin = o vacío"),
    ("file_test_9.txt", "Tipo de zona inválido"),
    ("file_test_10.txt", "max_drones no es entero positivo"),
    ("file_test_11.txt", "Clave de metadata desconocida"),
    ("file_test_12.txt", "Hub con argumentos insuficientes"),
    ("file_test_13.txt", "Nombre de zona duplicado"),
    ("file_test_14.txt", "Nombre de zona con guion"),
    ("file_test_15.txt", "Coordenada no entera"),
    ("file_test_16.txt", "start/end hub declarado dos veces"),
    ("file_test_17.txt", "Connection con longitud inválida"),
    ("file_test_18.txt", "Connection con split - inválido"),
    ("file_test_19.txt", "Connection con zona inexistente"),
    ("file_test_20.txt", "Connection duplicada"),
    ("file_test_21.txt", "Metadata de connection sin ="),
    ("file_test_22.txt", "Metadata de connection sin corchetes"),
    ("file_test_23.txt", "Clave/valor de max_link_capacity inválido"),
    ("file_test_24.txt", "max_link_capacity no positivo"),
]


def route(filename: str) -> str:
    return os.path.join(FILES_DIR, filename)


def check(label: str, obtained: object, expected: object) -> None:
    status: str = "OK" if obtained == expected else "FAIL"
    print(f"  [{status}] {label}: obtenido={obtained!r} esperado={expected!r}")


# ============================================================
# CASOS DE ERROR — cada archivo debe lanzar una excepción
# ============================================================
def run_failure_cases() -> None:
    print("=" * 60)
    print("CASOS DE ERROR (cada uno debe lanzar una excepción)")
    print("=" * 60)
    for i, (filename, desc) in enumerate(FAILURE_CASES):
        print(f"\nTest {i} — {desc}")
        try:
            Parser(route(filename)).manufacturing()
            print("  [FAIL] esperado: excepción | obtenido: ninguna")
        except (ValueError, OSError) as e:
            print(f"  [OK] excepción capturada: {e}")


# ============================================================
# CASO ARCHIVO INEXISTENTE — debe lanzar OSError
# ============================================================
def run_oserror_case() -> None:
    print("\n" + "=" * 60)
    print("CASO ARCHIVO INEXISTENTE (OSError)")
    print("=" * 60)
    print("\nTest 25 — Ruta a archivo que no existe")
    try:
        Parser(route("no_existe.txt")).manufacturing()
        print("  [FAIL] esperado: OSError | obtenido: ninguna")
    except (ValueError, OSError) as e:
        print(f"  [OK] excepción capturada: {e}")


# ============================================================
# CASO VÁLIDO — debe retornar Graph y drones correctos
# ============================================================
def run_valid_case() -> None:
    print("\n" + "=" * 60)
    print("CASO VÁLIDO (verifica los objetos retornados)")
    print("=" * 60)
    print("\nTest 26 — Mapa válido completo")
    try:
        graph, drones = Parser(route("file_test_25.txt")).manufacturing()
    except (ValueError, OSError) as e:
        print(f"  [FAIL] no debía lanzar, lanzó: {e}")
        return
    check("nº de drones", len(drones), 3)
    check("id primer drone", drones[0].id, "D1")
    check("id último drone", drones[2].id, "D3")
    check("nº de zonas", len(graph.zones), 3)
    check("relevant de start", graph.zones["start"].relevant, "start_hub")
    check("relevant de goal", graph.zones["goal"].relevant, "end_hub")
    check("relevant de mid", graph.zones["mid"].relevant, None)
    check("zone_type de mid", graph.zones["mid"].zone_type, "priority")
    check("color de mid", graph.zones["mid"].color, "red")
    check("max_drones de mid", graph.zones["mid"].max_drones, 2)
    check("color de start", graph.zones["start"].color, "green")
    check("color de goal", graph.zones["goal"].color, "yellow")
    check("nº de conexiones", len(graph.connections), 2)
    check("conexiones en start", len(graph.zones["start"].connections), 1)
    check("conexiones en mid", len(graph.zones["mid"].connections), 2)
    check("conexiones en goal", len(graph.zones["goal"].connections), 1)
    start = graph.zones["start"]
    mid = graph.zones["mid"]
    goal = graph.zones["goal"]
    check("cap start-mid (default)", start.connections[0].max_link_capacity, 1)
    for conn in mid.connections:
        if conn.get_otherside_zone(mid) is goal:
            check("cap mid-goal", conn.max_link_capacity, 2)


def main() -> None:
    run_failure_cases()
    run_oserror_case()
    run_valid_case()


if __name__ == "__main__":
    main()

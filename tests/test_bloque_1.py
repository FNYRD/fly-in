#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clases.graph.zone import Zone
from clases.graph.connection import Connection
from clases.graph.graph import Graph
from clases.drone.drone import Drone


def main() -> None:

    # ============================================================
    # BLOQUE: CONNECTION
    # ============================================================

    print("\n" + "=" * 60)
    print("BLOQUE: CONNECTION")
    print("=" * 60)

    # Crear zonas base para los tests de Connection
    za = Zone("hub", 0, 0)
    zb = Zone("roof1", 3, 4, zone_type="restricted")
    zc = Zone("corridorA", 4, 3, zone_type="priority")
    zd = Zone("tunnelB", 5, 5)
    ze = Zone("crossroad", 6, 2)
    zf = Zone("depot", 8, 1)
    zg = Zone("goal", 10, 10)

    # Crear 7 conexiones
    print("\n--- Creación de 7 conexiones ---")
    c1 = Connection(za, zb)
    c2 = Connection(za, zc)
    c3 = Connection(zb, zd)
    c4 = Connection(zc, zd, max_link_capacity=2)
    c5 = Connection(zd, ze)
    c6 = Connection(ze, zf)
    c7 = Connection(zf, zg, max_link_capacity=3)

    all_connections = [c1, c2, c3, c4, c5, c6, c7]
    print(f"Conexiones creadas: {len(all_connections)} (esperado: 7)")
    for c in all_connections:
        print(f"  {c.name} | max_link_capacity={c.max_link_capacity} | drone_count={c.drone_count}")

    # drone_in incrementa drone_count correctamente
    print("\n--- drone_in incrementa drone_count ---")
    c1.drone_in()
    print(f"drone_in en {c1.name}: drone_count={c1.drone_count} (esperado: 1)")

    # drone_out decrementa drone_count correctamente
    print("\n--- drone_out decrementa drone_count ---")
    c1.drone_out()
    print(f"drone_out en {c1.name}: drone_count={c1.drone_count} (esperado: 0)")

    # is_full retorna False cuando hay capacidad
    print("\n--- is_full cuando NO está llena ---")
    print(f"is_full {c1.name} (drone_count=0, max=1): {c1.is_full()} (esperado: False)")

    # is_full retorna True cuando está al límite
    print("\n--- is_full cuando SÍ está llena ---")
    c1.drone_in()
    print(f"is_full {c1.name} (drone_count=1, max=1): {c1.is_full()} (esperado: True)")
    c1.drone_out()

    # get_otherside_zone con zona válida (zone1)
    print("\n--- get_otherside_zone con zona1 válida ---")
    result = c1.get_otherside_zone(za)
    print(f"get_otherside_zone({za.name}) en {c1.name}: {result.name if result else None} (esperado: {zb.name})")

    # get_otherside_zone con zona válida (zone2)
    print("\n--- get_otherside_zone con zona2 válida ---")
    result2 = c1.get_otherside_zone(zb)
    print(f"get_otherside_zone({zb.name}) en {c1.name}: {result2.name if result2 else None} (esperado: {za.name})")

    # get_otherside_zone con zona inválida
    print("\n--- get_otherside_zone con zona inválida ---")
    result_invalid = c1.get_otherside_zone(zc)
    print(f"get_otherside_zone({zc.name}) en {c1.name}: {result_invalid} (esperado: None)")

    # Stress: drone_in intenta agregar 10 drones, max_link_capacity=2
    print("\n--- Stress: drone_in 10 veces en conexión con max_link_capacity=2 ---")
    print(f"Intentando agregar 10 drones a {c4.name} (max_link_capacity={c4.max_link_capacity})")
    for i in range(10):
        c4.drone_in()
        print(f"  drone_in #{i + 1}: drone_count={c4.drone_count}")
    print(f"drone_count final: {c4.drone_count} (esperado: {c4.max_link_capacity})")
    c4.drone_count = 0

    # Stress: drone_out intenta decrementar por debajo de 0
    print("\n--- Stress: drone_out 5 veces en conexión vacía ---")
    print(f"Intentando drone_out 5 veces en {c1.name} (drone_count={c1.drone_count})")
    for i in range(5):
        c1.drone_out()
        print(f"  drone_out #{i + 1}: drone_count={c1.drone_count}")
    print(f"drone_count final: {c1.drone_count} (esperado: 0)")

    # ============================================================
    # BLOQUE: ZONE
    # ============================================================

    print("\n" + "=" * 60)
    print("BLOQUE: ZONE")
    print("=" * 60)

    # Crear 10 zonas con distintas propiedades
    print("\n--- Creación de 10 zonas ---")
    zones = [
        Zone("start",     0,  0, zone_type="normal",     color="green"),
        Zone("alpha",     1,  2, zone_type="priority",   color="blue"),
        Zone("beta",      3,  1, zone_type="restricted", color="red"),
        Zone("gamma",     4,  4, zone_type="blocked"),
        Zone("delta",     5,  0, max_drones=3),
        Zone("epsilon",   6,  3, zone_type="priority",   color="yellow"),
        Zone("zeta",      7,  1, max_drones=2),
        Zone("eta",       8,  5),
        Zone("theta",     9,  2, zone_type="restricted", color="orange"),
        Zone("end",      10, 10, zone_type="normal",     color="green"),
    ]
    print(f"Zonas creadas: {len(zones)} (esperado: 10)")
    for z in zones:
        print(f"  {z.name} | type={z.zone_type} | max_drones={z.max_drones} | color={z.color}")

    # add_connection agrega correctamente
    print("\n--- add_connection agrega una conexión a la zona ---")
    conn_zone_test = Connection(zones[0], zones[1])
    zones[0].add_connection(conn_zone_test)
    print(f"Conexiones en {zones[0].name}: {len(zones[0].connections)} (esperado: 1)")

    # add_connection no agrega duplicados
    print("\n--- add_connection no agrega conexión duplicada ---")
    zones[0].add_connection(conn_zone_test)
    print(f"Conexiones en {zones[0].name} tras agregar duplicado: {len(zones[0].connections)} (esperado: 1)")

    # drone_in incrementa drone_count
    print("\n--- drone_in incrementa drone_count ---")
    zones[0].drone_in()
    print(f"drone_in en {zones[0].name}: drone_count={zones[0].drone_count} (esperado: 1)")

    # drone_out decrementa drone_count
    print("\n--- drone_out decrementa drone_count ---")
    zones[0].drone_out()
    print(f"drone_out en {zones[0].name}: drone_count={zones[0].drone_count} (esperado: 0)")

    # is_full retorna False cuando hay capacidad
    print("\n--- is_full cuando NO está llena ---")
    print(f"is_full {zones[0].name} (drone_count=0, max=1): {zones[0].is_full()} (esperado: False)")

    # is_full retorna True cuando está al límite
    print("\n--- is_full cuando SÍ está llena ---")
    zones[0].drone_in()
    print(f"is_full {zones[0].name} (drone_count=1, max=1): {zones[0].is_full()} (esperado: True)")
    zones[0].drone_out()

    # Stress: drone_in intenta agregar 10 drones, max_drones=3
    print("\n--- Stress: drone_in 10 veces en zona con max_drones=3 ---")
    z_stress = zones[4]  # delta, max_drones=3
    print(f"Intentando agregar 10 drones a {z_stress.name} (max_drones={z_stress.max_drones})")
    for i in range(10):
        z_stress.drone_in()
        print(f"  drone_in #{i + 1}: drone_count={z_stress.drone_count}")
    print(f"drone_count final: {z_stress.drone_count} (esperado: {z_stress.max_drones})")
    z_stress.drone_count = 0

    # Stress: drone_out intenta decrementar por debajo de 0
    print("\n--- Stress: drone_out 5 veces en zona vacía ---")
    print(f"Intentando drone_out 5 veces en {zones[0].name} (drone_count={zones[0].drone_count})")
    for i in range(5):
        zones[0].drone_out()
        print(f"  drone_out #{i + 1}: drone_count={zones[0].drone_count}")
    print(f"drone_count final: {zones[0].drone_count} (esperado: 0)")

    # ============================================================
    # BLOQUE: GRAPH
    # ============================================================

    print("\n" + "=" * 60)
    print("BLOQUE: GRAPH")
    print("=" * 60)

    graph = Graph()

    # Agregar las 10 zonas al grafo
    print("\n--- Agregar 10 zonas al grafo ---")
    for z in zones:
        graph.add_zone(z)
    print(f"Zonas en el grafo: {len(graph.zones)} (esperado: 10)")

    # Zona duplicada no se agrega
    print("\n--- Zona duplicada no se agrega ---")
    graph.add_zone(zones[0])
    print(f"Zonas tras agregar duplicado: {len(graph.zones)} (esperado: 10)")

    # Crear y agregar 7 conexiones al grafo
    print("\n--- Agregar 7 conexiones al grafo ---")
    graph_conns = [
        Connection(zones[0], zones[1]),
        Connection(zones[1], zones[2]),
        Connection(zones[2], zones[3]),
        Connection(zones[3], zones[4], max_link_capacity=2),
        Connection(zones[4], zones[5]),
        Connection(zones[5], zones[6], max_link_capacity=3),
        Connection(zones[7], zones[9]),
    ]
    for conn in graph_conns:
        conn.zone1.add_connection(conn)
        conn.zone2.add_connection(conn)
        graph.add_connection(conn)
    print(f"Conexiones en el grafo: {len(graph.connections)} (esperado: 7)")

    # Conexión duplicada no se agrega
    print("\n--- Conexión duplicada no se agrega ---")
    graph.add_connection(graph_conns[0])
    print(f"Conexiones tras agregar duplicado: {len(graph.connections)} (esperado: 7)")

    # Imprimir estado final: cada conexión con sus dos zonas
    print("\n--- Estado final del grafo ---")
    print(f"Total zonas:      {len(graph.zones)}")
    print(f"Total conexiones: {len(graph.connections)}")
    print("\nConexiones registradas:")
    for conn in graph.connections:
        print(f"  {conn.name:30} {conn.zone1.name} <-> {conn.zone2.name} | max_link_capacity={conn.max_link_capacity}")

    print("\nZonas y sus conexiones:")
    for name, zone in graph.zones.items():
        conn_names = [c.name for c in zone.connections]
        print(f"  {name:12} conexiones={conn_names}")

    # ============================================================
    # BLOQUE: DRONE
    # ============================================================

    print("\n" + "=" * 60)
    print("BLOQUE: DRONE")
    print("=" * 60)

    # Crear un dron con id, path e reservations vacías
    print("\n--- Creación de dron con path e id ---")
    drone_path = ["start", "alpha", "waiting", "beta", "gamma", "end"]
    d1 = Drone("D1", drone_path, {})
    print(f"Dron creado: id={d1.id} | is_active={d1.is_active} | path={d1.path}")

    # get_position con turno válido
    print("\n--- get_position con turnos válidos ---")
    for t in range(1, len(drone_path) + 1):
        pos = d1.get_position(t)
        print(f"  get_position({t}): {pos} (esperado: {drone_path[t - 1]})")

    # get_position con turno 0 (inválido)
    print("\n--- get_position con turno 0 (inválido) ---")
    pos_zero = d1.get_position(0)
    print(f"get_position(0): {pos_zero} (esperado: None)")

    # get_position con turno mayor que el path (inválido)
    print("\n--- get_position con turno fuera de rango ---")
    pos_out = d1.get_position(99)
    print(f"get_position(99): {pos_out} (esperado: None)")

    # get_position con turno negativo (inválido)
    print("\n--- get_position con turno negativo (inválido) ---")
    pos_neg = d1.get_position(-1)
    print(f"get_position(-1): {pos_neg} (esperado: None)")

    # deactive y verificar que get_position retorna None
    print("\n--- deactive y get_position posterior ---")
    d1.deactive()
    print(f"is_active tras deactive: {d1.is_active} (esperado: False)")
    pos_after = d1.get_position(1)
    print(f"get_position(1) tras deactive: {pos_after} (esperado: None)")

    print("\n" + "=" * 60)
    print("Tests completados.")
    print("=" * 60)


if __name__ == "__main__":
    main()

---
proyecto: Fly-in
version_subject: 1.4
generado: 2026-06-18
tags: [42, fly-in, handoff]
---

# HANDOFF.md — Fly-in

> [!info] Propósito
> Resumen completo del subject para agentes que se incorporan al proyecto.
> No releer el PDF si este archivo existe.

---

## Descripción

Diseñar un sistema de routing eficiente que navegue múltiples drones a través de zonas conectadas (grafo), minimizando el número de turnos de simulación, respetando restricciones de movimiento y capacidad.

**Input:** archivo de mapa con zonas y conexiones
**Output:** simulación turno a turno de los movimientos de cada dron hasta que todos llegan al destino

---

## Restricciones duras

> [!danger] Violaciones = fallo automático en peer-review
> - **Prohibidas** librerías de grafos: `networkx`, `graphlib`, etc.
> - **Obligatorio** 100% typesafe: `flake8` + `mypy` sin errores
> - **Obligatorio** 100% orientado a objetos
> - Todos los archivos en la **raíz del repositorio Git**
> - El programa no debe crashear con excepciones no manejadas

---

## Formato del archivo de entrada

```
nb_drones: <positive_integer>
start_hub: <name> <x> <y> [metadata]
end_hub:   <name> <x> <y> [metadata]
hub:       <name> <x> <y> [metadata]
connection: <zone1>-<zone2> [metadata]
# comentario (ignorado)
```

**Ejemplo:**
```
nb_drones: 5
start_hub: hub 0 0 [color=green]
end_hub: goal 10 10 [color=yellow]
hub: roof1 3 4 [zone=restricted color=red]
hub: corridorA 4 3 [zone=priority color=green max_drones=2]
connection: hub-roof1
connection: corridorA-tunnelB [max_link_capacity=2]
```

### Reglas del parser

- Primera línea: `nb_drones: <positive_integer>` (obligatorio)
- Exactamente 1 `start_hub` y 1 `end_hub`
- Nombres de zona: sin guiones, sin espacios, únicos
- Coordenadas: enteros
- Conexiones solo referencian zonas ya definidas
- Conexión duplicada (`a-b` == `b-a`) → error
- Metadata entre `[...]`, puede estar en cualquier orden
- Tipo de zona inválido → error de parsing
- Capacidades (`max_drones`, `max_link_capacity`): enteros positivos
- Cualquier error de parsing → parar + mensaje claro con línea y causa

### Metadata de zonas

| Campo | Valores | Default |
|---|---|---|
| `zone=<type>` | `normal`, `blocked`, `restricted`, `priority` | `normal` |
| `color=<value>` | cualquier string una palabra | none |
| `max_drones=<n>` | entero positivo | 1 |

### Metadata de conexiones

| Campo | Default |
|---|---|
| `max_link_capacity=<n>` | 1 |

---

## Tipos de zona y coste de movimiento

| Tipo | Coste | Descripción |
|---|---|---|
| `normal` | 1 turno | Estándar |
| `priority` | 1 turno | Preferida en pathfinding |
| `restricted` | 2 turnos | El dron ocupa la conexión durante el tránsito |
| `blocked` | ∞ | Inaccesible — ningún path puede usarla |

---

## Reglas de ocupación

- Default: máximo **1 dron por zona** por turno
- `max_drones=N` → hasta N drones simultáneos
- **Excepción start:** todos los drones empiezan aquí (pueden compartir)
- **Excepción end:** múltiples drones pueden llegar → considerados entregados
- Drones que **salen** de una zona liberan capacidad **ese mismo turno**
- `max_link_capacity`: límite de drones que atraviesan una conexión simultáneamente (default 1)
- Un dron NO puede moverse a una zona si excedería su capacidad máxima

---

## Mecánica de turnos

Cada turno, cada dron puede:

1. **Moverse** a zona adyacente conectada (si hay capacidad)
2. **Iniciar tránsito** hacia zona `restricted` (ocupa la conexión, llega al turno siguiente — MUST arrive, no puede esperar en la conexión)
3. **Esperar** (no se mueve)

> [!warning] Zona restricted
> El dron ocupa la conexión durante el tránsito y DEBE llegar al destino en el siguiente turno. No puede esperar en la conexión para que se libere espacio en destino.

La simulación debe:
- Prevenir conflictos y deadlocks
- Evaluar estado turno a turno
- Drones que salen liberan capacidad ese mismo turno

---

## Formato de output

Una línea por turno. Movimientos separados por espacios:

```
D<ID>-<zone>         → dron llegó a zona
D<ID>-<connection>   → dron en tránsito hacia zona restricted
```

- Drones que no se mueven: omitidos de esa línea
- Drones que llegan al end: entregados, ya no se trackean
- Simulación termina cuando todos los drones llegaron al end

**Ejemplo:**
```
D1-roof1 D2-corridorA
D1-roof2 D2-tunnelB
D1-goal D2-goal
```

---

## Requisitos del algoritmo

- Drones se mueven **simultáneamente**
- Distribuir drones en múltiples paths
- Espera estratégica cuando movimiento no es posible
- Evitar conflictos y deadlocks
- Considerar: costes por tipo de zona, scheduling de turnos, estructura del grafo, capacidades
- Adaptable: distintos mapas → distintas estrategias

### Visual representation (obligatorio)

Al menos una de:
- Colored terminal output (movimientos + estados de zonas)
- Interfaz gráfica con red y posiciones de drones
- Ambas

---

## Benchmarks de rendimiento

| Dificultad | Límite general | Mapa | Drones | Target |
|---|---|---|---|---|
| Easy | < 10 turnos | Linear path | 2 | ≤ 6 |
| Easy | | Simple fork | 4 | ≤ 8 |
| Easy | | Basic capacity | 4 | ≤ 6 |
| Medium | 10–30 turnos | Dead end trap | 5 | ≤ 12 |
| Medium | | Circular loop | 6 | ≤ 15 |
| Medium | | Priority puzzle | 5 | ≤ 12 |
| Hard | < 60 turnos | Maze nightmare | 8 | ≤ 30 |
| Hard | | Capacity hell | 12 | ≤ 35 |
| Hard | | Ultimate challenge | 15 | ≤ 45 |
| **Challenger** | (bonus) | Impossible Dream | 25 | **< 45** |

> [!note]
> Los mapas de evaluación pueden ser distintos a los del subject.

---

## Bonus

Evaluado solo si todos los requisitos obligatorios están cumplidos:

- **Exceptional performance:** cumplir exactamente todos los targets de los mapas provistos
- **Challenger map:** resolver Impossible Dream en < 45 turnos

---

## Makefile (obligatorio)

| Regla | Descripción |
|---|---|
| `install` | Instalar dependencias (pip/uv/pipx) |
| `run` | Ejecutar script principal |
| `debug` | Ejecutar con pdb |
| `clean` | Eliminar `__pycache__`, `.mypy_cache` |
| `lint` | `flake8 .` + `mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs` |
| `lint-strict` | `flake8 .` + `mypy . --strict` (recomendado) |

---

## README (en inglés, obligatorio)

Primera línea:
> *This project has been created as part of the 42 curriculum by \<login\>/[...]*

Secciones obligatorias:
- **Description**: objetivo y overview
- **Instructions**: compilación, instalación, ejecución
- **Resources**: referencias + descripción del uso de IA (qué tareas, qué partes)
- **Algorithm**: descripción de decisiones de algoritmo y estrategia de implementación
- **Visual Representation**: documentación de las features visuales

---

## Entrega

- Git repository
- Todos los archivos en la **raíz** del repositorio
- Durante peer-review: pueden pedir explicar código o escribir código en vivo
- Prepararse para modificaciones menores del proyecto durante la evaluación

---

## Briefing para el siguiente agente

**Fecha:** 2026-07-06 (actualizado)
**Contexto al momento del handoff:** ver PROJECT.md para el detalle fino del Bloque 3

### Qué se hizo

- FASE 0 y FASE 1 completas. Todos los bloques diseñados y documentados en `PROJECT.md`.
- FASE 2 en progreso:
  - **Bloque 1 (Modelo del grafo):** `Zone`, `Connection`, `Graph` — implementados y testeados en `tests/test_bloque_1.py`
  - **Bloque 4 parcial — `Drone`:** implementado y testeado en `tests/test_bloque_1.py`
  - **Bloque 2 — Parser:** ✅ completo y testeado (`tests/test_bloque_2.py` + `tests/files_test/`). mypy/flake8 limpios.
  - **Bloque 3 — Dijkstra:** turn-aware (enfoque A) casi completo. Puntos 1/2/4 hechos; **falta el punto 3 (arista de espera)**, partir 5 líneas E501, y tests. Ver detalle y decisiones abiertas en `PROJECT.md` (sección Bloque 3).

### Estructura de archivos actual

```
Fly-In/
  clases/
    graph/
      zone.py
      connection.py
      graph.py
    drone/
      drone.py
    parser/
      parser.py
  tests/
    test_bloque_1.py
  workflow/
    SYSTEM.md
    HANDOFF.md
    PROJECT.md
```

> [!warning] Los archivos están en subdirectorios por ahora. Al llegar a FASE 3 se mueven todos a la raíz del repositorio Git.

### Decisiones de diseño importantes

- `Drone` solo recibe `id` como argumento. `path` y `reservations` se asignan después vía `add_path()` y `add_reservation()` — el Parser crea los drones vacíos y la Simulation los completa.
- `Drone.path` es `List[Union[Zone, Connection]]` (objetos, no nombres — actualizado 2026-07-02). `Dijkstra.dijkstra()` retorna lo mismo. En tramos `restricted` se intercala la `Connection` del tránsito. Turno de espera = repetir la misma `Zone` (sin sentinel `"waiting"`). Al imprimir el output se usa `.name` (zona o conexión).
- `Zone` tiene atributo `relevant: Union[str, None]` — valores `"start_hub"`, `"end_hub"` o `None` (actualizado 2026-06-29: el Parser guarda el token sin los dos puntos vía `[:-1]`, sin remapear a `"start"`/`"end"`). El consumidor (pathfinding/simulación) debe comparar contra `"start_hub"` / `"end_hub"`.
- `reservations` es `Dict[int, Dict[str, int]]` (plano, actualizado 2026-07-06): `reservations[turno][nombre] = drone_count`. Nombres de zona no llevan `-` y los de conexión sí, así que no colisionan → no hace falta separar zonas/conexiones en capas.
- El Parser retorna `tuple[Graph, List[Drone]]` — crea los drones vacíos (sin path) listos para que la Simulation calcule sus rutas.

### Siguiente paso

**Bloque 3 — Dijkstra está funcionalmente completo y su archivo de tests (`tests/test_bloque_3.py`) ya está escrito y aprobado por el estudiante — pero nunca se pudo ejecutar.** Hay un bloqueo crítico sin relación con Dijkstra que impide correr absolutamente cualquier test del proyecto. Ver detalle completo en `PROJECT.md` (sección Bloque 3).

> [!danger] PRIMER PASO OBLIGATORIO AL RETOMAR — antes de cualquier otra cosa
> `clases/graph/zone.py` y `clases/graph/connection.py` importan la clase del otro solo bajo `if TYPE_CHECKING:`, pero la usan como anotación de tipo real en las firmas de métodos → `NameError: name 'Connection' is not defined` al importar, en tiempo de ejecución. Esto bloquea **todo** (incluso `tests/test_bloque_1.py`, que nunca se pudo correr). `mypy`/`flake8` no lo detectan (no ejecutan el código).
>
> **Fix de una línea por archivo:** agregar `from __future__ import annotations` al principio de `zone.py` y `connection.py` (antes de los demás imports). El estudiante debe aplicarlo (regla: el código lo escribe él).
>
> Una vez aplicado, correr `python tests/test_bloque_3.py` y confirmar que los valores esperados (calculados a mano durante el diseño del test) coinciden con la ejecución real.

En orden, lo que sigue después de destrabar esto:

1. **Correr `tests/test_bloque_3.py`** y revisar los `[OK]`/`[FAIL]`. Dos `[FAIL]` son **esperados a propósito** (hallazgos ya documentados, no bugs del test):
   - Sección 8 (`run_cascading_congestion_stress_case`): la longitud del path no va a coincidir con los turnos reales cuando hay 2+ esperas seguidas en `start` — bug real en `rebuild()` (ver `PROJECT.md`).
   - Sección 7 (`run_unreachable_end_case`): el mensaje de la excepción probablemente sea el de `max_moves`, no `"Unreacheble end node"` — posible código muerto (ver `PROJECT.md`).
   Discutir con el estudiante si/cómo corregir estos dos hallazgos antes de pasar a Bloque 4, o si se documentan como deuda técnica y se sigue adelante.
2. **Bloque 4 — Simulation:** es quien **produce** `reservations` (`Dict[int, Dict[str, int]]` plano). Diseño ya confirmado: crea una instancia **nueva** de `Dijkstra` por cada dron (nunca reutiliza el objeto), le pasa el `reservations` actualizado de ese momento, y hace `drone.add_path(resultado)`. Esto también resuelve la duda que tuvo el estudiante sobre si `Drone` necesitaba un atributo de algoritmo — no lo necesita, es un contenedor de datos; `Simulation` orquesta.
3. **Tests de Bloque 4 — CAMBIO DE CONVENCIÓN:** el estudiante decidió (2026-07-08) que a partir de aquí los tests usan un **framework recomendado por el subject**, no el estilo manual/print de Bloques 1-3. Falta revisar el PDF del subject para confirmar si menciona uno específico (no está en `HANDOFF.md` todavía); si no dice nada, usar `pytest` por default.
4. Menores: `get_connection_to` en `Zone`/`Graph`; revisar dead code `drone_in/out/is_full`.

> [!important] Instrucción para el próximo agente — primer mensaje de la sesión
> Al retomar, el primer mensaje al estudiante debe:
> 1. Recordarle que quedamos en el bloqueo de `Zone`/`Connection` (`NameError` por `TYPE_CHECKING`) — es el primer paso, antes que nada más.
> 2. Confirmar que Bloque 3 (Dijkstra + tests) está implementado y aprobado, pendiente solo de ejecutarse tras el fix.
> 3. Recordar los dos hallazgos ya documentados (rebuild/start, posible código muerto en "Unreacheble end node") para discutir una vez corran los tests.
> 4. Mencionar el cambio de convención de testing para Bloque 4 (framework del subject, no prints).
> Recordar: el estudiante escribe el código; el agente no lo escribe por su cuenta sin acordarlo antes línea a línea. Los tests sí los genera el agente (regla de `SYSTEM.md`), pero después de acordar conceptualmente los casos con el estudiante.

> [!important] Regla de trabajo (repetida por el estudiante): NO proponer soluciones ni escribir código — el estudiante propone diseño/código primero, el agente solo analiza y señala. Ver `SYSTEM.md`.

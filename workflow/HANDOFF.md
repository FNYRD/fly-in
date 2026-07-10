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

**Fecha:** 2026-07-10 (actualizado)
**Contexto al momento del handoff:** ver `PROJECT.md` para el detalle fino de Bloque 4 (Simulation) y de la sección de tests con pytest.

### Qué se hizo

- FASE 0 y FASE 1 completas. Todos los bloques diseñados y documentados en `PROJECT.md`.
- FASE 2 en progreso:
  - **Bloque 1 (Modelo del grafo):** `Zone`, `Connection`, `Graph` — implementados. *(Tests originales borrados intencionalmente, ver abajo.)*
  - **Bloque 4 parcial — `Drone`:** implementado.
  - **Bloque 2 — Parser:** ✅ completo. mypy/flake8 estaban limpios antes de que se borraran los tests.
  - **Bloque 3 — Dijkstra:** ✅ **CERRADO** (turn-aware, enfoque A completo).
  - **Bloque 4 — Simulation:** código escrito en los 4 métodos (`calculating_reservations`, `populate_logs`, `output`, `simulating`), revisado línea por línea con el agente. Varios bugs encontrados y corregidos durante esa revisión — detalle completo en `PROJECT.md` (typo `reservartions`, sobreescritura de dict de reservas en vez de mergear, `.name` sobre `Optional[Connection]` sin guard, orden `add_reservation`/`calculating_reservations` invertido, `add_path()` sin argumento, `print("\n")` duplicando salto de línea).
    > [!danger] NO CONFUNDIR "código escrito" con "Bloque 4 cerrado"
    > **El código de `Simulation` nunca se ejecutó ni una sola vez de punta a punta.** La revisión fue 100% estática (lectura + razonamiento), no hay corrida real contra ningún mapa que confirme que compila, que no crashea, o que el output es correcto. `pytest` ni siquiera llegó a correrse en la sesión (no estaba instalado en el intérprete usado para probar). Bloque 4 se considera **cerrado recién cuando haya al menos una corrida real verificada** (idealmente el caso de test de integración ya diseñado: mapa restricted, 3 drones → turnos 1/2/3) — hasta entonces, tratar cualquier parte de `Simulation` como **no verificada**, con posibles bugs adicionales no detectados en la revisión estática.

> [!warning] Cambio de estrategia de tests (2026-07-10)
> El estudiante **borró intencionalmente** `tests/test_bloque_1.py`, `test_bloque_2.py`, `test_bloque_3.py`, `tests/files_test/` (27 casos) y `ultimo_punto.txt` (sin commitear — recuperables con `git checkout` si hiciera falta, pero la intención es no volver a ese estilo). A partir de Bloque 4, los tests se escriben con **`pytest`** (confirmado válido por el subject, §III.3), no más el estilo manual/print de Bloques 1-3.

### Estructura de archivos actual

```
fly_in/
  clases/
    graph/
      zone.py
      connection.py
      graph.py
    drone/
      drone.py
    parser/
      parser.py
    dijkstra/
      dijkstra.py
    simulation/
      simulation.py
  tests/
    test_pytest.py       ← exploratorio, aprendiendo pytest (ver abajo)
    lazy_tests.py         ← scratch, no relacionado al proyecto
  maps/                   ← mapas de ejemplo provistos/organizados por dificultad
    easy/ medium/ hard/ challenger/ README.md
  Makefile                ← nuevo (2026-07-10), incompleto: solo `test` y `clean`
  fly-in.pdf
  workflow/
    SYSTEM.md
    HANDOFF.md
    PROJECT.md
```

> [!warning] Los archivos siguen en subdirectorios. Al llegar a FASE 3 se mueven todos a la raíz del repositorio Git (requisito duro del subject).

### Decisiones de diseño importantes

- `Drone` solo recibe `id` como argumento. `path` y `reservations` se asignan después vía `add_path()` y `add_reservation()` — el Parser crea los drones vacíos y la Simulation los completa.
- `Drone.path` es `List[Union[Zone, Connection]]` (objetos, no nombres). `Dijkstra.dijkstra()` retorna lo mismo. En tramos `restricted` se intercala la `Connection` del tránsito. Turno de espera = repetir la misma `Zone` (sin sentinel `"waiting"`). Al imprimir el output se usa `.name`.
- `Zone` tiene atributo `relevant: Union[str, None]` — valores `"start_hub"`, `"end_hub"` o `None`.
- `Zone.get_connection(zone_asked: Zone) -> Optional[Connection]` (nombre final, no `get_connection_to` como se había anotado antes) — retorna `None` si no encuentra la conexión; el caller hace `raise RuntimeError` si eso pasa en un contexto donde Dijkstra ya garantizó que la conexión existe (path válido) — un `None` ahí es estado corrupto, no un caso de negocio.
- `reservations` es `Dict[int, Dict[str, int]]` (plano): `reservations[turno][nombre] = drone_count`. Nombres de zona no llevan `-` y los de conexión sí, así que no colisionan.
- El Parser retorna `tuple[Graph, List[Drone]]` — crea los drones vacíos (sin path) listos para que la Simulation calcule sus rutas.
- **Invariante probado sobre `Simulation`** (ver `PROJECT.md` para la demostración completa): mientras haya al menos un dron activo en un turno, **siempre** hay alguien moviéndose ese turno (nunca puede estar todo el fleet esperando simultáneamente) — esto es lo que garantiza que `populate_logs` pueda indexar `self.logs` posicionalmente con `len(self.logs)` sin gaps. Se prueba por inducción: toda espera se rastrea a un dron anterior, y la cadena siempre termina en D1, que nunca espera (se calcula con `reservations=None`).

### Siguiente paso

**Bloque 4 — Simulation: código escrito y revisado, sin correr todavía.** El estudiante está aprendiendo pytest en paralelo (ver sección dedicada en `PROJECT.md`, dentro de Bloque 4).

> [!danger] AL RETOMAR — primer chequeo pendiente
> `tests/test_pytest.py` tiene una fixture que arma `route` con `os.path.join(TEST_DIR, "maps/easy", "01_linear_path.txt")`, donde `TEST_DIR` es la carpeta `tests/`. Pero el mapa real vive en `maps/easy/01_linear_path.txt` **en la raíz del repo**, no en `tests/maps/`. Esto probablemente tira `FileNotFoundError` — no se llegó a correr `pytest` en la sesión anterior (no estaba instalado en el intérprete usado). **Primera cosa a verificar.**

En orden, lo que sigue:

1. Confirmar/arreglar la ruta del mapa en `tests/test_pytest.py` y correr `pytest -s tests/test_pytest.py` para ver si `Simulation` funciona de punta a punta con un mapa real.
2. El `assert` actual (`len(simulation.logs) > 0`) es un placeholder — falta que el estudiante defina qué debería pasar exactamente con el mapa de test (turnos, orden de llegada) para escribir un `assert` real.
3. Cubrir el caso de test de integración ya diseñado hace tiempo: mapa `start → conn(cap1) → R(restricted,cap1) → end`, 3 drones → deben transitar la conexión en turnos 1/2/3.
4. Formalizar el archivo final de tests de Bloque 4 (nombre, organización) una vez el estudiante esté cómodo con pytest — `test_pytest.py` es exploratorio.
5. Completar el `Makefile` (faltan `install`, `run`, `debug`, `lint`, `lint-strict` — ver Chapter III.2 del subject) — no es urgente, pero está anotado en el checklist de FASE 3 de `PROJECT.md`.
6. Menor: revisar dead code `drone_in/out/is_full/drone_count` en Zone/Connection (si `reservations` cubre toda la ocupación).

> [!important] Instrucción para el próximo agente — primer mensaje de la sesión
> Al retomar, el primer mensaje al estudiante debe:
> 1. Confirmar que **Bloque 4 (Simulation) tiene código real en los 4 métodos**, revisado y con varios bugs ya corregidos — no queda en pseudocódigo.
> 2. Señalar el problema de ruta en `tests/test_pytest.py` (arriba) como primer paso concreto a verificar.
> 3. Recordar que el estudiante está aprendiendo pytest recién ahora — no asumir que ya domina fixtures/asserts, pero tampoco repetir la explicación básica si no hace falta.
> Recordar: el estudiante escribe el código; el agente no lo escribe por su cuenta sin acordarlo antes línea a línea. Los tests sí los genera el agente (regla de `SYSTEM.md`), pero después de acordar conceptualmente los casos con el estudiante.

> [!important] Regla de trabajo (repetida varias veces por el estudiante): NO proponer soluciones ni escribir código — el estudiante propone diseño/código primero, el agente solo analiza y señala. Excepción puntual ya ocurrida (2026-07-10): si el estudiante pide explícitamente "hazlo vos" después de rondas de señalamiento, el agente puede escribirlo aclarando que es una excepción puntual, no un cambio de regla general. Ver `SYSTEM.md`.

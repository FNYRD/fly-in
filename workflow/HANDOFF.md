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

**Fecha:** 2026-07-20 (actualizado)

### Qué se hizo

- FASE 0, FASE 1 y FASE 2 completas.
- FASE 3 **prácticamente cerrada**:
  - **Paso 0 (Dead code):** ✅
  - **Paso 1 (Mover a raíz):** ✅
  - **Paso 2 (Pygame):** ✅ menú, zonas con nombres, conexiones, drones cuadricóptero, controles manual/auto.
  - **Paso 3 (Main + Docstrings):** ✅ `fly.py` OOP (clase `TerminalSim`) con menú terminal/pygame. Docstrings Google style en 9 archivos. `view.py` OOP (clase `View`). Parser: validación mínimo una conexión, `startswith("#")`.
  - **Paso 4 (Makefile):** ✅ 7 reglas completas (`install`, `run`, `debug`, `clean`, `test`, `lint`, `lint-strict`), todas con venv `.fly_in`, tests excluidos de lint.
  - **Paso 5 (Linting):** ✅ `flake8`, `mypy` y `lint-strict` pasan sin errores.
  - **Paso 6 (Opción terminal/pygame):** ✅ menú en `fly.py`.
  - **Paso 7 (Tests contra la hoja de evaluación `Flyin-ev.pdf`):** ✅ cerrado. 19 tests pasando. Cubiertas: Zone occupancy, Movement costs (4 tests con grafos a mano), Connection capacity, formato de output. Edge cases / error handling se demuestran en vivo (no automatizados). Visual Representation verificada a mano. **Tests refactorizados (2026-07-20): tipado completo, `flake8` + `mypy --strict` limpios** por coherencia con el resto del proyecto (aunque no son entregable).
  - **Paso 8 (README):** ✅ escrito completo en inglés (2026-07-20), 7 secciones: Description, Instructions, Resources (incl. uso de IA), Algorithm, Visual Representation, Example input/output. La sección se llama `Algorithm` (el subject solo pide el contenido, no un heading exacto; decisión del estudiante).
  - **Paso 9 (`.gitignore` + limpiar repo):** ✅ commiteado. Venv desindexado (3415 → 33 archivos trackeados).

### Revisión final (2026-07-20)

Recorrida la evaluation sheet completa. Verificado: OOP, `flake8`, `mypy --strict`, grafo custom, parser + error handling (12 casos malformados → `ValueError`/`OSError`, todos capturados), formato de output, 19 tests, rendimiento (**todos los targets; challenger 43<45** → bonus exceptional performance cubierto).

**Bugs encontrados y corregidos en la revisión:**
- **Crash `EOFError`/`KeyboardInterrupt`** (Ctrl-D / Ctrl-C) no capturado en `fly.py:menu()` → traceback no controlado = flag nota 0 de la hoja. Corregido con `except (EOFError, KeyboardInterrupt): print("The simulation was stopped abruptly")`. De paso se borró el `except FileNotFoundError` final (código muerto, ya cubierto en la tupla de arriba).
- **Opción de menú inválida** (ej. `3`) quedaba muda → añadido `case _: raise ValueError("Wrong option!")`.

### Estructura de archivos actual

```
fly_in/
  zone.py, connection.py, graph.py   ← modelo del grafo
  drone.py                            ← contenedor de datos del dron
  parser.py                           ← lee archivo de mapa
  dijkstra.py                         ← pathfinding turn-aware
  simulation.py                       ← orquesta paths y reservas
  view.py                             ← visualización pygame (clase View)
  fly.py                              ← entry point (clase TerminalSim + menú)
  conftest.py                         ← marca raíz para pytest
  Makefile                            ← completo (7 reglas)
  views.jpg                           ← imagen de fondo para pygame
  README.md                           ← VACÍO (0 bytes) — pendiente
  DEFENSA.md                          ← guion completo del peer-review (no entregable)
  tests/
    test_pytest.py                    ← 19 tests (3 correctitud + 4 movement costs
                                        + 1 connection capacity + 1 output format
                                        + 10 benchmark)
  maps/
    easy/ medium/ hard/ challenger/
    extra/                            ← mapas hechos para tests
  fly-in.pdf
  Flyin-ev.pdf                        ← hoja de evaluación del peer-review
  workflow/
    SYSTEM.md, HANDOFF.md, PROJECT.md, dossier_pygame.md
```

> [!info] Leer también `DEFENSA.md` (en la raíz del proyecto, no en `workflow/`)
> Guion completo del peer-review escrito el 2026-07-18: arquitectura, Dijkstra turn-aware explicado a fondo (con una traza paso a paso de la arista de espera y de `rebuild`), el import circular, el modelo de reservas, las preguntas del subject con respuesta, la guía del live coding `--capacity-info` y las debilidades conocidas.
> **Es la fuente más completa sobre cómo funciona el proyecto.** No es entregable: está en español y es documentación interna.

### Siguiente paso

El proyecto se dio por **cerrado** (2026-07-20). Todo lo obligatorio está hecho. Pendiente antes de / durante la entrega:

1. **Quitar del repo antes de entregar** (lo hace el estudiante): `fly-in.pdf`, `Flyin-ev.pdf` (subject y hoja de evaluación, riesgo del flag "only requested files"), la carpeta `workflow/` y `DEFENSA.md`. Se necesitan en el repo hasta justo antes de la entrega, por eso no se han sacado aún.
2. **En la máquina de 42:** cambiar `requirements.txt` de `pygame-ce` → `pygame`; correr `make lint` y decidir los `# type: ignore[attr-defined]` de `view.py:50,52` (sobran con pygame-ce, pueden ser necesarios con los stubs de pygame).
3. **Ensayar el live coding** `--capacity-info` sobre una copia del proyecto (guía en `DEFENSA.md` §12).

> [!note] Entorno (2026-07-20)
> El venv `.fly_in` se había borrado del disco; recreado con `make install`. `make test` / `make lint` funcionan.

> [!success] RESUELTO (2026-07-18) — `.gitignore` y venv desindexado
> El venv `.fly_in/` estaba commiteado entero (3371 de 3415 archivos trackeados) y no había `.gitignore`, que el subject exige en III.3. La hoja avisa en Preliminaries: *"Check that only the requested files are available in the git repository. **If not, the evaluation stops here.**"*
> Hecho: `.gitignore` creado (venv, artefactos Python, cachés, `.DS_Store`) y desindexados `.fly_in/`, los `.DS_Store`, `workflow/.obsidian/` y `tests/lazy_tests.py`. **De 3415 a 37 archivos trackeados**, venv intacto en disco, 19 tests pasando.
> **Ojo: está en el índice, sin commitear.** Y el venv seguirá en el historial aunque se commitee (limpiarlo del todo requeriría reescribir la historia).

> [!danger] RECORDAR AL ESTUDIANTE EN LA MÁQUINA DE 42 (anotado 2026-07-18)
> Allá usará **pygame** (no pygame-ce) y un **Python menor**. Al llegar hay que:
> 1. Cambiar `requirements.txt` de `pygame-ce` a `pygame` (ce se eligió solo porque el original no compila en Python 3.14, que es el de la máquina actual).
> 2. Correr `make lint` y decidir sobre los `# type: ignore[attr-defined]` de `view.py:50` y `view.py:52`. Con pygame-ce sobran y hacen fallar el lint; con los stubs de pygame pueden ser necesarios. **Se dejan puestos a propósito** hasta comprobarlo allá.
>
> Detalle ya comprobado: los `# type: ignore` **no están prohibidos** por el subject ni por la hoja de evaluación. El Makefile obligatorio incluye `--warn-unused-ignores`, que solo rechaza los que sobran.

> [!warning] Deuda menor en los tests (2026-07-18)
> - `maps/extra/for_normla_tests.txt` (typo de "normal") es una **copia del mapa challenger** — 25 drones. Funciona como fixture pero no es un mapa "normal"; revisar si es lo que se quiere.
> - La fixture `simulation` traga la excepción con un `print` y luego hace `return sim`: si el parseo o la simulación fallan, `sim` queda sin asignar y revienta con `UnboundLocalError` en vez de un mensaje claro. El segundo `except FileNotFoundError` es además inalcanzable (ya está en la tupla del primero).

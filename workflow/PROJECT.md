---
proyecto: Fly-in
fecha_inicio: 2026-06-18
fase_actual: FASE 2
estado: en_progreso
tags: [42, proyecto]
---

# PROJECT.md

## Fase actual: `FASE 2 — IMPLEMENTACIÓN`

---

## FASE 0 — COMPRENSIÓN

### Input / Output

**INPUT:**
- Archivo de mapa con zonas (hubs) y conexiones

**OUTPUT:**
- Simulación turno a turno: una línea por turno con los movimientos de cada dron

### Restricciones duras

- [ ] Sin librerías de grafos (`networkx`, `graphlib`, etc.)
- [ ] 100% orientado a objetos
- [ ] 100% typesafe: `flake8` + `mypy` sin errores
- [ ] Todos los archivos en la raíz del repositorio Git
- [ ] El programa no debe crashear con excepciones no manejadas

### Conceptos a estudiar

#### Pathfinding con costes (Dijkstra vs BFS)

> [!info] Estado
> dominado

##### Dudas

> [!question] Duda
> [formulada por el agente]

> [!success] Respuesta
> [pegada del chat]

---

## FASE 1 — DISEÑO

### Bloques
*(en orden de dependencia)*

1. Modelo del grafo (zonas, conexiones)
2. Parser
3. Pathfinding
4. Simulación (drones + scheduler)
5. Output visual

---

### Bloque 1 — Modelo del grafo

#### Clases

##### Zone

| Campo | Valor |
|---|---|
| Responsabilidad | Representa una zona del mapa con su tipo, capacidad y estado de ocupación |

**Atributos:**

| Nombre        | Tipo               | Default    |
| ------------- | ------------------ | ---------- |
| `name`        | `str`              | —          |
| `x`           | `int`              | —          |
| `y`           | `int`              | —          |
| `zone_type`   | `str`              | `"normal"` |
| `color`       | `str \| None`      | `None`     |
| `max_drones`  | `int`              | `1`        |
| `drone_count` | `int`              | `0`        |
| `connections` | `List[Connection]` | `[]`       |

**Métodos:**

| Firma                                            | Descripción                         |
| ------------------------------------------------ | ----------------------------------- |
| `add_connection(connection: Connection) -> None` | registra una conexión de esta zona  |
| `drone_in() -> None`                             | incrementa `drone_count`            |
| `drone_out() -> None`                            | decrementa `drone_count`            |
| `is_full() -> bool`                              | retorna `drone_count >= max_drones` |

---

##### Connection

| Campo | Valor |
|---|---|
| Responsabilidad | Representa una conexión bidireccional entre dos zonas con su capacidad y estado |

**Atributos:**

| Nombre              | Tipo   | Default |
| ------------------- | ------ | ------- |
| `name`              | `str`  | —       |
| `zone1`             | `Zone` | —       |
| `zone2`             | `Zone` | —       |
| `max_link_capacity` | `int`  | `1`     |
| `drone_count`       | `int`  | `0`     |

**Métodos:**

| Firma                                    | Descripción                                |
| ---------------------------------------- | ------------------------------------------ |
| `drone_in() -> None`                     | incrementa `drone_count`                   |
| `drone_out() -> None`                    | decrementa `drone_count`                   |
| `is_full() -> bool`                      | retorna `drone_count >= max_link_capacity` |
| `get_otherside_zone(zone: Zone) -> Zone` | dada una zona, retorna la otra             |

---

##### Graph

| Campo | Valor |
|---|---|
| Responsabilidad | Contiene y gestiona todas las zonas y conexiones del mapa |

**Atributos:**

| Nombre        | Tipo               |
| ------------- | ------------------ |
| `zones`       | `Dict[str, Zone]`  |
| `connections` | `List[Connection]` |

**Métodos:**

| Firma                                            | Descripción                                                       |
| ------------------------------------------------ | ----------------------------------------------------------------- |
| `add_zone(zone: Zone) -> None`                   | registra una zona                                                 |
| `add_connection(connection: Connection) -> None` | registra la conexión y llama `zone.add_connection` en ambas zonas |

#### Dependencias

- ninguna

---

### Bloque 2 — Parser

#### Clases

##### Parser

| Campo | Valor |
|---|---|
| Responsabilidad | Lee el archivo de mapa, valida el formato y construye el Graph listo para usar |

**Atributos:**

| Nombre | Tipo |
|---|---|
| `route` | `str` |
| `graph` | `Graph` |
| `drones` | `List[Drone]` |

**Métodos:**

| Firma | Descripción |
|---|---|
| `manufacturing() -> tuple[Graph, List[Drone]]` | orquesta: lee el archivo, despacha cada línea a su `parse_*`, y retorna `(self.graph, self.drones)` |
| `parse_n_drones(...)` | valida y crea los `Drone` mutando `self.drones` |
| `_parse_zone(...)` | parsea una zona y la registra mutando `self.graph` |
| `_parse_connection(...)` | parsea una conexión y la registra mutando `self.graph` |
| `_parse_metadata(raw: str) -> Dict[str, str]` | parsea el bloque `[...]` y retorna clave-valor |

> Decisión (2026-06-26): `manufacturing` **retorna** `tuple[Graph, List[Drone]]`. Los métodos `parse_*` **mutan directamente** `self.graph`/`self.drones` (no retornan el objeto). El que llama recibe el grafo y los drones del valor de retorno.

#### Dependencias

- necesita [[Bloque 1]] porque: crea objetos Zone, Connection y Graph

---

### Bloque 3 — Pathfinding

#### Clases

##### Dijkstra

| Campo | Valor |
|---|---|
| Responsabilidad | Calcula el camino óptimo desde start hasta end consultando el grafo y las reservas por turno |

**Atributos:**

| Nombre | Tipo |
|---|---|
| `graph` | `Graph` |
| `start` | `Zone` |
| `end` | `Zone` |
| `reservations` | `Dict[int, Dict[str, int]]` |

> `reservations[turno]["zona_o_conn"] = drone_count` (plano: nombres de zona sin `-`, de conexión con `-`, no colisionan)

**Métodos:**

| Firma | Descripción |
|---|---|
| `dijkstra() -> List[Union[Zone, Connection]]` | calcula y retorna el path óptimo (start→end); intercala la `Connection` en los tramos `restricted`. Lanza `ValueError` si el end es inalcanzable |

> El coste real se calcula en el momento: `coste_base(zona) + turnos_de_espera`. Si una zona o conexión está llena en turno T, se prueba T+1, T+2... y se suma cada espera al coste antes de insertar en el heap.

#### Dependencias

- necesita [[Bloque 1]] porque: recorre Zone, Connection y Graph
- necesita reservas del [[Bloque 4]] porque: consulta ocupación por turno

---

### Bloque 4 — Simulación

#### Clases

##### Drone

| Campo | Valor |
|---|---|
| Responsabilidad | Contenedor de datos de un dron: identidad, path calculado y reservas usadas |

**Atributos:**

| Nombre | Tipo | Argumento |
|---|---|---|
| `id` | `str` | sí |
| `path` | `List[Union[Zone, Connection]]` | no (se asigna vía `add_path`) |
| `reservations` | `Dict[int, Dict[str, int]]` | no (se asigna vía `add_reservation`) |
| `is_active` | `bool` | no (default `True`) |

> `path` contiene objetos en orden (start→end), tipo `List[Union[Zone, Connection]]`: normalmente `Zone`, pero al entrar a una zona `restricted` se intercala la `Connection` del tránsito (turno en la conexión antes de llegar). Un turno sin movimiento se representa **repitiendo la misma `Zone`** (no con un sentinel `"waiting"`).

**Métodos:**

| Firma | Descripción |
|---|---|
| `get_position(self, turn: int) -> Union[Zone, Connection, None]` | retorna `path[turn-1]` si activo y turno válido, sino `None` |
| `deactive(self) -> None` | marca `is_active = False` |
| `add_path(self, path: List[Union[Zone, Connection]]) -> None` | asigna el path calculado por Dijkstra |
| `add_reservation(self, reservations: Dict[int, Dict[str, int]]) -> None` | guarda snapshot de reservas al momento del cálculo |

---

##### Simulation

| Campo | Valor |
|---|---|
| Responsabilidad | Orquesta el cálculo de paths, gestiona reservas y genera el log de simulación |

**Atributos:** *(actualizado 2026-07-09 para reflejar la implementación real)*

| Nombre | Tipo |
|---|---|
| `graph` | `Graph` |
| `drones` | `List[Drone]` |
| `reservations` | `Union[Dict[int, Dict[str, int]], None]` |
| `start` | `Union[Zone, None]` |
| `end` | `Union[Zone, None]` |
| `logs` | `List[List[str]]` |

> `reservations[turno]["zona_o_conn"] = drone_count` (plano). Tipado con `Union[..., None]` para calzar con el parámetro que espera `Dijkstra` (obliga a un guard de `None` al usarlo internamente).
> `start`/`end` se resuelven en `__init__` con `next((z for z in graph.zones.values() if z.relevant == ...), None)` → de ahí el `Union[Zone, None]` (guard requerido antes de pasarlos a `Dijkstra`).
> `logs[turno]` = lista de strings `"D1-zona"` / `"D1-conn"` para esa línea de output.

> [!note] Divergencia con el diseño original (2026-07-09)
> Se **eliminó `drone_reservations`**: el snapshot de reservas por dron ahora vive dentro del propio `Drone` (vía `add_reservation`), era redundante tenerlo también acá.
> Se reemplazó el atributo `simulation: Dict[int, Dict[str, str]]` por **`logs: List[List[str]]`** (misma info, representación por líneas de output en vez de dict anidado).

**Métodos:** *(renombrados respecto al diseño original)*

| Firma | Descripción |
|---|---|
| `simulating(self) -> None` | orquesta: por cada dron instancia un `Dijkstra` nuevo, le pasa las `reservations` del momento, `add_path` + `add_reservation`, vuelca a `reservations` vía `calculating_reservations` y llena `logs`. (era `calculate`) |
| `calculating_reservations(self, path) -> ...` | recorre el path de un dron y acumula su ocupación turno a turno en `self.reservations` (índice del path = turno de Dijkstra). Return por definir |
| `get_connection(self, zone1, zone2) -> Connection` | helper para hallar la conn entre dos zonas consecutivas en movimientos **normales** (en restricted la conn ya viene en el path). **Pendiente:** mover a `Zone` como `get_connection_to`, y recibir objetos `Zone` en vez de `str` |
| `output(self) -> None` | imprime `logs` línea por turno; omite drones que no se mueven (espera) y los ya entregados. (era `print_log`) |

#### Dependencias

- necesita [[Bloque 1]] porque: usa Graph, Zone, Connection
- necesita [[Bloque 3]] porque: instancia Dijkstra para cada dron

---

### Bloque 5 — Output visual (pygame)

> [!warning] Pendiente
> Diseño aplazado para cuando se llegue a este bloque en Fase 2.
> Usará pygame. Mostrará el mapa y la posición de cada dron por turno usando `simulation_log`.

#### Dependencias

- necesita [[Bloque 4]] porque: consume `simulation` para renderizar

---

## FASE 2 — IMPLEMENTACIÓN

> [!todo] Caso de test pendiente para Bloque 4 (Simulation) — anotado 2026-07-09
> **Mapa:** `start → conn(cap 1) → R(restricted, cap 1) → end`, con **3 drones**.
> **Verificar:** los tres transitan la conexión en turnos **1, 2, 3** (escalonados por la capacidad del link, no 1/3/5). La espera se hace en `start` (sin límite de aforo), NUNCA en la conexión — el subject prohíbe esperar en la conexión hacia una restricted (el tránsito es atómico: arranca → llega al turno siguiente).
> **Por qué:** confirmar que Simulation alimenta `reservations` turno a turno bien, para que `congested_area` escalone por `conn_turn` (turno de tránsito) y por turno de **llegada** (`accumulated_cost`) por separado. Dijkstra ya razona bien; esto prueba la integración. Origen de la duda: distinción flujo (`max_link_capacity`) vs stock (`max_drones`).

### Bloque 1 — Modelo del grafo

#### Zone
- [x] Implementación
- [x] Test

#### Connection
- [x] Implementación
- [x] Test

#### Graph
- [x] Implementación
- [x] Test

### Bloque 4 (parcial) — Drone

#### Drone
- [x] Implementación
- [x] Test

### Bloque 3 — Pathfinding (Dijkstra turn-aware, enfoque A)

Archivo: `clases/dijkstra/dijkstra.py`. Método `dijkstra() -> List[Union[Zone, Connection]]`. **Enfoque A** (turn-aware) sobre B (Simulation inserta esperas): A enruta viendo la ocupación → evita deadlocks. Estado de búsqueda = `(Zone, turno)`; turno = coste acumulado.

**Hecho (revisado, mypy limpio):**
- [x] Base: heap por coste + `penalty` (priority=0 desempata), `real_cost` (normal/priority 1, restricted 2, blocked skip), lazy-deletion, stop en `end`, raise si inalcanzable.
- [x] Intercala la `Connection` del tránsito en tramos `restricted` (en `rebuild`).
- [x] **Punto 1** — estado `(Zone, turno)` en `distances`/`previous`/`visited`; `previous[(M,turnoLlegada)] = (poped, cost)`. Guard de novedad `if (neighbor, acc) not in distances` (no "más barato", porque coste=turno fija el estado).
- [x] **Punto 2** — al evaluar vecino: consulta `reservations` con `.get(turno, {}).get(nombre, 0)`. Zona en turno de **llegada** (`accumulated_cost`), exime start/end vía `not neighbor.relevant`. Conexión en `cost+1` (tránsito). `reservations` ya tipado `Dict[int, Dict[str, int]]` (plano).
- [x] **Punto 4** — stop en `poped == end`; `rebuild((poped, cost), previous)` camina tuplas.

- [x] **Punto 3 — arista de espera** `(N,T)→(N,T+1)`. Implementada (2026-07-08).

> [!info] Decisión tomada (2026-07-07) — mecanismo de la espera
> Cuándo dispararla: cuando `poped` agota el `for conn in poped.connections` (línea 75) sin haber hecho **ningún** `heappush` exitoso (todos los vecinos fallaron por `blocked` o por capacidad llena). En ese caso, en vez de dejar morir el estado, se hace `heappush(priority, (cost + 1, self.penalty(poped), poped))` y se registra `previous[(poped, cost + 1)] = (poped, cost)` — igual que con un vecino normal — para que `rebuild` pueda reconstruir el turno de espera (se ve como la misma `Zone` repetida, consistente con el diseño ya fijado en `Drone.path`).
>
> Sin esto, el estado `(poped, cost)` simplemente desaparece si todos sus vecinos están ocupados, y el algoritmo depende de que otra rama del heap resuelva el problema — puede producir `ValueError` (inalcanzable) en casos que en realidad solo necesitaban esperar.

> [!success] RESUELTO (2026-07-08) — tope de turnos
> Se descartaron `2×path(D1)` y `2×path(dron_anterior)` encadenado (ver histórico abajo) por no aguantar los mapas de congestión extrema (Capacity hell, Impossible Dream). Solución final, con base estructural (no en el resultado de otro dron):
>
> - `max_turn = max(self.reservations.keys(), default=0) if self.reservations else 0` — turno máximo global con datos reales en `reservations`. Por construcción (cada dron ocupa una zona en cada turno de su path, incluso esperando), más allá de `max_turn` no puede existir ninguna reserva — `reservations.get(turno, {})` da `{}` de forma confiable y permanente a partir de ahí.
> - `n_zone = len(self.graph.zones)` — presupuesto de **movimientos** (no turnos de calendario) disponibles una vez pasada la congestión. Un camino simple (sin repetir zona) tiene como máximo `n_zonas` zonas visitadas, así que este presupuesto alcanza sin importar cuántas zonas del camino sean `restricted`.
> - `last_cost` (inicia en `0`) trackea el último `cost` en que se decrementó, para decrementar `n_zone` solo cuando `cost` avanza a un valor **nuevo** (no en cada `heappop`, que puede repetir el mismo turno en ramas distintas).
> - Condición dentro del `while`, tras sacar `poped`: `if cost > max_turn and cost > last_cost: last_cost = cost; n_zone -= 1`, seguido de `if n_zone < 1: raise ValueError(...)`.
>
> **Nota importante (restricted no cuenta doble):** el contador mide movimientos, no turnos — entrar a una zona `restricted` salta `cost` en +2 en vez de +1, pero sigue siendo **un solo** avance de `last_cost` → decrementa `n_zone` en 1, igual que una zona normal. No hay que sumar nada extra por zonas restricted ni duplicar `n_zonas`; el salto de coste ya quedó reflejado en el propio `cost`, no en el contador de movimientos.
>
> **D1 no necesita caso especial:** con `reservations` vacío, `max_turn = 0`, así que el contador se activa desde el primer turno real — mismo mecanismo sirve para todos los drones, congestionados o no, sin lógica separada.
>
> <details><summary>Histórico de candidatos descartados (2026-07-07)</summary>
>
> - Tope fijo arbitrario (`100`, etc.) — sin justificación.
> - `2×path(D1)` — los mapas difíciles (Capacity hell 12 drones ≤35 turnos; Impossible Dream 25 drones <45 turnos) fuerzan esperas muy superiores al doble del camino ideal.
> - `2×path(dron_anterior)` encadenado — mejor que el anterior, pero vulnerable al "efecto acantilado" de teoría de colas cerca de la saturación (un dron más puede forzar un desvío/espera desproporcionada sin ser deadlock real).
> </details>

**Refactors acordados junto con el tope — todos implementados (2026-07-08):**
- [x] `congested_area(...) -> bool` — condiciones de bloqueo por capacidad extraídas a método propio, con `return False` explícito al final (corregido tras detectar que faltaba y rompía mypy).
- [x] Contador de pushes exitosos por vecino (`pushed`, reset a 0 antes del `for`, +1 en cada `heappush` real); si al terminar el `for` sigue en 0 → arista de espera. Sin comprobar duplicados en `distances`/`Set` antes de este push — decidido por simplicidad; no afecta corrección.
- [x] `distances` cambiado de `Dict[Tuple[Zone,int], int]` a `Set[Tuple[Zone,int]]`.

**Bug detectado y corregido en revisión (2026-07-08):** `self.max_turn` en `__init__` llamaba `reservations.keys()` sin proteger el caso `reservations=None` (el caso real de D1) → crasheaba con `AttributeError`. Corregido: `max(reservations.keys(), default=0) if reservations else 0`.

**Confirmado:** `self.max_moves` se muta directamente sobre `self` dentro de `dijkstra()` (no en variable local) — es seguro porque el diseño de Simulation (Bloque 4) crea una instancia **nueva** de `Dijkstra` por cada dron (nunca se reutiliza el mismo objeto para más de un cálculo), así que no hay riesgo de arrastrar estado entre llamadas.

**Pendiente:**
- [x] **E501** — resuelto (2026-07-08): las 2 líneas largas en `congested_area` (antes 194 y 155 caracteres) se partieron, extrayendo `conn_turn` como variable intermedia. `flake8 dijkstra.py` limpio.
- [x] **mypy** — limpio sobre la lógica del archivo. Los 3 `import-not-found` que salen al correr `mypy dijkstra.py` desde `clases/dijkstra/` son esperados: es el problema ya conocido de que los archivos viven en subdirectorios (`clases/graph/...`) en vez de la raíz del repo — se resuelve solo al mover todo a la raíz en FASE 3 (ver Checklist subject). No es un bug de tipado real; correr `mypy .` desde la raíz del proyecto no debería mostrarlo.
- [x] **Tests del Bloque 3** — escrito, **ejecutado y APROBADO** (2026-07-09). Todo verde, `flake8` + `mypy` limpios. Bloque 3 cerrado.
- [ ] Menores: método `get_connection_to(other)` en `Zone`/`Graph` (lo necesita Simulation para hallar la conn entre 2 zonas consecutivas del path); posible dead code `drone_in`/`drone_out`/`is_full`/`drone_count` en Zone/Connection (revisar al diseñar Bloque 4 — si `reservations` cubre la ocupación, se borran con sus tests del Bloque 1).

> [!success] RESUELTO (2026-07-09) — bloqueo de import circular (Zone/Connection/Graph)
> `zone.py`, `connection.py` y `graph.py` importaban la clase del otro solo bajo `if TYPE_CHECKING:` pero la usaban como anotación real en las firmas → `NameError` al definir la clase en runtime (`mypy`/`flake8` no lo detectan porque no ejecutan). Bloqueaba **todos** los tests, incluso Bloque 1.
>
> **Fix aplicado:** `from __future__ import annotations` como primera línea en los **tres** archivos (`graph.py` había quedado sin el fix en la sesión anterior). Difiere la evaluación de anotaciones a texto. `TYPE_CHECKING` se mantiene (lo necesita mypy). Confirmado corriendo `tests/test_bloque_3.py` sin `NameError`.

**Dos hallazgos que estaban abiertos — RESUELTOS (2026-07-09):**
1. **`rebuild()` colapsaba esperas consecutivas en `start` — CORREGIDO.** La condición `if unpacked_before == self.start: break` cortaba ante cualquier predecesor cuya zona fuera `start`, sin mirar el turno → con 2+ esperas seguidas en start (o esperas en start en general) el path quedaba más corto que los turnos reales. **Fix:** se reemplazó por un corte estructural `before = previous.get(after); if before is None: break` — camina hasta el único estado sin predecesor, que es la semilla `(start, 0)` (cada `heappush` va siempre con su `previous[...]`, así que ese es el único hueco). Ahora las esperas se reconstruyen completas y el largo del path coincide con los turnos reales. Verificado en secciones 4, 5, 6-A y 8 del test.
2. **`raise ValueError("Unreacheble end node")` final — código muerto confirmado, se deja como red de seguridad.** La arista de espera se dispara siempre que `pushed == 0`, así que el heap no se vacía solo: el disparador real de "inalcanzable" es el tope de `max_moves` (`"Unreachable end node"`, typo corregido). El `raise` por heap vacío queda inalcanzable en la práctica; se mantiene como defensa por si un refactor futuro cambia la condición de espera. Decisión del estudiante: dejarlo.

**Depende de Bloque 4:** la etapa de reservas solo se prueba de verdad cuando `Simulation` **produzca** `reservations`. Dijkstra la recibe como snapshot estático (solo lee); Simulation la posee y la actualiza tras cada dron. Estructura plana: `Dict[int, Dict[str, int]]` = `[turno][nombre]=count`.

**Conceptos ya asentados con el estudiante:** Dijkstra no "camina" (los pops saltan, `previous` mantiene el árbol); turno = coste acumulado; espera = arista que compite por coste; el mismo estado `(zona,turno)` siempre cuesta lo mismo (por eso el guard es de novedad, no de coste).

**Decisión del estudiante para Bloque 4 (2026-07-08):** a partir de Bloque 4 (Simulation), los tests van a escribirse con un **framework de testing**, no con el estilo manual/print de Bloques 1-3. **Confirmado en el PDF del subject (§III.3, pág. 6, 2026-07-09):** *"Use frameworks like **pytest or unittest** for unit tests, covering edge cases."* → `pytest` es válido y recomendado por el propio subject. Duda cerrada.

**Invariante crítico a respetar en Bloque 4 (Simulation) — anotado 2026-07-09:** al construir `reservations`, un dron reserva una zona **solo** los turnos en que su path lo pone ahí; el turno en que se mueve a la siguiente zona **ya no cuenta** en la anterior (cuenta en la destino). Esto implementa la regla del subject §VII.3 *"drones moving out free up capacity for that same turn"*. Sale automático si se recorre el path posición por posición (`get_position(turno)`), sin solapar dos zonas en el mismo turno. Si se violara (contar al dron en la zona el turno que la deja), se bloquearía injustamente al que llega en la llegada exacta. Test sugerido: A sale de una restricted en T y B entra a esa misma restricted en T → válido.

### Bloque 2 — Parser (en progreso)

Método principal: `manufacturing(self) -> None` (puebla `self.graph` y `self.drones`, no retorna).

Esqueleto del bucle listo y aprobado: guardia de línea vacía/comentario + cadena `if/elif` despachando por `line_processed[0]` (`nb_drones:`, `"hub" in ...`, `connection:`, `else` → raise).

- [x] Rama `nb_drones:` — completa: duplicado, `len(line_processed) != 2`, dígito + `> 0`, creación de drones, y guardia "1ª línea". Usa `len(self.drones)` como única señal de "ya declarado" (sin variable `flag`).
- [x] Rama hubs (`_parse_zones`) — completa: dispatch valida token exacto (`hub:`/`start_hub:`/`end_hub:`), nombres únicos + sin `-`, coordenadas enteras (negativas incluidas), `relevant` solo en start/end (guarda token sin `:` vía `[:-1]`), `add_zone` único al final. Post-validación `len(self.start_end) != 2` tras el bucle en `manufacturing`.
- [x] `_parse_metadata` — completa: valida `[...]` por posición, parte por `=`, `match` por clave (`zone`/`color`/`max_drones`), **muta el objeto `Zone` directamente** (`-> None`, sin dict intermedio).
- [x] Rama `connection:` (`_parse_connections`) — completa: `len` 2-3, split por `-` (== 2), zonas existen vía `.get()`, dedup recorriendo `z1.connections` con `get_otherside_zone(z1) == z2` (cubre ambos órdenes), metadata `max_link_capacity` (entero positivo) opcional. Registra en graph + ambas zonas manualmente en el parser (no se tocó `Graph.add_connection`).

**Parser COMPLETO + TESTEADO.** Falta: integración con main.

#### Tests Bloque 2
- [x] `tests/test_bloque_2.py` — 25 casos de error (1 por `raise`, archivos `tests/files_test/file_test_N.txt`) + caso `OSError` (archivo inexistente) + caso válido completo verificando retornos. Runner recorre los archivos en un `for`, captura con `try/except (ValueError, OSError)`. Todo pasa; flake8 + mypy limpios (imports con `# noqa: E402` por el `sys.path`).

> [!info] Decisión clave de la rama hub (typing)
> Se descartó acumular en `Dict[str, Union[int,str]]` + `Zone(**obj)` porque NO pasa mypy estricto (los valores son unión, no tipos por clave; y `cast`/`TypedDict` incremental tampoco). **Solución:** crear `Zone(name, x, y)` con lo mandatory y dejar que `_parse_metadata` mute los atributos opcionales (`zone.color = ...`) con claves literales del `match`. Sin contenedor intermedio.

> [!warning] Pendiente al integrar (main)
> - `manufacturing` debe retornar `tuple[Graph, List[Drone]]` (ahora `-> None`, sin `return`).
> - Los `except` salen de `manufacturing` (que solo lanza) y van a **main**: `except (ValueError, OSError)` → imprimir + parar, sin continuar a la simulación. El parser solo construye-o-lanza.

> [!note] Pendiente menor
> `import sys` (línea 7) sin usar → `flake8` lo marca. Quitar.

> [!info] Retomar aquí (pausa 2026-06-26)
> El estudiante se replantea dividir `manufacturing` en métodos (instinto bueno; coincide con el diseño original `_parse_zone`/`_parse_connection`/`_parse_metadata` + un `parse_n_drones`). **Decisión pendiente que tomará él:** ¿los métodos *retornan* el objeto (`Zone`/`Drone`) y `manufacturing` registra en `self.graph`/`self.drones`, o *mutan* el estado directamente? Definir qué recibe cada método (línea cruda vs `line_processed`).
>
> Diseño de la rama hub (propuesto por el estudiante, ya analizado). Puntos que debe resolver al implementarla:
> - **Coordenadas son enteros, pueden ser NEGATIVAS** (subject dice "enteros", no positivas). `isdigit()` NO sirve para negativos. Índices: `tokens[1]`=name, `tokens[2]`=x, `tokens[3]`=y.
> - **Nombres únicos** (no solo sin `-`): comprobar contra `self.graph.zones`.
> - **Exactamente 1 `start_hub` y 1 `end_hub`**: falta llevar la cuenta.
> - `relevant`: `"start"` / `"end"` / `None` según tipo.
> - **Metadata `[...]`**: el `split()` inicial ya partió `[color=green max_drones=2]` en varios tokens con `[` y `]` pegados → hay que reconstruir el bloque crudo y pasarlo a `_parse_metadata`. Partir cada par por `=`. Validar valores según campo (`zone` ∈ {normal,blocked,restricted,priority}; `color` palabra; `max_drones` entero positivo).
> - `"hub" in line_processed[0]` matchea substrings raros tipo `"subhub:"` → validar tipo exacto.
> - Crear la `Zone` y registrarla en `self.graph`.

---

### Bloque 4 — Simulation (EN PROGRESO — diseño de firmas/lógica, sin código real todavía)

Archivo: `clases/simulation/simulation.py`. Estado: firmas y atributos definidos, cuerpos de métodos aún en pseudocódigo. **Pausado 2026-07-09** (el estudiante paró por cansancio).

> [!danger] AL RETOMAR — primera decisión pendiente (L2/L3)
> **El offset de `logs[0]` (la posición inicial `start` NO se imprime).** El ejemplo del subject arranca el output en el primer *movimiento*, no en `start`. Como el bucle de logs indexa por el índice `i` del path y el start es el índice 0, hay que decidir **una** de dos formas de evitar una primera línea en blanco:
> - **(a)** `logs` con offset → usar `logs[i-1]`, o
> - **(b)** indexar por `i` y en `output` saltar las sublistas vacías.
> Esto es lo primero a resolver antes de seguir escribiendo `simulating`/`output`.

#### Firmas (cerradas 2026-07-09)

- `__init__(self, graph: Graph, drones: List[Drone]) -> None` — **se eliminó el parámetro `dijkstra`** (se instancia uno nuevo por dron dentro del método, no se reutiliza).
- `simulating(self) -> None` — orquestador (era `calculate`).
- `calculating_reservations(self, path: List[Union[Zone, Connection]]) -> ...` — vuelca la ocupación de un path a `self.reservations`. Return por definir (probablemente `-> None`, muta en sitio).
- `get_connection(self, zone1, zone2) -> Connection` — helper. **Decisión tomada:** se moverá a `Zone` como `get_connection_to(other)` y recibirá objetos `Zone` (no `str`), porque quien lo llama ya tiene los objetos del path. Pendiente crear el método en `Zone`.
- `output(self) -> None` — imprime `logs` (era `print_log`).

#### Atributos (ver tabla en Fase 1, ya actualizada)

`graph`, `drones`, `reservations: Union[Dict[int, Dict[str, int]], None]`, `start: Union[Zone, None]`, `end: Union[Zone, None]`, `logs: List[List[str]]`. Se eliminó `drone_reservations` (el snapshot vive en `Drone`) y `simulation` dict → `logs`.

#### Decisiones de lógica ya tomadas

- **`start`/`end`** se resuelven en `__init__` con `next((z for z in graph.zones.values() if z.relevant == "start_hub"/"end_hub"), None)`. Requiere **guard `if self.start and self.end`** antes de pasarlos a `Dijkstra` (que los pide `Zone`, no `Optional`). ✅ escrito.
- **Orden de cálculo:** los drones se rutean en el orden de la lista (`D1, D2, …`), tal como los creó el Parser. D1 se rutea con `reservations = None`; a partir de D2 se pasa `self.reservations` acumulado + `add_reservation`.
- **`add_path` recibe el PATH**, no el objeto Dijkstra: `add_path(Dijkstra(...).dijkstra())`. ✅ corregido.
- **Indexado de `reservations` y `logs` por el índice `i` del path** = turno de Dijkstra (todos arrancan en `start` = coste 0 = índice 0; cada elemento = +1 turno; restricted = `Connection`+`Zone` = 2 elementos = +2). Confirmado alineado con lo que Dijkstra lee.
- **`reservations`: se saltea `start`** al reservar (Dijkstra lo exime vía `not relevant`, no lo chequea).
- **`get_connection` se llama solo en movimientos NORMALES** (en restricted la `Connection` ya viene intercalada en el path → se reserva sola al iterar). *(El estudiante ya corrigió la rama que estaba invertida.)*
- **Omisión en el output:** un dron en **espera** (`path[i] == path[i-1]`) se omite de esa línea; un dron **entregado** deja de aparecer solo porque su path termina en `end`. El bucle debe arrancar en **`i = 1`** (en `i = 0`, `path[i-1]` sería `path[-1]` = `end`, bug de wrap-around).
- **NOTA descartada:** poner `max_drones = float("inf")` en start/end NO hace falta (Dijkstra ya exime zonas `relevant`) y rompería el tipo `int`.

#### Pendiente de escribir/decidir

- [ ] **PRIMERO:** resolver el offset de `logs[0]` (L2/L3, ver danger arriba).
- [ ] Patrón para crecer `logs`: `if i >= len(self.logs): self.logs.append([entry]) else: self.logs[i].append(entry)` — sin `logs[i].append` en la rama de creación (IndexError), sin corchetes de más.
- [ ] Recordar `.name` al construir el string del log: `drone.path[i].name` (los elementos son objetos, no strings).
- [ ] Crear `Zone.get_connection_to(other: Zone) -> Connection`.
- [ ] Escribir los cuerpos reales (hoy son pseudocódigo + `return ...` placeholders).
- [ ] Partir líneas E501 (diferido a propósito hasta tener el código).
- [ ] Tests con `pytest` (framework confirmado por el subject) — incluir el caso de integración anotado arriba (mapa restricted, 3 drones → 1/2/3).

---

## FASE 3 — INTEGRACIÓN Y VALIDACIÓN

### Tests de integración

#### [Bloque A] + [Bloque B]

- [ ] Implementación
- [ ] Test

### Checklist subject

- [ ] Todos los archivos en la raíz del repositorio Git
- [ ] Sin librerías de grafos
- [ ] 100% orientado a objetos
- [ ] 100% typesafe: flake8 + mypy sin errores
- [ ] El programa no crashea con excepciones no manejadas
- [ ] Makefile con todas las reglas requeridas
- [ ] README en inglés con todas las secciones obligatorias
- [ ] Visual representation implementada (pygame)

### Linting

- [ ] `flake8` sin errores
- [ ] `mypy` sin errores

### README

- [ ] Completo

### Revisión final

- [ ] Subject releído por agente
- [ ] Proyecto revisado contra requisitos
- [ ] Reporte generado

### Repaso final del estudiante (post-entrega)

- [ ] **Armar un dossier del proyecto para Perplexity** que lo explique todo de cero, asumiendo que el estudiante habrá olvidado muchos detalles. El agente diseña la forma de empaquetar y entregar la info (qué archivos/código/decisiones incluir y en qué orden) para que Perplexity pueda dar una explicación clara y completa.
  - **Prioridad de temas a que quede explicado bien:** el import circular resuelto con `from __future__ import annotations` + `TYPE_CHECKING` (por qué las anotaciones no se evalúan en runtime, por qué mypy sí las ve, por qué se necesitan ambos). Es lo que más cuesta recordar.
  - Incluir también: Dijkstra turn-aware (turno = coste, arista de espera, tope `max_moves`), el modelo de `reservations` plano, y el invariante "moving out frees capacity same turn".

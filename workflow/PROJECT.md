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

**Atributos:**

| Nombre | Tipo |
|---|---|
| `graph` | `Graph` |
| `drones` | `List[Drone]` |
| `reservations` | `Dict[int, Dict[str, int]]` |
| `drone_reservations` | `Dict[str, Dict[int, Dict[str, int]]]` |
| `simulation` | `Dict[int, Dict[str, str]]` |

> `reservations[turno]["zona_o_conn"] = drone_count` (plano)
> `drone_reservations["D1"]` = snapshot de reservas al momento de calcular D1
> `simulation[turno]["D1"] = "zone_x"`

**Métodos:**

| Firma | Descripción |
|---|---|
| `calculate() -> None` | calcula paths de todos los drones en orden de prioridad, actualiza reservas y llena `simulation` |
| `print_log() -> None` | imprime el log de simulación usando `self.simulation` |

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

**Pendiente:**
- [ ] **Punto 3 — arista de espera** `(N,T)→(N,T+1)`. NO implementada. Decisiones abiertas: **cuándo dispararla** (propuesto: solo si un vecino se bloqueó por lleno este turno; sin reservas no hace falta) y un **tope de turnos** para garantizar terminación (si algo está lleno para siempre → dar inalcanzable).
- [ ] **E501** en 5 líneas de código (10, 19, 33, 81, 86) — partir.
- [ ] **Tests del Bloque 3.**
- [ ] Menores: método `get_connection_to(other)` en `Zone`/`Graph` (lo necesita Simulation para hallar la conn entre 2 zonas consecutivas del path); posible dead code `drone_in`/`drone_out`/`is_full`/`drone_count` en Zone/Connection (revisar al diseñar Bloque 4 — si `reservations` cubre la ocupación, se borran con sus tests del Bloque 1).

**Depende de Bloque 4:** la etapa de reservas solo se prueba de verdad cuando `Simulation` **produzca** `reservations`. Dijkstra la recibe como snapshot estático (solo lee); Simulation la posee y la actualiza tras cada dron. Estructura plana: `Dict[int, Dict[str, int]]` = `[turno][nombre]=count`.

**Conceptos ya asentados con el estudiante:** Dijkstra no "camina" (los pops saltan, `previous` mantiene el árbol); turno = coste acumulado; espera = arista que compite por coste; el mismo estado `(zona,turno)` siempre cuesta lo mismo (por eso el guard es de novedad, no de coste).

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

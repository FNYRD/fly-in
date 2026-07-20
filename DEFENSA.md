---
proyecto: Fly-in
tipo: guion de defensa
generado: 2026-07-18
tags: [42, fly-in, peer-review]
---

# DEFENSA.md — Guion para el peer-review

> [!info] Para qué sirve este archivo
> Explicar el proyecto completo de cero, con la profundidad suficiente para responder cualquier pregunta del evaluador. Está ordenado como conviene contarlo, no como está el código.

---

## 1. El problema en una frase

Mover `N` drones desde una zona `start` hasta una zona `end` a través de un grafo de zonas conectadas, **en el menor número de turnos posible**, respetando capacidades de zonas y de conexiones, costes de movimiento distintos por tipo de zona, y sin colisiones ni deadlocks.

Lo que lo hace difícil no es encontrar *un* camino — eso es Dijkstra de libro. Es que **los drones se estorban entre sí**: si los 25 toman la ruta más corta, se atascan en el primer cuello de botella. El problema real es de *scheduling*, no de pathfinding.

---

## 2. Arquitectura: quién hace qué

Nueve archivos en la raíz del repo (exigido por el subject), en orden de dependencia:

| Archivo | Responsabilidad |
|---|---|
| `zone.py` | Una zona: nombre, coordenadas, tipo, capacidad, sus conexiones |
| `connection.py` | Una arista bidireccional entre dos zonas, con su capacidad |
| `graph.py` | Contenedor: `Dict[str, Zone]` + `List[Connection]` |
| `drone.py` | Contenedor de datos: id, path calculado, snapshot de reservas |
| `parser.py` | Lee el archivo de mapa, valida, construye el `Graph` y los `Drone` |
| `dijkstra.py` | Pathfinding **turn-aware** para UN dron |
| `simulation.py` | Orquesta: rutea cada dron, acumula reservas, genera el log |
| `view.py` | Visualización con pygame (clase `View`) |
| `fly.py` | Entry point: menú terminal/pygame (clase `TerminalSim`) |

**Flujo completo:**

```
fly.py  →  Parser.manufacturing()  →  (Graph, List[Drone])
        →  Simulation.simulating()
              └─ por cada dron: Dijkstra(...).dijkstra()  →  path
                                calculating_reservations(path)
                                populate_logs(drone, path)
        →  Simulation.output()   →  una línea por turno
```

Regla de diseño que conviene decir en voz alta: **el parser solo construye o lanza**. No captura sus propias excepciones. Los `except` viven en `fly.py`, que es quien decide qué hacer con el error (imprimirlo y parar).

---

## 3. El modelo de datos

### Zone

`name`, `x`, `y`, `zone_type` (`normal`/`priority`/`restricted`/`blocked`), `color`, `max_drones` (default 1), `relevant` (`"start_hub"` / `"end_hub"` / `None`), `connections: List[Connection]`.

`relevant` es la marca de start/end. Se usa en dos sitios clave: `Simulation.__init__` para localizarlos, y `congested_area` para **eximirlos del límite de capacidad** (el subject dice que start y end son las dos excepciones a la regla de ocupación).

Métodos: `add_connection`, `get_connection(zone_asked) -> Optional[Connection]`.

### Connection

`zone1`, `zone2`, `name` (= `"zone1-zone2"`), `max_link_capacity` (default 1). Método clave: `get_otherside_zone(zone)` — dada una punta, devuelve la otra, o `None` si la zona no pertenece a la conexión.

> **Por qué el nombre es `"a-b"`:** permite meter zonas y conexiones en el **mismo diccionario plano** de reservas sin colisión, porque el subject prohíbe guiones en los nombres de zona. Una clave con guion es siempre una conexión. Es un truco deliberado, no una casualidad.

### Drone

Contenedor puro: `id` (`"D1"`, `"D2"`…), `path: List[Union[Zone, Connection]]`, `reservations` (snapshot de lo que vio al calcularse), `is_active`.

El `path` es la estructura central del proyecto. **Un elemento = un turno:**

- Zona normal/priority → un solo elemento (la `Zone`), 1 turno.
- Zona restricted → **dos** elementos (la `Connection` y luego la `Zone`), 2 turnos.
- Esperar → **la misma `Zone` repetida**.

Se descartó usar un sentinel tipo `"waiting"`: repetir la zona hace que el índice del path sea siempre el turno, sin excepciones.

---

## 4. El import circular (pregunta probable)

`zone.py`, `connection.py` y `graph.py` se necesitan mutuamente en las anotaciones de tipo. La primera versión importaba bajo `if TYPE_CHECKING:` y usaba los nombres en las firmas → **`NameError` en runtime**, porque el bloque `TYPE_CHECKING` es `False` al ejecutar, pero las anotaciones sí se evaluaban.

**Solución: `from __future__ import annotations` como primera línea de los tres archivos.**

Por qué funciona, que es lo que hay que saber explicar:

- Sin ese import, Python **evalúa** las anotaciones al definir la función. `def f(z: Zone)` ejecuta el nombre `Zone` en ese momento → si no está importado, `NameError`.
- Con él, las anotaciones se guardan como **texto** y no se evalúan nunca en tiempo de ejecución. Da igual que `Zone` no exista en runtime.
- **mypy sí las lee**, porque no ejecuta el código: analiza el fuente, ve el bloque `if TYPE_CHECKING:` y resuelve el tipo.
- Por eso hacen falta **los dos**: `TYPE_CHECKING` para que mypy tenga el símbolo, y `from __future__ import annotations` para que Python no intente resolverlo.

Detalle que demuestra que se entendió: ni `flake8` ni `mypy` detectaron el bug, porque **ninguno ejecuta el código**. Apareció al correr los tests.

---

## 5. El parser

`manufacturing()` lee línea a línea y despacha por el primer token:

- línea vacía o que empieza por `#` → se ignora
- `nb_drones:` → `_parse_drones` (solo una vez, primera línea, entero positivo)
- `hub:` / `start_hub:` / `end_hub:` → `_parse_zones`
- `connection:` → `_parse_connections`
- cualquier otra cosa → `ValueError` con la causa

Validaciones que conviene poder citar: nombres únicos y sin guiones; coordenadas enteras **incluyendo negativas** (por eso no se usa `isdigit()` a secas); exactamente un `start_hub` y un `end_hub` (se comprueba con `len(self.start_end) != 2` al terminar); conexiones solo entre zonas ya definidas; conexión duplicada detectada en **ambos órdenes** (`a-b` == `b-a`) recorriendo `z1.connections` con `get_otherside_zone`; tipos de zona limitados a los cuatro válidos; capacidades enteras positivas; al menos una conexión.

Decisión de tipado que costó y vale contar: se intentó acumular la metadata en un `Dict[str, Union[int, str]]` y hacer `Zone(**obj)`. **No pasa mypy estricto**, porque los valores son una unión y mypy no sabe qué clave lleva qué tipo. La solución fue crear la `Zone` con lo obligatorio y dejar que `_parse_metadata` **mute los atributos** con claves literales dentro de un `match`.

---

## 6. Dijkstra turn-aware — el corazón del proyecto

Aquí es donde hay que estar más sólido. Es lo que diferencia el proyecto de un Dijkstra copiado.

### La idea central: el coste **es** el turno

Como cada movimiento cuesta 1 o 2 turnos, el coste acumulado de Dijkstra **es literalmente el número de turno** en que el dron llega a esa zona. Eso permite consultar la ocupación futura: si sé que llego a la zona `M` con coste 7, puedo preguntar "¿cuántos drones tienen reservada `M` en el turno 7?".

### El estado no es una zona, es `(Zona, turno)`

En un Dijkstra normal el estado es el nodo. Aquí no basta: llegar a `M` en el turno 3 y llegar a `M` en el turno 5 son situaciones **distintas**, porque la ocupación cambia. Por eso `distances`, `visited` y `previous` se indexan con la tupla `(Zone, int)`.

Consecuencia sutil: el guard es de **novedad**, no de "más barato":

```python
if (neighbor, accumulated_cost) not in distances:
```

Porque el coste forma parte del propio estado — el mismo `(zona, turno)` siempre cuesta lo mismo. No tiene sentido preguntarse si se llegó "más barato".

### Los cuatro costes

`real_cost(zone)`: 1 para `normal` y `priority`, 2 para `restricted`. Las `blocked` ni se evalúan (`continue` en el bucle de vecinos).

`penalty(zone)`: 0 si es `priority`, 1 si no. Va en la **segunda posición** de la tupla del heap, así que **solo desempata entre estados de igual coste**. Esto implementa exactamente lo que dice el subject: priority cuesta 1 turno *pero se prefiere*. Si preguntan por qué no se le da coste 0.5 o menor: porque falsearía el número de turnos, que es justo la métrica que se puntúa.

### `congested_area` — la comprobación de capacidad

Antes de encolar un vecino se comprueban dos cosas:

1. **La conexión**, en el turno de tránsito: `conn_turn = accumulated_cost - 1` si el destino es restricted (porque el dron está en la conexión el turno *anterior* a llegar), o `accumulated_cost` si es normal.
2. **La zona destino**, en el turno de llegada, **salvo que sea start o end** (`not neighbor.relevant`).

La distinción entre los dos turnos viene de una distinción conceptual: `max_link_capacity` es un límite de **flujo** (cuántos cruzan a la vez) y `max_drones` es de **stock** (cuántos están dentro a la vez). No se miden en el mismo instante.

### La arista de espera

Si tras recorrer todos los vecinos no se encoló **ninguno** (`pushed == 0`, todos bloqueados o llenos), el estado no se deja morir: se encola el propio nodo un turno más tarde.

```python
if pushed == 0:
    heapq.heappush(priority, (cost + 1, self.penalty(poped), poped))
    previous[(poped, cost + 1)] = (poped, cost)
```

Esperar se convierte así en **una arista más que compite por coste** dentro del mismo Dijkstra. No hay lógica separada de "esperar": el algoritmo elige esperar cuando esperar sale más barato que rodear. Y como `previous` se registra igual que con un vecino normal, `rebuild` reconstruye la espera sola, como la misma zona repetida.

Sin esto, un estado cuyos vecinos estuvieran todos ocupados desaparecería y podría reportarse "inalcanzable" un caso que solo necesitaba esperar un turno.

### El tope de turnos: `max_moves`

Con la arista de espera, el heap **nunca se vacía solo** — siempre hay un estado que puede esperar un turno más. Hace falta un corte para el caso realmente inalcanzable.

```python
self.max_turn = max(reservations.keys(), default=0) if reservations else 0
self.max_moves = len(self.graph.zones)
...
if cost > self.max_turn and cost > last_cost:
    last_cost = cost
    self.max_moves -= 1
if self.max_moves < 1:
    raise ValueError("Unreachable end node")
```

La lógica, que es la parte más fina del proyecto:

- `max_turn` es el último turno con datos reales en `reservations`. Más allá, por construcción, no puede existir ninguna reserva. Es decir: **pasada la congestión conocida, el mapa está vacío**.
- Una vez ahí, un camino simple (sin repetir zona) tiene como máximo tantos movimientos como zonas hay. Si se gastan más, se está dando vueltas: no hay camino.
- `last_cost` hace que se descuente **una sola vez por turno nuevo**, no en cada `heappop` (varias ramas pueden compartir turno).
- **Una zona restricted no cuenta doble**: el contador mide *movimientos*, no turnos. Entrar en una restricted salta el `cost` de +2, pero sigue siendo un único avance → descuenta 1.
- **D1 no necesita caso especial**: con `reservations` vacío, `max_turn = 0` y el contador arranca desde el primer turno. El mismo mecanismo sirve para todos.

Alternativas descartadas, por si preguntan: un tope fijo (arbitrario), `2×path(D1)` y `2×path(dron_anterior)` — los mapas de congestión extrema (Capacity hell, Impossible Dream) fuerzan esperas muy por encima del doble del camino ideal, y cerca de la saturación aparece el "efecto acantilado" de teoría de colas: un dron más puede disparar una espera desproporcionada sin que haya deadlock.

### `rebuild`

Camina `previous` hacia atrás desde `(end, coste_final)` y da la vuelta a la lista. Dos detalles:

- Cuando la zona a la que se llega es `restricted`, **intercala la `Connection`** entre las dos zonas. Ahí es donde el path gana su segundo elemento.
- El corte es **estructural**: `before = previous.get(after); if before is None: break`. Se camina hasta el único estado sin predecesor, que es la semilla `(start, 0)`.

> **Bug histórico que vale contar:** antes el corte era `if unpacked_before == self.start: break`, comparando solo la zona sin mirar el turno. Con dos o más esperas seguidas en `start`, cortaba antes de tiempo y el path salía más corto que los turnos reales. Es un buen ejemplo de por qué el estado tiene que ser `(zona, turno)` **de forma consistente en todo el algoritmo**, no solo en el heap.

### `Zone.__lt__` — por qué existe

Las entradas del heap son tuplas `(coste, penalty, Zone)`. Cuando dos estados empatan en coste **y** en penalty, `heapq` compara el tercer elemento para ordenar — y comparar dos objetos `Zone` sin `__lt__` lanzaría `TypeError`. Por eso `Zone` define `__lt__` comparando por nombre: da un desempate **determinista** (mismo mapa → mismo resultado siempre) y evita el crash. No es decoración: sin ese método el algoritmo revienta en cuanto dos ramas empatan, que es lo normal en un grafo simétrico.

### Traza completa: la espera y la reconstrucción, paso a paso

Mapa mínimo: `start — A — end`, todo `normal`, `A` con capacidad 1, la conexión `start-A` con capacidad 1. **Dos drones.**

**D1** se calcula con `reservations = None`, así que va libre: path `[start, A, end]`. Al volcarlo, `calculating_reservations` deja:

```
reservations = {
    1: {"A": 1, "start-A": 1},     # turno 1: D1 entra en A cruzando start-A
    2: {"end": 1, "A-end": 1},     # turno 2: D1 llega al end
}
```

**D2** se calcula con ese mapa. `max_turn = 2`, `max_moves = len(zones) = 3`.

| Paso | Qué pasa |
|---|---|
| `push (0, 1, start)` | semilla, coste 0 |
| `pop (start, 0)` | `cost=0`, no supera `max_turn` → no descuenta `max_moves` |
| vecino `A`, `acc=1` | `congested_area(1, A, start-A)`: `conn_turn = 1`, y `reservations[1]["start-A"] = 1`, `1 + 1 > 1` → **bloqueado**, `continue` |
| fin del `for` | `pushed == 0` → **arista de espera**: `push (1, 1, start)` y `previous[(start,1)] = (start,0)` |
| `pop (start, 1)` | el mismo nodo, un turno más tarde — es un estado **distinto** |
| vecino `A`, `acc=2` | `conn_turn = 2`: `reservations[2]` no tiene `start-A` → libre. Zona `A` en turno 2: tampoco reservada → libre. `push (2, 1, A)`, `previous[(A,2)] = (start,1)` |
| `pop (A, 2)` | vecinos `start` (acc 3) y `end` (acc 3), turno 3 sin reservas → ambos se encolan. `previous[(end,3)] = (A,2)` |
| `pop` | empatan `(3,1,end)` y `(3,1,start)` → desempata `__lt__` por nombre: `"end" < "start"`, sale `end`. `poped == self.end` → **break** |

`rebuild((end, 3), previous)` camina hacia atrás:

```
(end,3) → (A,2) → (start,1) → (start,0) → previous.get() da None → break
```

y da la vuelta a la lista:

```python
[start, start, A, end]
 T0     T1     T2  T3
```

**Los dos `start` seguidos son el turno de espera.** No hay ningún marcador especial: la espera *es* la zona repetida, porque el estado `(start,1)` se alcanzó desde `(start,0)` por la arista de espera, y `previous` la registró igual que a cualquier vecino. Por eso `rebuild` no necesita saber nada de esperas — solo camina predecesores.

Salida final de los dos drones:

```
D1-A                 <- turno 1: D2 espera, se omite de la línea
D1-end D2-A          <- turno 2: D1 llega, D2 entra en A justo cuando se libera
D2-end               <- turno 3
```

Esa línea 2 es además la demostración visible del invariante *"drones moving out free up capacity for that same turn"*: D2 entra en `A` **el mismo turno** en que D1 sale hacia `end`.

### Por qué el camino reconstruido es el más corto

Es la garantía estándar de Dijkstra, con un matiz. Al extraerse siempre el estado de menor coste del heap, cuando `end` sale de la cola ya no puede existir otra ruta más barata hacia él: cualquier camino alternativo pasaría por algún estado todavía encolado, y **todos** los encolados tienen coste mayor o igual. Como aquí el coste **es** el turno, "el camino más barato" y "el que llega antes" son literalmente lo mismo.

El matiz es que el óptimo lo es **dado el mapa de reservas actual**: para D2, el camino más corto que respeta lo que ya ocupa D1. No es el óptimo global de la flota (ver sección 13).

---

## 7. Simulation — de un dron a la flota

### La estrategia: secuencial con reservas acumuladas

Los drones se rutean **de uno en uno, en orden** (`D1`, `D2`, …). Cada uno ve las reservas de todos los anteriores y las respeta:

- `D1` se calcula con `reservations = None` → camino libre, el óptimo absoluto.
- `D2` en adelante reciben `self.reservations` acumulado, así que su Dijkstra ya esquiva lo ocupado.
- Tras cada dron: `calculating_reservations(path)` vuelca su ocupación al mapa global.

Esto es lo que evita los deadlocks **por construcción**: un dron nunca planifica entrar donde ya no cabe, así que no hay que detectar ni resolver colisiones después. El conflicto se previene en la fase de ruteo, no en la de ejecución.

> **Orden de las operaciones (bug corregido):** en la rama de D2+, `add_reservation` va **antes** de `calculating_reservations`. Al revés, el snapshot que guarda el dron incluiría su propio camino recién calculado, en vez de solo lo que vio al decidir.

### `reservations`: un diccionario plano

```python
reservations[turno][nombre] = cuántos_drones
```

Zonas y conexiones **en el mismo diccionario**, sin colisión posible porque solo las conexiones llevan guion en el nombre. Es la estructura que Dijkstra **lee** (nunca escribe) y que Simulation **posee**.

### El invariante de capacidad

> *"Drones moving out free up capacity for that same turn"* (subject VII.3).

Sale gratis del diseño: al recorrer el path posición por posición, un dron reserva una zona **solo** en los turnos en que su path lo pone ahí. El turno en que se mueve ya cuenta en el destino, no en el origen. Si se violara, se bloquearía injustamente al dron que llega justo cuando el otro sale.

### `populate_logs` y el invariante del "turno vacío"

`logs[i]` es la lista de movimientos del turno `i+1`. Se indexa posicionalmente con `len(self.logs)`, lo cual solo es correcto si **nunca hay un turno en el que ningún dron se mueva**. Se probó que no puede pasar:

- Si un dron `K` espera en el turno `T`, es porque otro dron `J`, calculado antes, ocupa lo que `K` necesita.
- Si `J` también espera, se rastrea hacia atrás; la cadena siempre termina en **D1**.
- D1 se calcula con `reservations = None`, así que **nunca genera una arista de espera**: si está activo, se mueve.
- Un dron ya entregado no deja reservas en turnos posteriores, así que no puede causar bloqueos después de llegar.

Conclusión: mientras haya un dron activo, siempre hay alguien moviéndose. No hay líneas vacías y el índice nunca se desalinea.

### `output`

Una línea por turno, entradas `D<ID>-<nombre>` separadas por espacio. Los drones que esperan se omiten (`if path[i-1] == path[i]: continue`), y los entregados desaparecen solos porque su path se acabó.

---

## 8. Visual representation (`view.py`)

Pygame-ce (el pygame original no compila en Python 3.14; la API es idéntica). Clase `View`.

- Menú de mapas que escanea `maps/` por dificultad, y menú de modo (manual con flechas / automático a 0.5 s por turno).
- Escalado dinámico de coordenadas a píxeles: `pixels_per_unit` adaptativo según el rango de coordenadas del mapa y el tamaño de pantalla, con radio de zona y márgenes proporcionales.
- Zonas como círculos con **el color declarado en la metadata del mapa** (17 colores mate mapeados desde todos los mapas), conexiones como líneas de grosor proporcional.
- Drones dibujados como cuadricópteros (4 motores, brazos, cuerpo), un color por dron, con su ID encima.
- Posición por turno: centrado en la zona, o **en el punto medio de la conexión** cuando está en tránsito hacia una restricted — que es la lectura visual directa de que ese movimiento cuesta 2 turnos.

Esto cubre el requisito de que los colores de la metadata se usen en la visualización, que es un bullet explícito de la hoja de evaluación.

---

## 9. Tests

`tests/test_pytest.py`, 19 tests con pytest (el subject lo autoriza explícitamente en III.3; no son entregable ni se puntúan).

- **Correctitud (3):** capacidades respetadas turno a turno, todos los drones llegan al end, todos los pares consecutivos del path son movimientos legales.
- **Movement costs (4):** normal = 1 turno, restricted = 2 (con la conexión intercalada), priority preferida a igualdad de coste, blocked inalcanzable.
- **Connection capacity (1):** tres drones cruzan a la vez una conexión de capacidad 3 sin esperar.
- **Output format (1):** ningún dron repetido en una línea, los que esperan se omiten, el último en llegar es D3.
- **Benchmarks (10):** un test por mapa contra el target del subject.

Los cuatro de movement costs y el de capacidad **construyen el grafo a mano**, sin parser: aíslan el algoritmo del formato de entrada.

---

## 10. Rendimiento

Todos los targets del subject se cumplen. **Impossible Dream: 43 turnos** (el récord de referencia es 45), que es el bonus del challenger.

| | Mapa | Drones | Target | Estado |
|---|---|---|---|---|
| Easy | Linear path | 2 | ≤ 6 | ✅ |
| Easy | Simple fork | 4 | ≤ 8 | ✅ |
| Easy | Basic capacity | 4 | ≤ 6 | ✅ |
| Medium | Dead end trap | 5 | ≤ 12 | ✅ |
| Medium | Circular loop | 6 | ≤ 15 | ✅ |
| Medium | Priority puzzle | 5 | ≤ 12 | ✅ |
| Hard | Maze nightmare | 8 | ≤ 30 | ✅ |
| Hard | Capacity hell | 12 | ≤ 35 | ✅ |
| Hard | Ultimate challenge | 15 | ≤ 45 | ✅ |
| Challenger | Impossible Dream | 25 | < 45 | ✅ 43 |

---

## 11. Las preguntas del subject, con respuesta

El propio subject (pág. 12) lista lo que van a preguntar:

**¿Qué complejidad tiene?**
Un Dijkstra con heap binario es `O(E log V)`. Aquí el espacio de estados no son las zonas sino los pares `(zona, turno)`, así que el peor caso es `O(E · T · log(V · T))` con `T` el horizonte de turnos, y eso **por dron**: `N` drones → `N` ejecuciones. Es lineal en el número de drones, que es la razón de que 25 drones sigan resolviéndose en milisegundos.

**¿Funciona con muchos drones?**
Sí, y escala linealmente. El coste real no crece por el algoritmo sino por la congestión: cuantos más drones, más turnos de espera y más largo el horizonte `T`.

**¿Recalculas o cacheas caminos?**
Se **recalcula** para cada dron, a propósito. Cachear el camino de D1 y reusarlo sería incorrecto: el mapa de reservas cambia después de cada dron, así que el camino óptimo de D2 no es el de D1. Lo que sí se reutiliza es el `reservations` acumulado, que es precisamente el estado compartido.

**¿Cómo afecta a la memoria?**
`reservations` es `O(T · zonas_ocupadas)`. Los `distances`/`visited` de cada Dijkstra son `O(V · T)` pero se descartan al terminar el dron, porque **se instancia un objeto `Dijkstra` nuevo por cada uno**. Ese detalle también es lo que hace seguro mutar `self.max_moves` dentro de `dijkstra()`: no se arrastra estado entre cálculos.

**¿Cómo mejora la visualización el entendimiento?**
Ver los drones parados en mitad de una conexión hace evidente el coste de 2 turnos de las restricted, y ver la cola formándose en un cuello de botella muestra la espera estratégica, que en el output de texto es solo una ausencia de líneas.

---

## 12. Live coding: el flag `--capacity-info`

La hoja pide, en ≤ 10 minutos, un flag que muestre la ocupación por turno tipo `"Zone X: Y/Z drones, Connection A-B: Y/Z capacity used"`.

### El contexto: el programa hoy no lee argumentos

Revisado el subject entero: **nunca exige pasar el mapa por línea de comandos.** III.2 solo pide que `make run` ejecute el script principal; VI describe el formato del archivo; VII.5 el formato de salida. Ni una mención a `sys.argv`. El menú interactivo actual es perfectamente válido.

La única invocación con argumentos de todo el proyecto es el ejemplo de la hoja de evaluación — `./main.py --capacity-info map.txt` — y aparece solo dentro de este ejercicio. Como el evaluador tendrá ese texto delante, conviene soportarlo.

La buena noticia: **el dato ya existe y está completo**. `self.reservations[turno]` es exactamente `{nombre: cuántos}` para zonas *y* conexiones, y los límites están en `graph.zones[name].max_drones` y en `max_link_capacity` de cada conexión. No hay que calcular nada: es formateo.

### Decisiones tomadas (2026-07-18) — leerlas antes de teclear

**1. `sys.argv` se lee lo primero, al principio de `menu()`.**
Si hay argumentos → se salta el menú entero y se va directo a parsear el archivo indicado y simular. Si no hay ninguno → el flujo actual queda intacto, con sus dos menús. Así el modo interactivo no se toca y el modo con argumentos no arrastra preguntas que ya están respondidas.

**2. Un argumento desconocido lanza `ValueError`.**
El `except (ValueError, FileNotFoundError, RuntimeError)` que ya existe en `menu()` lo captura e imprime, así que el programa no crashea — que es requisito explícito del subject (III.1: *"if your program crashes due to unhandled exceptions during the review, it will be considered non-functional"*).

**3. El flag y la ruta se distinguen por contenido, no por posición.**
Un token es `--capacity-info`, el otro es la ruta del mapa. Así `--capacity-info map.txt` y `map.txt --capacity-info` funcionan igual, y no hay que recordar el orden delante del evaluador.

**4. La información de capacidad va intercalada, turno a turno, no al final.**
La hoja dice literalmente *"displays capacity information during simulation... **for each turn**"* y *"should output the normal simulation **plus** capacity usage information"*. O sea: la simulación normal **sigue imprimiéndose igual**, y cada línea de turno lleva debajo su bloque de capacidad.

> [!warning] Por qué NO imprimirlo todo al final
> Se consideró volcar el bloque de capacidad después del `match` de `menu()`, tras la simulación. Dos problemas concretos:
> 1. **`sim` no es visible ahí.** Se crea dentro de `TerminalSim.terminal_sim()` (`fly.py:65`) y muere con la función. Habría que devolverlo o convertirlo en atributo — trabajo extra en un ejercicio cronometrado.
> 2. **El `case 2` (pygame) no tiene `sim` en absoluto**, así que esa rama quedaría sin cubrir.
>
> Haciéndolo **dentro de `output()`** los dos problemas desaparecen: el objeto ya está a mano y no hay que cambiar la estructura de `menu()`. Y de paso queda más cerca del texto de la hoja.

### Guía de resolución (ensayarla una vez, no llevarla escrita)

**Paso 1 — localizar el código relevante.** Es lo primero que evalúan (*"should be able to locate the relevant parsing and output code"*). Son dos sitios: `fly.py` (entrada) y `Simulation.output()` (salida). Merece la pena decirlo en voz alta al abrirlos, porque es un criterio explícito.

**Paso 2 — la entrada, en `menu()`.** Leer `sys.argv[1:]`, clasificar cada token, y ramificar. La forma del código, no para copiar sino para tener clara la estructura:

- si la lista está vacía → el flujo de siempre (`print` del menú, `input`, `match`)
- si no, por cada token: si es `--capacity-info` → activar el booleano; si no, si aún no hay ruta → guardarla como ruta; en cualquier otro caso → `raise ValueError` con el token que sobra
- al terminar, si hay ruta → llamar directamente a la simulación con esa ruta y el booleano

Los `raise` que conviene tener: argumento desconocido, y ruta ausente cuando sí venía el flag (`--capacity-info` a secas no dice qué mapa usar).

**Paso 3 — pasarlo a la salida.** `terminal_sim` necesita aceptar la ruta y el booleano; hoy la ruta la fabrica `_get_maps()`. Con un parámetro opcional de ruta (`""` por defecto) se saltan los menús cuando ya viene dada. Y donde hoy hay `sim.output()`, queda `sim.output(capacity)`.

**Paso 4 — el método.** En `simulation.py`, un parámetro con default (para no romper las llamadas existentes) y un método nuevo:

```python
    def output(self, capacity_info: bool = False) -> None:
        """Print the simulation log, one line per turn."""
        for i, logs in enumerate(self.logs):
            for log in logs:
                print(log, end=" ")
            print()
            if capacity_info:
                self.capacity_info(i + 1)

    def capacity_info(self, turn: int) -> None:
        """Print zone and connection usage for a given turn."""
        if self.reservations is None:
            return
        for name, count in self.reservations.get(turn, {}).items():
            if name in self.graph.zones:
                zone = self.graph.zones[name]
                if zone.relevant:
                    print(f"  Zone {name}: {count} drones (no limit)")
                    continue
                print(f"  Zone {name}: {count}/{zone.max_drones} drones")
                continue
            for conn in self.graph.connections:
                if conn.name == name:
                    print(f"  Connection {name}: {count}/"
                          f"{conn.max_link_capacity} capacity used")
                    break
```

**Paso 5 — demostrarlo.** Con `maps/easy/03_basic_capacity.txt` (4 drones, conexiones de capacidad 4) se ven contadores mayores que 1, que es justo lo que el evaluador quiere ver. Con un mapa de capacidad 1 todo saldría `1/1` y parecería que no hace nada.

**Así se ve** — salida real de ese mapa, ejecutada el 2026-07-18 con la lógica de arriba (antes de aplicar el `(no limit)` de start/end):

```text
D1-bottleneck D2-bottleneck
  Zone bottleneck: 2/2 drones
  Connection start-bottleneck: 2/4 capacity used
  Zone start: 2/1 drones
D1-wide_area D2-wide_area D3-bottleneck D4-bottleneck
  Zone wide_area: 2/3 drones
  Connection bottleneck-wide_area: 2/4 capacity used
  Zone bottleneck: 2/2 drones
  Connection start-bottleneck: 2/4 capacity used
D1-goal D2-goal D3-wide_area D4-wide_area
  Zone goal: 2/1 drones
  Connection wide_area-goal: 2/4 capacity used
  Zone wide_area: 2/3 drones
  Connection bottleneck-wide_area: 2/4 capacity used
D3-goal D4-goal
  Zone goal: 2/1 drones
  Connection wide_area-goal: 2/4 capacity used
```

Vale la pena leer esta salida un momento antes del review, porque **demuestra sola varias cosas del algoritmo**: `bottleneck` va siempre a tope (`2/2`) sin pasarse nunca; las conexiones de capacidad 4 llevan 2 drones a la vez (movimiento simultáneo real, no serializado); y en el turno 1 aparece `Zone start: 2` porque D3 y D4 **están esperando ahí** — se ve la espera estratégica en el contador, aunque esos drones no salgan en la línea de movimientos.

### El detalle que hay que anticipar: start y end dicen `2/1`

`start` y `end` están **exentos** del límite de capacidad (`congested_area` los salta con `not neighbor.relevant`), pero su `max_drones` sigue valiendo 1 por defecto. Si se imprime sin más, sale esto — comprobado ejecutándolo sobre `easy/03_basic_capacity.txt`:

```
D1-goal D2-goal D3-wide_area D4-wide_area
  Zone goal: 2/1 drones          <- parece una violación de capacidad
```

Y no lo es: el subject dice que en el end pueden llegar varios drones. Pero un evaluador que vea `2/1` va a pensar que el algoritmo está roto, y explicarlo sobre la marcha cuesta más que el propio ejercicio. Por eso el `if zone.relevant` del ejemplo, que lo imprime como `(no limit)`.

Merece la pena mencionarlo en voz alta al implementarlo: demuestra que se conocen las excepciones de la regla de ocupación.

### Los tres detalles que pueden costar minutos

1. **El off-by-one.** `logs[i]` es el turno `i + 1` en `reservations`: `calculating_reservations` recorre `range(1, len(path))` (arranca en 1 porque el turno 0 es el start), mientras que `logs` es 0-indexado. De ahí el `self.capacity_info(i + 1)`.
2. **`self.reservations` es `Optional`.** Está tipado `Union[Dict[...], None]` para encajar con lo que espera `Dijkstra`, así que hace falta el guard `if self.reservations is None: return` o mypy protesta.
3. **Distinguir zona de conexión.** Como están en el mismo diccionario plano, la forma limpia es `if name in self.graph.zones` — y si no está, es una conexión. (También valdría `"-" in name`, porque los guiones están prohibidos en nombres de zona; el primero es más explícito.)

### Cómo ensayarlo

El ejercicio se puntúa con cronómetro (≤ 10 minutos **incluida la demostración**), y el objetivo del ensayo es que salga natural, no memorizado.

**Método: practicar sobre una copia del proyecto**, no sobre el repo. El proyecto entregado queda intacto (si el evaluador encuentra el flag ya hecho, pedirá otra modificación distinta), y en el review la modificación se hace igualmente sobre la copia que abra el reviewer.

Ciclo de ensayo: copiar el proyecto → leer esta sección → escribirlo sin mirar → ejecutarlo contra `easy/03_basic_capacity.txt` → borrar la copia y repetir hasta que salga solo.

Lo que hay que llevar en la cabeza no es el código, son cuatro cosas: **dónde** se toca (`fly.py` y `Simulation.output`), el **off-by-one** del turno, la **exención de start/end**, y que zonas y conexiones **comparten diccionario**.

---

## 13. Debilidades conocidas — mejor decirlas tú

Un evaluador que sabe del tema va a llegar aquí. Adelantarse suma.

- **El ruteo es greedy secuencial, no óptimo global.** Cada dron es óptimo *dadas las reservas de los anteriores*, pero el orden `D1…DN` es fijo. El óptimo real es un problema de flujo en el tiempo (min-cost max-flow sobre el grafo desplegado por turnos), muchísimo más caro. Se eligió la vía greedy porque cumple todos los benchmarks, es explicable y no puede producir deadlocks.
- **El `raise ValueError` por heap vacío al final de `dijkstra()` es código muerto.** Con la arista de espera el heap nunca se vacía; el disparador real de "inalcanzable" es `max_moves`. Se dejó a propósito como red de seguridad ante un refactor futuro.
- **El orden de los drones importa.** Rutear en otro orden podría dar menos turnos en algún mapa. No se explora ninguna permutación.
- **`Zone.get_connection` es lineal** sobre la lista de conexiones de la zona. Con grafos densos convendría un dict por vecino; con estos tamaños es irrelevante.

---

## 14. Checklist de constraints del subject

- [x] Sin librerías de grafos (`networkx`, `graphlib`) — solo `heapq` de la stdlib, que es una cola de prioridad genérica, no lógica de grafos
- [x] 100% orientado a objetos — 9 clases (`Zone`, `Connection`, `Graph`, `Drone`, `Parser`, `Dijkstra`, `Simulation`, `View`, `TerminalSim`), sin funciones sueltas salvo el `menu()` del entry point
- [ ] 100% typesafe — **`make lint` y `make lint-strict` fallan ahora mismo**, ver abajo
- [x] Todos los archivos en la raíz del repositorio
- [x] Sin excepciones no manejadas — `try/except (ValueError, FileNotFoundError, RuntimeError)` en `fly.py`
- [x] Makefile con `install`, `run`, `debug`, `clean`, `lint`, `lint-strict` (+ `test`)
- [x] Docstrings Google style (PEP 257) en todas las clases y métodos
- [x] Representación visual — terminal + pygame

> [!danger] Comprobar al llegar a 42, antes de entregar (anotado 2026-07-18)
> La hoja dice explícitamente *"Run `mypy .` in the project directory to verify"*, así que el evaluador va a correr el lint. **Hay que pasar `make lint` y `make lint-strict` en la máquina de 42**, que tiene **pygame** (no pygame-ce) y un **Python menor** que el de la máquina de desarrollo.
>
> 1. **Cambiar `requirements.txt` de `pygame-ce` a `pygame`.** ce se eligió solo porque el original no compila en Python 3.14; con el Python de 42 no hace falta.
> 2. **Decidir sobre los `# type: ignore[attr-defined]` de `view.py:50` y `view.py:52`** (`screen_info.current_w` / `current_h`). En la máquina de desarrollo, con pygame-ce 2.5.7 + py3.14, **sobran** y hacen fallar el lint con `Unused "type: ignore" comment` — `--warn-unused-ignores` está en la regla **obligatoria** del subject, no solo en `--strict`. Comprobado en una copia: quitándolos, `mypy --strict` da *Success: no issues found in 10 source files* y flake8 queda limpio.
>    **Se dejan puestos a propósito**, porque con los stubs de pygame (no ce) pueden volver a ser necesarios. Se decide allá, corriendo `make lint`.
> 3. **Sacar `workflow/` del repo entregado.** No es entregable, y `workflow/test_example.py` (plantilla del sistema con `from ` sin completar) dispara `E999 SyntaxError` en flake8, porque el Makefile solo excluye `.fly_in` y `tests`.
>
> **Los `# type: ignore` no están prohibidos.** Revisado el subject y la hoja completos: ninguno los menciona. Al contrario, que el Makefile obligatorio incluya `--warn-unused-ignores` implica que los ignores necesarios se dan por válidos — lo único que se rechaza es que sobren. Sirve como respuesta si el evaluador pregunta.

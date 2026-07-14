# Dossier para Perplexity — Pygame para Fly-In

## Contexto del proyecto

Tengo un simulador de drones que navegan un grafo (zonas conectadas) desde un start hasta un end. La simulación ya funciona: calcula los paths de cada dron turno a turno y genera un log con los movimientos. Necesito crear una visualización con pygame.

## Qué tengo disponible

### Datos del grafo (objeto `Graph`)
- `graph.zones`: `Dict[str, Zone]` — cada zona tiene:
  - `name: str` — nombre único
  - `x: int, y: int` — coordenadas (pueden ser negativas)
  - `zone_type: str` — `"normal"`, `"priority"`, `"restricted"`, `"blocked"`
  - `color: str | None` — color asignado en el mapa (puede ser None)
  - `max_drones: int` — capacidad máxima
  - `relevant: str | None` — `"start_hub"`, `"end_hub"` o None
  - `connections: List[Connection]` — conexiones de esta zona
- `graph.connections`: `List[Connection]` — cada conexión tiene:
  - `name: str` — formato `"zona1-zona2"`
  - `zone1: Zone, zone2: Zone` — las dos zonas que conecta
  - `max_link_capacity: int`

### Datos de la simulación (objeto `Simulation`)
- `sim.drones`: `List[Drone]` — cada dron tiene:
  - `id: str` — formato `"D1"`, `"D2"`, etc.
  - `path: List[Union[Zone, Connection]]` — posición en cada turno (índice = turno)
  - Método `get_position(turn: int) -> Zone | Connection | None`
- `sim.logs: List[List[str]]` — `logs[turno]` = lista de strings `"D1-zona"` por turno
- El total de turnos es `len(sim.logs)`

### Tipos de zona y cómo visualizarlos
| Tipo | Significado | Sugerencia visual |
|------|------------|-------------------|
| `normal` | Estándar | Círculo gris/azul |
| `priority` | Preferida por pathfinding | Círculo verde |
| `restricted` | Cuesta 2 turnos entrar | Círculo rojo |
| `blocked` | Inaccesible | Círculo negro/oscuro |
| `start_hub` | Origen de todos los drones | Círculo verde brillante |
| `end_hub` | Destino de todos los drones | Círculo amarillo |

## Qué necesito que me enseñes

1. **Cómo funciona pygame** — lo básico: inicializar ventana, game loop, dibujar formas, manejar eventos, cerrar.

2. **Cómo dibujar un grafo** — tengo coordenadas (x, y) de cada zona. Necesito:
   - Transformar las coordenadas del mapa a coordenadas de pantalla (escalar y centrar)
   - Dibujar zonas como círculos con colores según su tipo
   - Dibujar conexiones como líneas entre zonas
   - Mostrar nombres de zona

3. **Cómo animar los drones turno a turno** — la simulación ya tiene los paths calculados. Necesito:
   - Mostrar el estado del grafo en cada turno
   - Mover los drones (representados como círculos pequeños o puntos) por el grafo
   - Un dron puede estar en una zona o en una conexión (tránsito hacia restricted)
   - Avanzar turno con una tecla o con un timer automático
   - Mostrar qué turno es actualmente

4. **Cómo integrar mis datos existentes con pygame** — no quiero cambiar la estructura de mis clases. Pygame debe consumir `Graph` y los `Drone.path` tal como están.

## Restricciones
- No puedo usar librerías de grafos (networkx, etc.)
- El código debe ser 100% orientado a objetos
- Debe pasar flake8 + mypy
- Python 3.14

## Lo que espero como respuesta
Explicación paso a paso de cómo usar pygame para este caso específico, con ejemplos de código adaptados a mis estructuras (`Zone`, `Connection`, `Graph`, `Drone`, `Simulation`). No necesito un tutorial genérico de pygame — necesito entender cómo aplicarlo a mi proyecto.

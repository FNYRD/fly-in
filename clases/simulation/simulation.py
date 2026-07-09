from __future__ import annotations
from clases.graph.connection import Connection
from clases.graph.zone import Zone
from clases.drone.drone import Drone
from clases.graph.graph import Graph
from clases.dijkstra.dijkstra import Dijkstra
from typing import Dict, List, Union

# Los imports se van eliminando o agregando al final, el estado actual solo representa
# adicion improvisada


class Simulation:
    def __init__(self, graph: Graph, drones: List[Drone], dijkstra: Dijkstra) -> None:
        self.graph: Graph = graph
        self.drones: List[Drone] = drones
        self.reservations: Union[Dict[int,
                                      Dict[str, int]], None] = {}
        self.start: Union[Zone, None] = next(
            (start for start in self.graph.zones.values()
             if start.relevant == "start_hub"), None)
        self.end: Union[Zone, None] = next(
            (start for start in self.graph.zones.values()
             if start.relevant == "end_hub"), None)
        self.logs: List[List[str]] = []


    def calculating_reservations(self, path: List[Union[Zone, Connection]]) -> None:
        # El return esta por definirse

        # Este metodo recibe el path del nuevo drone y usando un ciclo for
        # con i in range(len(path)) comienza a entrar en orden en self.reservartions.get(i, {}).get(Zone.name, 0)
        # si es 0 se hace self.reservartions[i][zone|connection] = 1, sino self.reservartions[i][zone|connection] += 1.
        # tambien se verifica si la zona actual no es start y si no es verifico que no sea restricted, caso no lo sea, llamo
        # a get_connection(zone: Zone) le mando la zona actual y el index actual - 1 del path para obetener la connetion entre ambas zonas,
        # esta tambien se agrega a reservations
        # por que no hay problema con que sea acumulativo? porque cada turno es unico y segun cada turno tengo que tener
        # el registro de todas las posiciones para que el siguiente drone sepa por donde pasar, por donde no y cuando
        # esperar
        return ...

    def simulating(self) -> None:
        # atributo log: List[str]
        # Iniciar un ciclo for sobre la lista de drones, asi en orden ascendente
        # comenzando por D1, ya que ese es el orden en el que fue creada la lista
        # ir tomando drone a drone e ir pasando en cada vuelta por su metodo
        # if self.start and self.end Guard requerido por typing 
        # add_path(Dijkstra(...).dijkstra()) para d1
        # y a partir de D2 add_path(Dijkstra(...).dijkstra()) y add_reservation(self.reservation)
        # intercalando entre cada add, del dron actual tomo su path dede el atributo luego de haberselo asignado
        # lo mando a calculating_reservations y actualizo el atributo self.reservations para repetir el ciclo
        # habiendo tomado su path, lo que hago es que recorro el path entero y con un for para colocar en orden
        # reviso que no este repetido en el index anterior y si no, los logs hago 
        # primero reviso if len(i >= len(self.logs))
        # self.logs[i].append([dron.id + "-" + drone.path[i]]) 
        # else self.logs[i].append(dron.id + "-" + drone.path[i]) 
        # asi al final me queda el atributo
        # totalmente poblado y para imprimir los logs es simplemente recorrelo e ir imprimiendo cada linea con end=" "

    def output(self) -> None:
        # for a self.logs con for anidado y print con end=" ". cuando se finaliza una lista dentro de la
        # lista principal, print("\n") para cortar el efecto del end=" "



    # NOTA: VOY A PONER UN IF EN START Y END PARA QUE CUANDO SE VERIFIQUE PRIMERO SI SON UNO DE ELLOS
    # MAX_DRONES QUEDE EN FLOAT("INF") PORQUE POR DEFAULT VIENE CON CAPACIDAD 1, LO QUE PUEDE CREAR ERRORES PRINCIPALMENTE
    # EN END. UN DRONE PODRIA ASUMIR QUE ESTA LLENO Y ESPERAR ANTES DE ENTRAR EN END

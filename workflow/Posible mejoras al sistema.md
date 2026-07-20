****
## Analizar primero y luego decidir solo al finalizar el proyecto actual


# Mejoras:

- [ ] buscar una manera de crear visualizaciones que representen el proyecto para tener una guia visual. usar alguna herramienta ya existente
- [ ] siempre hacer los test en pytest
- [ ] conectar con el mcp de notion y trabajar mas visuamente ahi
- [ ] crear una regla make para hacer commit y push
- [ ] siempre trabajar con gitignore
- [ ] Que todos los .md sean optimizados para obsidian, asi hasta el HANDOF me ayuda para entender mejor el subject.
- [ ] Cambiar restricciones duras por Restricciones Genereales: que cubran todo lo que se restringe en el proyecto
- [ ] Agregar como instruccione el no hacer presion para continuar o realizar cualquier accion. En vez de decir:   ¿Pasamos a volcar el Bloque 3 al PROJECT.md y continuamos con el Bloque 4?. Mostrar: El resultado y estado actual del problema que se esta solucionando o la solucion que se esta creando y que sea el estudiante quien propone si avanzar o no.
- [ ] Cuando se actualiza el PROJECT.md tomar en cuenta que sera visualizado por el estudiante en algun visualizador de md u obsidian por lo que agregar formate agradable, con colores, tamanos de letra y lenguaje elocuente y facil de entender
- [ ] |Campo|Valor||---|---| |Responsabilidad|Representa una conexión bidireccional entre dos zonas con su capacidad y estado|: ese campo no tiene sentido en la definicion de las clases, cambiar por Descripcion. lo mostrado anteriormente es solo un ejemplo de como se estaba llenando ese campo.
- [ ] Poner en los objetivos de la fase 2, que cada que revise mi codigo me ayude a ser mas y mas eficiente, ya sea mejroando estructuras, condicones y/o flujo.
- [ ] poner en el diseno de bloques una checklist en cada cosa: atributos, metodos, etc. de cada clase para que asis ea mas facil llevar ell flujo de trabajo. Ademas el nombre de la clase debe ser mas grande, se diferencia poco y con un color diferente.
- [ ] antes de alterar todo ver a que archivo corresponde la alteracion
- [ ] Tomar en cuenta que al moemnto de planificar lo mejor es ponerme los tapones y estar en silecio, para mejor concetracio, ya para implementar puede haber musica.
- [ ] Cuando se registran los atributos, se debe crear una columna que diga si entran como argumentos o no
- [ ] cuando se registra un bloque o cualquier tipo de informacion que pueda servir en el futuro como guia al momento de implementar se debe colcoar una descripcion muy breve y directa de que hace esa estructura, codigo, etc. Por ejempo los atributos tambien deben tenerla, muchas veces la definicion de todo previa al codigo puede tardar dias lo que hace que al momento de volver a implementar usando como guia la lista creada en los bloques, el estudiante no recuerde bien la razon de esa implementacion.
- [ ] Cuando se crea la firma de un metodo, por ejemplo drone_in() -> None caso no reciba arumentos mas que self, de igual manera poner drone_in(self) -> None
- [ ] Los test de bloques se deben hacer por bloque porque la mayoria de componentes de ese bloque estan interconectados
- [ ] al final de HANDOFF.md se debe crear una division para contextualizaciones del siguiente agente, con un briefing del agente actual que explique que se hizo durante su existencia y en que punto se quedo. El cambio de agente debe suceder cuando el context del agenta actual: ⛶ Free space: 30%
- [ ] Enseñar al estudiante a usar frameworks de testing (pytest) en algún punto de Fase 2, y migrar los tests manuales a ese framework una vez que entienda la base.
- [ ] Mejorar la descripcion del flujo que quiero en terminos de definir las bloques, mi propuesta y discusion

- [ ] Cada explicacion debe darse usando escenas o situaciones de la vida real para mejor comprension de los conceptos y estas escena o situacion debe coincidir con el problema o tema que se esta tratando en el proyecto, en ese momento determinado

- [ ] Cuando el agente realiza una tarea no es necesario dar una explicacion de los resultados caso sean positivos y la meta del test o la verificacion sea asegurar que algo funciona o no. solo en los casos en los que no funciona es donde se debe explicar donde y porque, ya que esto lleva a una solucion rapida, en los casos en que la respuesta es positiva, esta informacion solo es ruido que ofusca al estudiante

- [ ] En la medida en que se toman decisiones de diseno y se van ejecutando, encontrando problemas y pensando en edge cases durante el desarrollo, si existe la posibilidad de generar un test legitimo sobre dicho escenario y asi llegar a la fase de test con camino adelantado debe hacerse. ya sea que el estudiante lo proponga o el agente lo detecte y el estudiante lo apruebe posterior a la propuesta del agente 

- [ ] Los test se deben hacer de la siguiente manera: El agente y el estudiante los discuten teoricamente, luego de haber definido los casos, bloque por bloque el agente crea el codigo y el estudiante lo lee, entiende y aprueba o rechaza segun el caso

- [ ] Pedirle al agente que cree un md llamado psicology.md. el agente debe apuntar alli todas las fortalezas y debilidades
psicologicas e intelectuales que detecte conversando conmigo, en mi, para que a medida que avanzo me ayude a mejorar en las
debilidades y a fortalecer las fortalezas, asi como tambien difcultades de aprendisaje y mejores maneras de que aprenda
y razone




---

## Tests (por bloque) — propuesta para SYSTEM.md

Los tests se generan por el agente con high effort y los ejecuta el estudiante.
Se definen conceptualmente en discusión antes de generarlos.

### Estructura

- Un archivo por bloque: `tests/test_bloque_N.py`
- Se ejecutan desde la raíz del proyecto
- Cada archivo tiene un `main()` y un `if __name__ == "__main__"`
- No usar frameworks de testing — output manual con print

### Organización del archivo

- Separar por clase con un bloque de comentario visible
- Cada test va precedido de un comentario describiendo qué verifica
- Cada print incluye valor obtenido y valor esperado

### Casos obligatorios por clase

1. **Creación correcta** — instanciar objetos con distintas combinaciones de parámetros, incluyendo valores por defecto
2. **Flujo normal** — cada método en su caso esperado (happy path)
3. **Valor límite válido** — operar justo en el borde del límite permitido y verificar que funciona
4. **Stress sobre el límite** — intentar superar el límite repetidamente y verificar que la clase no se rompe ni produce valores inválidos
5. **Comportamiento ante entradas inválidas** — identificar qué entradas o secuencias de operaciones podrían romper el método o clase, y verificar que los maneja sin producir estado inválido ni crashear

### High effort

Los tests deben cubrir interacción entre clases del mismo bloque y edge cases del dominio, no solo cada clase en aislamiento. El agente debe proponer tests de integración dentro del mismo archivo cuando aplique.

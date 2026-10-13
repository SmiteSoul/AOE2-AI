# 07 — Scripting de IA en AoC + UserPatch 1.5: investigación y auditoría integral

> **Corte de la investigación:** 2026-10-13. **Objetivo exacto:**
> *Age of Empires II: The Conquerors* 1.0c con UserPatch 1.5; DE se estudia
> solo para separar versiones y evitar portar semántica incompatible.
>
> **Estado de prueba:** la sintaxis y los invariantes descritos abajo se
> contrastaron con CPSB, el catálogo de UserPatch, AIREf, el corpus local y el
> linter. No había ejecutable del juego en este entorno: las correcciones de
> esta auditoría todavía requieren una partida real `[RUNTIME-pendiente]`.

## 0. Resultado ejecutivo

La investigación produjo cinco resultados prácticos:

1. **Modelo del motor fijado.** Las reglas son un sistema experto ordenado;
   `defconst` nombra enteros, los goals almacenan estado, los strategic numbers
   configuran la IA táctica interna y DUC permite seleccionar/ordenar objetos
   directamente. `[CPSB][FORO: AIREf]`
2. **Versiones separadas.** AoC 1.0c, UP 1.5 y DE no comparten todos los
   límites ni todos los comandos. Usar documentación moderna sin mirar la
   columna de versión es una fuente real de errores silenciosos.
   `[CPSB][FORO: AIREf]`
3. **El repositorio ya contiene tres arquitecturas distintas.** `semiUtils` es
   un monolito clásico sin DUC; `forty` es un monolito UP autocontenido; `siege`
   es modular y carga seis módulos más `UserPatchConst.per`.
   `[SEMIUTILS][FORTY][SIEGE]`
4. **La auditoría encontró fallos estáticos que el linter anterior no veía:**
   goals vanilla usados como pares/cuaternas DUC, variables `this-any-*` sin
   enlace, cuatro máquinas de estado sin inicializar, un ciclo de fase urbana,
   muros sin planificación, reglas duplicadas, `this-any-*` usados como facts y
   rearmes de timer que ocultaban el trigger a reglas posteriores.
   `[CPSB][FORO: AIREf][SEMIUTILS][FORTY][SIEGE]`
5. **Los defectos anteriores quedaron corregidos y cubiertos por regresión.**
   Los tres proyectos pasan el linter y `tools/test_lint_siege.py` ejecuta nueve
   pruebas, incluidas siete inyecciones de defectos, una regresión limpia de
   los tres proyectos y el rechazo de un nombre de proyecto inválido.
   `[FORTY][SIEGE][SEMIUTILS]`

## 1. Jerarquía de fuentes y método

### 1.1. Qué fuente prueba qué cosa

| Nivel | Fuente | Uso correcto |
|---|---|---|
| `[CPSB]` | [`reference/CPSB.pdf`](../reference/CPSB.pdf), manual de *Computer Player Strategy Builder* | Gramática y semántica base de AoC: reglas, carga, wildcards, goals vanilla, timers y SNs clásicos. |
| `[UP]` | [`reference/UserPatchConst.per`](../reference/UserPatchConst.per) y notas de UserPatch conservadas por AIREf | Constantes, comandos, límites y cambios añadidos por UserPatch. |
| `[RUNTIME]` | Una partida real en AoC 1.0c + UP 1.5 | Única prueba final de que el parser acepta el paquete y de que la táctica hace lo esperado. |
| `[CORPUS]` | [`reference/ais/`](../reference/ais/) | Prueba de uso real y de arquitectura; **no** convierte un alias local en builtin ni demuestra por sí sola la semántica. |
| `[FORO]` | [AIREf](https://airef.github.io/), repositorios y documentación comunitaria | Detalles UP/DUC, bugs y mediciones que CPSB no cubre. Debe fijarse la versión. |
| `[REPO]` | Código y linter propios | Prueba de lo que este proyecto hace estáticamente; no equivale a una partida. |

### 1.2. Material realmente revisado

- Se leyó completo el CPSB local: 95 páginas y 171.714 caracteres extraídos
  para búsqueda. `[CPSB]`
- Se revisaron los 284 scripts `.per` versionados que existían al comenzar la
  auditoría, además de los `.ai`, la documentación y el historial de errores.
  `[REPO: inventario Git al inicio de la tarea]`
- Se leyeron completos `semiUtils/semiutils.per`, `forty/forty.per`, los seis
  módulos ejecutables de `siege` y sus entrypoints. `[REPO]`
- Se estudió el corpus local y las guías de arquitectura de Barbarian 2.18,
  The General 1.3, The Horde 3.9, Promi, Brutal2, Binary, Crusher, Kaia y
  Training. `[CORPUS]`
- Se fijó AIREf al commit
  [`2f4bbd15702c`](https://github.com/airef/airef.github.io/commit/2f4bbd15702c90e920abac6f5639db1c27912149),
  2026-10-07. Su catálogo contiene 385 comandos: 185 marcados AoC, 189 UP y
  11 DE. `[FORO: conteo reproducible de js/commands.js]`
- Se contrastaron herramientas de generación, parsing y automatización; la
  tabla de §10 conserva commit, fecha y alcance. `[FORO: GitHub]`

### 1.3. Regla de compatibilidad usada

Una construcción entra en código de UP 1.5 solo si cumple al menos una de estas
condiciones: está en CPSB, está en el catálogo/constantes de UserPatch con
versión UP, o aparece en corpus UP y su firma se confirma independientemente.
Una API de DE, un compilador moderno o un ejemplo generado no son prueba de
compatibilidad por sí solos. `[CPSB][UP][CORPUS][FORO]`

## 2. Tres motores parecidos, no idénticos

### 2.1. Matriz mínima de límites

| Recurso | AoC 1.0c | UserPatch 1.5 (objetivo) | DE | Evidencia |
|---|---:|---:|---:|---|
| Reglas | 1.000 | 10.000 | 10.000 | `[FORO: AIREf data-limits]` |
| Elementos por regla | 16 | 16 | 32 | `[CPSB][FORO: AIREf data-limits]` |
| Goals disponibles | 1–40 | 1–512 | 1–16.000 | `[CPSB][FORO: AIREf data-limits]` |
| Timers por jugador | 10 | 50 | 100 | `[CPSB][FORO: AIREf data-limits]` |
| SN IDs | clásicos documentados | 0–511 | 0–511 | `[CPSB][FORO: AIREf data-limits]` |
| Lista DUC local/remota | no DUC UP | 240 / 40 objetos | 240 / 40 objetos | `[FORO: AIREf data-limits]` |

**Advertencia documental.** En el commit fijado de AIREf, el resumen de
`data-limits.html` muestra 16.000 goals, mientras el cuerpo explica los 512 de
UserPatch; varias fichas de comandos también muestran el máximo DE aunque el
comando esté marcado UP. Para este repositorio mandan los límites UP: 512
slots, pares seguros 41–510 y cuaternas seguras 41–508.
`[FORO: AIREf, discrepancia verificada][UP]`

### 2.2. Consecuencias de mezclar versiones

- Un comando marcado DE puede ser un identificador inválido en UP.
  `[FORO: AIREf commandVersion]`
- Una regla de 17–32 elementos puede funcionar en DE y producir `ERR6002` en
  UP. `[FORO: AIREf data-limits][REPO: Script_Errors.md]`
- Un goal 513–16.000 es legal en DE y no existe en UP. `[FORO: AIREf]`
- XS, APIs de objetos añadidos y algunos IDs de DLC pertenecen a DE; no deben
  colarse en un paquete para AoC 1.0c + UP 1.5. `[FORO: AIREf][FORO: AgeSharp]`

## 3. Modelo de ejecución que debe tener el scripter

### 3.1. Parseo, símbolos y carga

`defconst` no es una variable: asocia un nombre a un entero o cadena durante
la carga. Los usos posteriores deben resolver a un literal, builtin o
`defconst` ya visible. Un alias privado de Barbarian no existe automáticamente
en Siege. `[CPSB][CORPUS]`

`load` se expande inmediatamente: el parser suspende el archivo llamador,
procesa el cargado y vuelve a la regla siguiente. Puede anidarse hasta diez
niveles. Las secciones de carga condicional deciden qué reglas se cargan, pero
el parser sigue comprobando sintaxis en todas las ramas. `[CPSB]`

Implicaciones:

- ordenar los módulos es ordenar también las reglas; `[CPSB]`
- las constantes compartidas deben cargarse antes de usarse; `[CPSB]`
- en UP una redefinición cargada con valor distinto produce `ERR2012`;
  `[CPSB][FORO: AIREf]`
- `UserPatchConst.per` nombra enums como `search-local`, `action-*`,
  `object-data-*` y `position-*`; los comandos `up-*` son del motor, pero sus
  argumentos simbólicos deben resolver. `[UP]`

### 3.2. Reglas y pases

Una regla contiene facts antes de `=>` y acciones después. Mientras siga
habilitada vuelve a evaluarse en pases sucesivos; `disable-self` surte efecto
en el pase siguiente, por lo que las acciones restantes de esa regla todavía
se ejecutan. `[CPSB][FORO: AIREf]`

Los cambios de goal y SN son visibles inmediatamente para reglas posteriores
del mismo pase, pero algunos facts derivados del mundo se actualizan solo en
el pase siguiente. Por eso el orden es parte de la arquitectura y no mero
formato. `[FORO: AIREf helpful-info/SWGB guide][CORPUS]`

En UP se cuentan como elementos tanto cada fact/acción como cada operador
lógico `or`, `and`, `not`, etc.; el techo es 16. El objetivo conservador del
repo es 15. `[FORO: AIREf data-limits][CORPUS: Barbarian]`

### 3.3. Goals: estado explícito, no memoria implícita

- AoC aporta 40 goals vanilla; UserPatch amplía el espacio hasta 512.
  `[CPSB][FORO: AIREf]`
- Goals y timers arrancan en `-1`. Una nota oficial de UserPatch 1.1
  (2012-05-02, issue 336) corrigió los slots extendidos que arrancaban en cero
  y ordena inicializar siempre los datos. `[UP: AIREf js/upreleases.js]`
- `(goal id valor)` solo prueba igualdad. Para comparaciones se usa
  `up-compare-goal` o un operando `g:` en los comandos que lo admiten.
  `[CPSB][UP][REPO: errores reproducidos]`
- Un `defconst gl-mode 10` nombra el **ID** 10; no asigna cero a ese goal.
  `[CPSB]`

Patrón seguro:

```lisp
(defconst gl-mode 10)
(defconst mode-grow 0)
(defrule
    (true)
=>
    (set-goal gl-mode mode-grow)
    (disable-self)
)
```

### 3.4. Strategic Numbers

Los SN no son goals intercambiables por defecto: muchos activan lógica táctica
interna, tienen rango propio y algunos se actualizan en subsistemas más lentos.
Los IDs 313–511 parecen libres en la referencia comunitaria actual y pueden
servir como almacenamiento, pero se debe volver a consultar el índice antes de
usarlos. `[CPSB][FORO: AIREf SN index]`

`sn-number-attack-groups 200` no viola el rango documentado (`>= 0`) y el corpus
contiene 199 e incluso 1.000 para estrategias de muchos grupos. Aun así, su
calidad y coste en Forty/Siege son parámetros de balance que requieren partida,
no una garantía del parser. `[CPSB][CORPUS][RUNTIME-pendiente]`

### 3.5. Timers: la semántica correcta

Un timer tiene tres estados mutuamente excluyentes: disabled, running y
triggered. Al agotarse, `timer-triggered` puede consultarse cuantas veces sea
necesario hasta un `disable-timer` **o un nuevo `enable-timer`**; rearmar lo
pone de nuevo en running. No queda “apagado” automáticamente al dispararse.
`[CPSB][FORO: AIREf enable/disable/timer-triggered]`

Patrón multicast seguro del repo:

1. armar una vez en init;
2. poner **todos** los consumidores antes;
3. rearmar al final del orden global.

Si un consumidor rearma antes que los demás, limpia el estado triggered y los
consumidores posteriores no lo ven. `[CPSB][FORO: AIREf][REPO]`

## 4. Wildcards y variables de regla

Los wildcards `any-*` usados por un fact exitoso enlazan la variable asociada
`this-any-*`. Esa variable solo vive durante la misma regla y se invalida al
terminar. CPSB la autoriza en acciones concretas; AIREf amplía la tabla para
acciones UP como `up-get-player-fact`, pero no la autoriza como argumento de
facts. `[CPSB: “Rule Variables”, pp. 68–69][FORO: AIREf PlayerNumber]`

Correcto:

```lisp
(defrule
    (players-building-count any-enemy > 0)
=>
    (up-get-player-fact this-any-enemy player-number 0 gl-enemy)
)
```

Incorrecto por falta de enlace:

```lisp
(defrule
    (true)
=>
    (up-get-player-fact this-any-enemy player-number 0 gl-enemy)
)
```

Incorrecto porque intenta usar la variable como fact:

```lisp
(defrule
    (taunt-detected any-computer 201)
    (stance-toward this-any-computer neutral)
=>
    ...
)
```

Cuando solo se necesita elegir un enemigo sin conservar el wildcard, el patrón
más claro es `(up-find-player enemy find-closest gl-enemy)` y después
`(up-modify-sn sn-focus-player-number g:= gl-enemy)`.
`[FORO: AIREf][CORPUS: The Horde/The General/Barbarian]`

## 5. DUC y TSA sin mitología

### 5.1. Modelo de listas

DUC imita selección y orden humana:

1. limpiar búsqueda/filtros si la rutina necesita aislamiento;
2. llenar la lista local con unidades propias (`up-find-local`);
3. llenar la remota con objetivos (`up-find-remote`);
4. comprobar los conteos;
5. fijar objeto/punto si procede;
6. emitir una orden (`up-target-objects` o `up-target-point`).

Las listas tienen 240 slots locales y 40 remotos. Una búsqueda puede acumular
resultados; copiar solo la última orden de una rutina ajena sin reproducir su
reset, filtros y conteos es un error lógico silencioso. `[FORO: AIREf DUC
tutorials][CORPUS]`

### 5.2. Estado de búsqueda

`up-get-search-state G` escribe cuatro goals consecutivos:

1. total local actual;
2. último conteo local;
3. total remoto actual;
4. último conteo remoto.

Deben ser goals extendidos. Para UP se reservan aquí 102–105, dentro del rango
seguro 41–508. `[FORO: AIREf up-get-search-state/data-limits][SIEGE][FORTY]`

### 5.3. Puntos

Un punto ocupa dos goals consecutivos `(x,y)`. Los comandos de punto no deben
usar los goals vanilla 1–40; este repo reserva 100–101. Para UP se adopta el
rango conservador 41–510. `[FORO: AIREf Points/data-limits][UP]`

`up-path-distance P opción cmp valor` compara la distancia desde el target
object actual al punto `P`; 65.535 representa inalcanzable. No escribe la
distancia en un goal. `[FORO: AIREf up-path-distance]`

### 5.4. Target object y órdenes

- `up-set-target-object search-local c: 0` usa índice **base cero**. Si el
  índice es inválido conserva el target anterior; por eso debe validarse el
  conteo para no operar sobre un target obsoleto. `[FORO: AIREf]`
- En `up-target-objects`, opción `1` usa el target fijado; opción `0` reparte la
  lista local entre la remota. El motor divide en grupos de hasta 20 unidades.
  `[FORO: AIREf]`
- `action-default`/`action-move` pueden entrar en conflicto con TSA defensivo
  mientras este esté bloqueado; patrulla o desbloqueo/ajuste de town size son
  alternativas documentadas. `[FORO: AIREf]`

### 5.5. Rendimiento

Búsquedas, pathfinding y órdenes DUC son de complejidad alta o muy alta. AIREf
sitúa el umbral de lag de un pase alrededor de 20 ms. La defensa práctica es
temporizar, limitar cardinalidad, evitar búsquedas redundantes y no ordenar
centenares de unidades una por una. `[FORO: AIREf command-performance y
data-limits][CORPUS]`

## 6. Construcción, economía y combate

### 6.1. Muros

`build-wall` y `build-gate` no bastan: `enable-wall-placement <perímetro>` debe
ejecutarse una vez al inicio para que el motor planifique esa línea. El
perímetro 1 suele ser interior respecto al 2 y la planificación también separa
otros edificios de la futura muralla. `[CPSB][FORO: AIREf]`

### 6.2. Reparación

No existe una acción directa CPSB llamada `repair`/`can-repair`. Eso no
significa que la IA sea incapaz de reparar: el comportamiento automático se
controla, entre otros mecanismos, con `sn-object-repair-level` en UP. No se
debe prometer selección DUC + orden de reparación como si hubiese una acción
nativa. `[CPSB: ausencia de acción tras doble búsqueda][FORO: AIREf SN 246]`

### 6.3. Mercado

Las commodities comprables/vendibles son food, wood y stone; gold es la
moneda. Las tecnologías usan sus identificadores `ri-*`, salvo las edades,
que se investigan como `feudal-age`, `castle-age` e `imperial-age`.
`[CPSB][CORPUS][REPO: Script_Errors.md]`

### 6.4. Separar macro y micro

TSA (`sn-minimum/maximum-town-size`, grupos de ataque/defensa y prioridades)
resuelve control agregado barato. DUC debe reservarse para tareas en las que
la selección exacta aporta valor: cargar arietes, enfocar una amenaza,
retirada, brecha o guardia. Usar ambos sin arbitraje puede dar órdenes
contradictorias. `[CPSB][FORO: AIREf][CORPUS]`

## 7. Arquitecturas aprendidas del corpus

| IA | Patrón útil | Riesgo al copiar |
|---|---|---|
| Barbarian 2.18 | Árbol grande de estrategias, goals nombrados, DUC y especialización por apertura. `[CORPUS]` | Sus aliases, flags y módulos cargados no son builtins. |
| The General 1.3 | Librería modular de “funciones”, resets explícitos y pipelines DUC. `[CORPUS]` | Copiar el cuerpo sin init/retorno/reset rompe precondiciones. |
| The Horde 3.9 | Monolito autocontenido con constantes inline. `[CORPUS]` | Es fácil crear colisiones y difícil aislar el orden global. |
| Promi | Módulos tácticos y uso intensivo de TSA/DUC. `[CORPUS]` | Algunos valores extremos son decisiones estratégicas, no defaults universales. |
| Kaia | Estructura pequeña, goals/init legibles. `[CORPUS]` | Su menor cobertura no sustituye pruebas de mapas/civs. |
| Training | Ejemplos pedagógicos de reglas clásicas. `[CORPUS]` | No representa la complejidad UP moderna. |

Conclusión arquitectónica: un entrypoint corto, constantes/init primero,
responsabilidades separadas y rearmes al final hacen auditable el orden. Un
monolito puede funcionar —The Horde lo demuestra—, pero exige disciplina de
namespaces y secciones. `[CORPUS]`

## 8. Radiografía actual del repositorio

### 8.1. Métricas ejecutables tras la corrección

| Proyecto | `.per` ejecutables | Líneas | Reglas | `defconst` | llamadas `up-*` ejecutables | Estilo |
|---|---:|---:|---:|---:|---:|---|
| `semiUtils` | 1 | 1.511 | 145 | 19 | 0 | monolito AoC clásico |
| `forty` | 1 | 1.534 | 101 | 624 | 36 | monolito UP autocontenido |
| `siege` | 7 | 1.171 | 115 | 27 | 65 | entrypoint + 6 módulos |
| `siege`, incluyendo su catálogo UP | 8 | 2.014 | 115 | 627 | 65 | paquete distribuible |

`[REPO: conteo sobre texto sin comentarios; “ejecutable” excluye comentarios y,
en Siege, separa UserPatchConst.per]`

Las tres copias canónicas revisadas de `UserPatchConst.per` —raíz, Siege y The
General— comparten SHA-256
`0078494b12489b1e6de3e91a167c95bbadb75858911e83ceb93d15533064b3e8`.
`[REPO: sha256sum]`

### 8.2. `siege`

**Diseño.** `siege.per` expande, en orden, constantes, init, economía,
construcción, entrenamiento y combate; después rearma `t-micro` y `t-eco`.
La economía prioriza madera/oro, el ejército combina asedio, infantería de
carga/escolta y rango, y el combate mezcla TSA con DUC. `[SIEGE]`

**Defectos hallados y corregidos:**

| Hallazgo anterior | Riesgo | Corrección |
|---|---|---|
| `up-get-point`/`up-path-distance` usaban goals 20–21. | Los puntos requieren un par extendido. `[FORO: AIREf]` | `gl-pt1` pasó a 100–101. |
| `up-get-search-state` usaba 30–33. | Cuaterna vanilla ilegal. `[FORO: AIREf]` | Estado DUC pasó a 102–105. |
| Tres rutinas usaban `this-any-enemy` sin fact wildcard en la regla. | Variable inválida; target anterior/valor no fiable. `[CPSB]` | Se usa `up-find-player enemy find-closest gl-temp`. |
| El linter recorría módulos alfabéticamente. | Su análisis de timers no reproducía la carga real. `[SIEGE]` | Orden explícito `const→init→eco→build→train→combat→entrypoint`. |

### 8.3. `forty`

**Diseño.** Forty embebe el catálogo UP y combina cuatro máquinas: modo del
director, fase urbana, oleada y chat inicial; añade dos perímetros de muralla,
economía, distrito militar y micro DUC. `[FORTY]`

**Defectos hallados y corregidos:**

| Hallazgo anterior | Efecto estático | Corrección |
|---|---|---|
| `gl-mode`, `gl-city`, `gl-wave` y `gl-first-chat` no se inicializaban. | Arrancaban en `-1`; director, ciudad, oleadas y saludo quedaban sin entrada. `[UP][FORTY]` | Init asigna `m-grow`, `cty-aldea`, `0`, `0`. |
| `cty-muralla→cty-plaza` exigía castillo, pero el único build de castillo exigía `cty-plaza`. | Ciclo de dependencia sin productor accesible. `[FORTY]` | La transición exige las torres; al entrar en plaza se habilita el castillo. |
| Estado DUC en 30–33. | Cuaterna no extendida. `[FORO: AIREf]` | 102–105; el par reservado quedó en 100–101. |
| Dos rutinas usaban `this-any-enemy` sin enlace. | Selección de jugador inválida. `[CPSB]` | `up-find-player enemy find-closest`. |

Que el linter pase no demuestra todavía que las paredes cierren ni que el
balance alcance Imperial: eso pertenece a la prueba Forty vs Forty de §11.
`[RUNTIME-pendiente]`

### 8.4. `semiUtils`

**Diseño.** Es un único script de conquistador diplomático: tres goals
(personalidad, modo, diplomacia), tres timers, macro clásica, muralla,
producción, all-in, taunts y cambios de postura; no llama a comandos `up-*`.
`[SEMIUTILS]`

**Defectos hallados y corregidos:**

| Hallazgo anterior | Riesgo | Corrección |
|---|---|---|
| Construía muros/puerta sin `enable-wall-placement`. | No había planificación del perímetro. `[CPSB][FORO: AIREf]` | Init habilita perímetro 1. |
| Tres reglas all-in estaban duplicadas byte a byte. | Evaluación redundante y mantenimiento ambiguo. `[SEMIUTILS]` | Se conserva una copia. |
| Nueve signos `¡` estaban en Latin-1 dentro de seis chats. | El archivo no era ASCII/UTF-8 limpio. `[SEMIUTILS]` | Chats convertidos a ASCII; CRLF preservado. |
| Doce facts pasaban `this-any-*` a `stance-toward`. | AIREf/CPSB no permiten rule variables como facts. | Los facts wildcard/taunts enlazan al jugador y las acciones usan la variable. |
| Consumidores rearmaban timers antes de reglas posteriores. | El primer match podía ocultar el trigger. `[CPSB]` | Consumidores primero; rearmes disjuntos al final. |
| La regla de boom podía pisar defensa en el mismo pase. | `m-defend` seguido de `m-boom` con ejército bajo. `[SEMIUTILS]` | El retorno a boom exige no estar bajo ataque. |

La aceptación de taunts ahora toma al emisor enlazado como autoridad y aplica la
postura en la acción; probar alianzas con varios jugadores sigue pendiente.
`[CPSB][SEMIUTILS][RUNTIME-pendiente]`

## 9. Linter: cobertura real y límites

`tools/lint_siege.py` acepta exactamente `siege`, `forty` o `semiUtils`; un typo
sale con código 2 en vez de validar Siege silenciosamente. `[REPO]`

Cobertura actual:

- resolución de identificadores, colisiones `defconst`, comandos y aridades;
- paréntesis, loads, facts/acciones y máximo de 16 elementos;
- posiciones de research, commodities y slots DUC;
- ASCII, goals/timers nombrados y duración/cuenta válidas;
- pares/cuaternas extendidos para los comandos DUC usados por el repo;
- enlace, alcance y acciones permitidas de `this-any-*`;
- máquinas de estado cuya totalidad de escrituras depende de su propio estado;
- reglas exactamente duplicadas;
- `build-wall`/`build-gate` sin `enable-wall-placement`;
- consumidores/rearmes de timer en orden global real.

`[REPO: tools/lint_siege.py]`

La suite `tools/test_lint_siege.py` ejecuta nueve tests y tarda unos 16 s en
este entorno. `[REPO: unittest 2026-10-13]`

Límites deliberados: no prueba disponibilidad por civilización/mapa, economía,
pathfinding, cierre físico de murallas, calidad de targets, balance, ni todos
los comandos de punto/cost data existentes. Tampoco reemplaza el parser del
juego. `[REPO][RUNTIME-pendiente]`

## 10. Ecosistema de herramientas evaluado

| Proyecto (commit revisado) | Utilidad para este repo | Límite |
|---|---|---|
| [AIREf](https://github.com/airef/airef.github.io) `2f4bbd15702c`, 2026-10-07 | Mejor índice vivo de comandos, SNs, DUC, bugs y límites. | Mezcla presentación UP/DE en algunos máximos; fijar versión. |
| [The General](https://github.com/airef/the-general-ai) `ba107be745a6`, 2025-08-24 | Referencia UP modular y biblioteca DUC. | Un patrón depende de su cadena completa de loads/goals. |
| [AI Strategy Builder](https://github.com/TMB-2197/aoe2-ai-strategy-builder) `1a3773ee598e`, 2026-10-08 | Genera estrategias para DE y UP 1.5 desde hojas; documenta dependencias y reparto eco. | Versión 1.0 alpha; README advierte bugs y documentación desactualizada. |
| [AlphaScripter](https://github.com/mboop127/AlphaScripter) `0b39ba61c6af`, 2023-05-07 | Evolución genética y partidas automáticas específicamente en AoC UP 1.5. | Requiere Python 32-bit, Windows, DLL y trabajo de configuración. |
| [PyAge2](https://github.com/kachayev/pyage2) `adf87e0deedd`, 2021-07-12 | Entorno Gym y simulación acelerada; README declara pruebas en UP 1.5/1.6. | Inyección Win32 no oficial; riesgo de crash/ban fuera de investigación; proyecto antiguo. |
| [AoE2 AI Module](https://github.com/FLWL/aoe2-ai-module) `a6a550d148de`, 2021-02-26 | API/DLL para observar y controlar el juego; dependencia de PyAge2. | No es un `.per` portable y modifica proceso. |
| [aoc-ai-parser](https://github.com/FLWL/aoc-ai-parser) `2e08fc7b0909`, 2019-04-26 | AST/generación experimental para AoC. | Cobertura y mantenimiento limitados. |
| [aoe2-aiscript](https://github.com/Jvinniec/aoe2-aiscript) `02054e0fb6a1`, 2020-09-28 | Resaltado/tooltips para editar. | No sustituye parser ni prueba runtime. |
| [AgeSharp](https://github.com/01010100b/AgeSharp) `aad136c5f42e`, 2024-11-17 | Contraste moderno de intrinsics y generación. | Orientación/abstracciones DE; no prueba UP. |
| [lewisc64/aoe2ai](https://github.com/lewisc64/aoe2ai) `966e7ecb0079`, 2025-05-08 | DSL moderno y ejemplos DUC legibles. | Mezcla semántica/IDs modernos; validar cada emisión para UP. |

`[FORO: metadatos y README de cada repositorio, consultados 2026-10-13]`

**Pipeline recomendado:** edición + linter local → smoke test en juego → lote de
partidas con AlphaScripter/aoc-auto-game o PyAge2 en una máquina Windows aislada
→ análisis de recs/logs → cambio de un parámetro por iteración.
`[REPO][FORO: AlphaScripter/PyAge2]`

## 11. Plan de validación en el juego

### 11.1. Smoke test común

Configuración mínima: AoC 1.0c + UP 1.5, mapa Arabia conocido, recursos
estándar, una IA auditada contra una IA estable. `[RUNTIME-pendiente]`

Criterios:

1. no aparece diálogo `ERR*` al cargar;
2. se ejecuta el chat/init esperado;
3. la IA crea aldeanos, casas, dropsites y avanza de edad;
4. una partida guardada/replay permite localizar el primer bloqueo;
5. repetir al menos con población 75 y 200 para descubrir umbrales codificados.

### 11.2. Forty vs Forty

- Antes de 10 s debe aparecer “el feudo despierta”.
- Al llegar a Feudal debe entrar en villa y construir market/blacksmith/militar.
- En Castillo y con 22 casas debe entrar en muralla, levantar torres y ambos
  perímetros.
- Con dos torres debe anunciar el inicio de plaza y comenzar el castillo.
- Con masa militar debe alternar grow/attack/defend y activar oleada DUC.
- Registrar si `sn-number-attack-groups 200` fragmenta demasiado el ejército.

`[FORTY][RUNTIME-pendiente]`

### 11.3. Siege

- Verificar que el primer DUC toma al enemigo más cercano y no conserva target
  obsoleto.
- Observar arietes contra muro/puerta, transición de brecha por path distance y
  time-box, carga de infantería y paso posterior a edificios.
- Verificar fuego concentrado y `action-guard`, los dos comportamientos que la
  validación estática no puede confirmar.
- Medir duración del pase al aumentar asedio y reducir frecuencia si aparece
  lag.

`[SIEGE][RUNTIME-pendiente]`

### 11.4. SemiUtils

- Confirmar que el perímetro 1 se planifica antes de Feudal y recibe puerta.
- Probar 1v1, FFA con varias IAs y humano+IA: taunts 201–204, 31 y 38.
- Comprobar que cada trigger de director puede ejecutar consumidores y que el
  rearme final queda en 12/15 s según edad, 8/12 s según modo y 30/45 s según
  diplomacia.
- Confirmar que el failsafe bilateral no genera spam ni impide alianzas futuras.

`[SEMIUTILS][RUNTIME-pendiente]`

## 12. Fronteras del conocimiento y pendientes

1. **No se declara “funcional en partida” todavía.** Las tres ejecuciones del
   linter pasan, pero no se ejecutó AoC en este entorno. `[RUNTIME-pendiente]`
2. **DUC inválido tenía efecto runtime no determinado.** Antes de la corrección
   no se pudo distinguir entre rechazo, valor inválido o target conservado; ya
   no se depende de ese comportamiento. `[RUNTIME-pendiente]`
3. **Balance abierto:** Forty/Siege usan valores agresivos de grupos y searches;
   son legales, no necesariamente óptimos. `[CPSB][CORPUS][RUNTIME-pendiente]`
4. **Cobertura futura del linter:** generalizar metadatos de firmas desde una
   fuente versionada UP, detectar más pares/cuaternas y modelar grafos de
   productores/consumidores sin introducir falsos positivos. `[REPO]`
5. **Próximo paso con mayor retorno:** ejecutar la matriz de §11, conservar
   replay/log y documentar cada observación como `[RUNTIME]`.

## 13. Comandos de reproducción

```bash
python3 tools/lint_siege.py . siege
python3 tools/lint_siege.py . forty
python3 tools/lint_siege.py . semiUtils
python3 -m unittest -v tools.test_lint_siege
```

Los cuatro comandos pasan en el commit de esta investigación.
`[REPO: verificación 2026-10-13]`

## 14. Fuentes principales

- Ensemble Studios, *Computer Player Strategy Builder*:
  [`reference/CPSB.pdf`](../reference/CPSB.pdf). `[CPSB]`
- Catálogo de constantes UP:
  [`reference/UserPatchConst.per`](../reference/UserPatchConst.per). `[UP]`
- AIREf, [Commands](https://airef.github.io/commands/commands-index.html),
  [Data Limits](https://airef.github.io/resources/articles/data-limits.html),
  [Introduction to DUC](https://airef.github.io/resources/articles/enmipho-intro-to-duc.html),
  [Leif's DUC tutorial](https://airef.github.io/resources/articles/leif-duc-tutorial-1.html),
  [Command Performance](https://airef.github.io/resources/articles/command-performance.html)
  y notas UP. `[FORO]`
- Corpus local y procedencia:
  [`reference/ais/README.md`](../reference/ais/README.md). `[CORPUS]`
- Historial de errores del proyecto:
  [`../Script_Errors.md`](../Script_Errors.md). `[REPO][RUNTIME]`

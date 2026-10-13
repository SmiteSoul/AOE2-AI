# Diseño de FORTY: la ciudad-fortaleza como feudo medieval

> **Tarea 8 (Paso 1).** Diseño del `forty.per` unificado a partir de la
> investigación de asentamientos medievales (feudos, villas, plazas
> fuertes). Etiquetas de procedencia de TODA afirmación: `[CPSB]`,
> `[CORPUS]`, `[RUNTIME]`, `[FORO]`, `[FOLKLORE]`, `[INVESTIGACION]`
> (historia medieval). El código implementado usa únicamente
> identificadores verificables.

---

## 1. La investigación: cómo se organizaba un feudo

`[INVESTIGACION]` Fuentes de historia medieval (English Heritage, History
Extra, historiadores de urbanismo medieval). Hallazgos que gobiernan el
diseño:

| Concepto medieval | Qué era | Traducción al motor AoC |
|---|---|---|
| **Castillo fuerte / keep** | Torreón de piedra, refugio y símbolo del señor | `(build castle)` |
| **Bailey (patio)** | Recinto de servicios: establos, almacenes, talleres, guarnición | Anillo denso de edificios militares/económicos |
| **Frentes de burgage** | Parcelas largas y estrechas desde la calle; la casa forma CALLE, el huerto detrás | Las casas en fila = el muro urbano |
| **Muralla + torres** | Cortina con torres redondas, puertas con peaje | `watch-tower` + anillo de casas (ver §2) |
| **Plaza de mercado** | Corazón comercial: mercado, ayuntamiento, casas de gremio | `(build market)` |
| **Iglesia parroquial** | Centro espiritual y administrativo | `(build monastery)` |
| **Villa / burgo** | Calle principal + calle trasera + barrios por oficio | Fases de construcción secuencial |
| **Bailiff (administrador)** | Gestión diaria: aldeanos, cosechas, obras, defensa | El DIRECTOR (state machine + timers) |
| **Mesnada y arqueros** | Fuerza del señor: piqueros, ballesteros, retenes | `spearman-line` / `archer-line` / `skirmisher-line` |
| **Máquinas de asedio** | Arietes, trabucos, mangoneles | `battering-ram-line` / `trebuchet` |

### La limitación dura del motor `[CORPUS]`

**Los AIs de AoC no pueden construir murallas ni puertas.** Verificado en
los 50 archivos de AIs de élite del corpus (incluida *Brutal2*, que es un
AI de Arena): **0 usos** de `(build wall)`, `(build gate)`,
`(build fortified-wall)`. Lo que el corpus SÍ hace en masa:

- `up-assign-builders c: watch-tower c: 3` (28×) — torres con cuadrillas;
- `up-assign-builders c: castle c: 4` (10×) — castillos urgentes;
- `(can-build castle)` (81×), `(can-build watch-tower)` (61×).

Por tanto la **muralla medieval se emula como las IAs de élite fortifican
de verdad**: el anillo de casas (burgage) + torres (muralla) + castillo
(keep) + edificios densos (bailey). Es el patrón de `brutal2.per` y de la
literatura del foro `[CORPUS][FORO]`.

---

## 2. Estructura del archivo único (`forty/forty.per`)

1334 líneas autocontenidas: `.ai` (vacío) + `.per` con TODO dentro
(constantes UP inlineadas — mismo diseño monolito que *The Horde*
`[CORPUS]`). Orden de secciones:

1. **Constantes propias** — namespaces:
   - `gl-mode` (herencia directa de `v1`): `m-grow` / `m-defend` / `m-attack`.
   - `gl-city`: fases urbanas `cty-aldea` → `cty-villa` → `cty-muralla` → `cty-plaza`.
   - `gl-wave`, `gl-first-chat`, `gl-temp`, `gl-pt1`, `gl-local-total` (DUC).
2. **INIT de velocidad y respuesta** — SNs verificadas en corpus/foros:
   - `sn-initial-exploration-required 0` y `sn-defer-dropsite-update 1`:
     descubrimiento y campamentos sin esperas `[RUNTIME]`.
   - `sn-percent-enemy-sighted-response 100` + radio 100: respuesta
     táctica inmediata `[CPSB][RUNTIME]`.
   - `sn-allow-civilian-defense 1` + `sn-gather-defense-units 1`: los
     aldeanos huyen/luchan si atacan el feudo (patrón de `init.per`).
   - Grupos escalonados 2-12 con `scale-*-attack-group-size 0` y
     `group-form-distance 30` (la "oleada" que documentamos en Task 7).
3. **DIRECTOR** (`t-director`) — el bailiff: cambia `gl-mode` (defensa si
   atacan la ciudad; asalto si hay ejército ≥35 o trabuco; si no, crecer)
   y `gl-city` (aldea→villa al llegar a Edad Feudal; villa→muralla con
   22 casas + Edad de los Castillos; muralla→plaza con castillo + 2
   torres). Cada transición anuncia el estado por chat.
4. **Economía** — aldeanos (hasta 110), casas, molino, campamentos con
   regla de distancia (`dropsite-min-distance`), granjas con reserva de
   madera >120 (anti-deadlock), reconstrucción del TC con
   `up-assign-builders c: town-center-foundation c: 4` (patrón corpus 18×).
5. **Construcción por fases** (la doctrina urbana):
   - **aldea**: la economía (casas/granja/campamentos);
   - **villa**: `market` (plaza) + `blacksmith` (gremio) + 2 `barracks` +
     2 `archery-range` (cuarteles) + `monastery` (iglesia, Edad de los
     Castillos);
   - **muralla**: hasta 6 `watch-tower` con cuadrilla de 3 + densificación
     de casas a 30 (el anillo burgage);
   - **plaza**: 2 `castle` con cuadrilla de 4 + `siege-workshop` +
     `stable` + `university` + torres a 10 + casas a 42.
6. **Investigación** (rápida, estilo Barbarian): edades tempranas
   (25/32/75 aldeanos), economía (`ri-loom`, `ri-double-bit-axe`,
   `ri-horse-collar`, `ri-gold-mining`, `ri-wheel-barrow`,
   `ri-stone-mining`), militar (`ri-fletching`, `ri-bodkin-arrow`,
   `ri-ballistics`, `ri-chemistry`, `ri-pikeman`, `ri-halberdier`,
   `ri-elite-skirmisher`, `ri-siege-engineers`) y las dos joyas de
   corona: `my-unique-unit-upgrade` y `my-unique-research`
   `[CPSB][CORPUS: 56×/114× en el corpus]`.
7. **Milicia** — piqueros (35), arqueros (45), hostigadores (15), unidad
   única del señor (20), arietes (6), trabucos (4).
8. **Defensa** — `sn-number-defend-groups` por modo (6 defendiendo,
   3 creciendo, 2 asaltando).
9. **Asalto organizado** — oleada con `sn-number-attack-groups 200`,
   `attack-now`, TSA progresiva (`sn-maximum-town-size +10` cada `t-push`
   hasta 180) y repliegue a defensa si atacan nuestra ciudad.
10. **Micro DUC** (Task 7): fuego concentrado de arqueros/hostigadores
    con `formation-stagger` sobre el enemigo con mejor
    `player-number` (`this-any-enemy`, `sn-focus-player-number`) y
    **asedio que prioriza edificios** (castillo → TC → torres → resto).
11. **Mercado y cuentas** (`t-eco`): comprar piedra para el castillo,
    vender madera de sobra, comprar comida si falta, y el reparto de
    aldeanos por fase (60/35/5/0 → 45/35/20/0 → 40/30/20/10 →
    35/25/25/15).
12. **Timers** — armado inicial + rearme SIEMPRE al final (regla de
    `docs/01`).

### Fases de la ciudad (resumen)

| Fase | Condición de avance | Se construye |
|---|---|---|
| `cty-aldea` | edad ≥ Feudal | casas, granja, molino, campamentos |
| `cty-villa` | edad ≥ Castillo + 22 casas | market, blacksmith, barracks, archery-range, monastery |
| `cty-muralla` | castillo + 2 torres | torres ×6, casas a 30, piedra |
| `cty-plaza` | — (estado final) | castillo ×2, siege-workshop, stable, university, torres ×10, casas a 42 |

---

## 3. Modos del director (herencia semiUtils/v1)

| Modo | Entrada | Efecto |
|---|---|---|
| `m-grow` | default | ciudad crece; 3 grupos defensivos |
| `m-defend` | `town-under-attack` (o ejército <15) | 6 grupos defensivos; sin asalto |
| `m-attack` | ejército ≥35 o trebuchet disponible | oleada + TSA + micro |

Es la misma máquina de `forty v1` (`gl-mode`) alimentada por eventos del
motor, tal como analizamos en `docs/05`.

---

## 4. Verificación y prueba

- **Lint**: `python3 tools/lint_siege.py . forty` → OK sin errores
  (mismo motor que validó siege; ahora parametrizado por proyecto).
  Regresión siege: `python3 tools/lint_siege.py . siege` → OK.
- **Prueba funcional (la del usuario)**: forty vs forty en DE. Criterios
  observables: ambas IAs pasan de aldea a villa, levantan plaza con
  market/blacksmith, se amurallan con torres y casas, llegan al castillo,
  y se atacan con oleadas escalonadas y arietes que van a por edificios.
- **Paso 2 pendiente** (mejoras iterativas, documentadas): defensa
  coordinada con `up-retreat-now`/`up-gather-inside`/`up-loop`,
  `sn-free-siege-targeting`, más doctrinas de plaza, unidades de élite
  (`ri-elite-cavalier`...), y ajuste de tiempos según las partidas de
  prueba.

## 5. Instalación

Copiar `forty/forty.ai` y `forty/forty.per` en la carpeta `AI/` del
juego (UserPatch 1.5). Sin dependencias: es un solo par de archivos.

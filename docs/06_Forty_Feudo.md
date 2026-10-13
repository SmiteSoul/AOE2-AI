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
| **Muralla + torres + puertas** | Cortina de empalizada/piedra con torres y puertas | `build-wall` perímetro 1 (empalizada→piedra) y 2 (piedra), `build-gate`, `watch-tower` |
| **Plaza de mercado** | Corazón comercial: mercado, ayuntamiento, casas de gremio | `(build market)` |
| **Iglesia parroquial** | Centro espiritual y administrativo | `(build monastery)` |
| **Villa / burgo** | Calle principal + calle trasera + barrios por oficio | Fases de construcción secuencial |
| **Bailiff (administrador)** | Gestión diaria: aldeanos, cosechas, obras, defensa | El DIRECTOR (state machine + timers) |
| **Mesnada y arqueros** | Fuerza del señor: piqueros, ballesteros, retenes | `spearman-line` / `archer-line` / `skirmisher-line` |
| **Máquinas de asedio** | Arietes, trabucos, mangoneles | `battering-ram-line` / `trebuchet` |

### El sistema real de murallas del motor `[CORPUS][FORTY v1/v2]`

**Los AIs de AoC SÍ construyen murallas y puertas**, con un juego de
comandos propio que el forty v1 y el fortyV2 ya usaban (está en
`forty/legacy/`) y que también aparece en el corpus de AIs de élite:

| Comando / hecho | Uso | Evidencia |
|---|---|---|
| `(enable-wall-placement <perimetro>)` | Habilita la planificación del perímetro 1 (exterior) o 2 (interior) | corpus 7×, forty v1/v2 |
| `(can-build-wall <perimetro> <tipo>)` / `(build-wall ...)` | Coloca el tramo siguiente: `palisade-wall` (empalizada) o `stone-wall`/`stone-wall-line` (piedra) | corpus 11×, forty v1/v2 |
| `(can-build-gate <perimetro>)` / `(build-gate <perimetro>)` | Puertas por donde salen las tropas | corpus 6×, forty v1/v2 |
| `(wall-completed-percentage <perimetro> <cmp> <pct>)` | % de muralla hecho, por perímetro | corpus 60×, forty v1/v2 |
| `(research ri-fortified-wall)` | Piedra → muralla fortificada | corpus 8×, fortyV2 |
| `sn-percent-civilian-builders` / `sn-cap-civilian-builders` | Cuadrillas dedicadas a la obra de muralla | corpus 9×/21×, forty v1/v2 |

**La doctrina de los DOS perímetros** (exactamente como el forty
original, heredado en el unificado):

1. **Feudal** — perímetro **exterior (1)** en **empalizada**
   (`build-wall 1 palisade-wall`), con `build-gate 1` cuando el tramo
   lleva >15% hecho.
2. **Castillo** — el exterior se reconstruye en **piedra**
   (`build-wall 1 stone-wall`) y nace el perímetro **interior (2)**,
   también de piedra, cuando el exterior supera el 45%.
3. **Imperial** — `ri-fortified-wall` endurece la cortina.

El anillo de casas (burgage), las torres y el castillo siguen
importando: completan la fortaleza POR DENTRO (plaza, servicios,
guarnición), como el bailey medieval.

*(Nota de método: mi análisis anterior dijo "0 usos de `(build wall)`"
— un grep mal enfocado: el comando real es `build-wall` con perímetro y
tipo. Corregido aquí y en el código.)*

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
   - **muralla**: la **muralla de doble perímetro** (sección propia:
     empalizada→piedra exterior + piedra interior, ver §1) + hasta 6
     `watch-tower` con cuadrilla de 3 + densificación de casas a 30
     (el anillo burgage);
   - **plaza**: 2 `castle` con cuadrilla de 4 + **2º `town-center`**
     (doctrina eco-expand) + `siege-workshop` ×2 + distrito militar
     ampliado (`barracks` ×3, `archery-range` ×3, `stable` ×2,
     `monastery` ×2, `university`) + `bombard-tower` ×4 en Imperial +
     torres a 10 + casas a 42.
6. **Murallas: doble perímetro** (herencia forty v1/v2, ver §1):
   `enable-wall-placement 1/2`; perímetro exterior de **empalizada** en
   Feudal → **piedra** en Castillo; perímetro interior de piedra desde
   Castillo; `build-gate` en cada tramo; constructores dedicados mientras
   quede muralla; `ri-fortified-wall` en Imperial.
7. **Investigación** (rápida, estilo Barbarian): edades tempranas
   (25/32/75 aldeanos), economía (`ri-loom`, `ri-double-bit-axe`,
   `ri-horse-collar`, `ri-gold-mining`, `ri-wheel-barrow`,
   `ri-stone-mining`), militar (`ri-fletching`, `ri-bodkin-arrow`,
   `ri-ballistics`, `ri-chemistry`, `ri-pikeman`, `ri-halberdier`,
   `ri-elite-skirmisher`, `ri-siege-engineers`) y las dos joyas de
   corona: `my-unique-unit-upgrade` y `my-unique-research`
   `[CPSB][CORPUS: 56×/114× en el corpus]`.
8. **Milicia** — piqueros (35), arqueros (45), hostigadores (15), unidad única del señor (20), arietes (6), trabucos (4).
9. **Defensa** — `sn-number-defend-groups` por modo (6 defendiendo,
   3 creciendo, 2 asaltando) + **defensa coordinada de UserPatch**:
   la guarnición se refugia en TC/castillo/torres con
   `up-gather-inside` mientras atacan y sale al calmarse;
   `up-retreat-now` (retirada al centro) si el ejército < 12 con la
   ciudad atacada; puntería del asedio por modo con
   `sn-free-siege-targeting` (asalto: solo edificios; defensa: los
   trabucos disparan unidades — valores documentados por Barbarian
   `[CORPUS]`, SN clásico 282).
10. **Asalto organizado** — oleada con `sn-number-attack-groups 200`,
   `attack-now`, TSA progresiva (`sn-maximum-town-size +10` cada `t-push`
   hasta 180) y repliegue a defensa si atacan nuestra ciudad.
11. **Micro DUC** (Task 7): fuego concentrado de arqueros/hostigadores
    con `formation-stagger` sobre el enemigo con mejor
    `player-number` (`this-any-enemy`, `sn-focus-player-number`) y
    **asedio que prioriza edificios** (castillo → TC → torres → resto).
12. **Mercado y cuentas** (`t-eco`): comprar piedra para el castillo,
    vender madera de sobra, comprar comida si falta, y el reparto de
    aldeanos por fase (60/35/5/0 → 45/35/20/0 → 40/30/20/10 →
    35/25/25/15).
13. **Timers** — armado inicial + rearme SIEMPRE al final (regla de
    `docs/01`).

### Fases de la ciudad (resumen)

| Fase | Condición de avance | Se construye |
|---|---|---|
| `cty-aldea` | edad ≥ Feudal | casas, granja, molino, campamentos |
| `cty-villa` | edad ≥ Castillo + 22 casas | market, blacksmith, barracks, archery-range, monastery |
| `cty-muralla` | castillo + 2 torres | torres ×6, casas a 30, murallas de piedra (perímetros 1 y 2) |
| `cty-plaza` | — (estado final) | castillo ×2, 2º TC, siege-workshop ×2, cuarteles/gremios ampliados, bombard-tower ×4 (Imperial), torres ×10, casas ×42 |

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
  (mismo motor que validó siege; parametrizado por proyecto).
  Regresión siege: `python3 tools/lint_siege.py . siege` → OK.

### 4.1. Plan de prueba: forty vs forty `[RUNTIME-pendiente: el agente no
puede ejecutar el juego aquí; la partida la corre el usuario]`

**Configuración**: DE (o AoC+UP1.5), 1v1, Random Map (Arabia u
ocasionalmente Arena/BF para ver las murallas cerras), recursos
normales, victoria estándar.

**Criterios observables (checklist de la partida):**

| # | Momento | Qué debe verse |
|---|---|---|
| 1 | 0-10 min | Chat "el feudo despierta"; aldeanos a 25, granjas+campamentos, molino |
| 2 | ~min 12-16 | Edad Feudal → chat "la aldea se convierte en villa"; market+blacksmith+cuarteles; **empalizada del perímetro 1 con puertas** |
| 3 | ~min 20-28 | Edad de los Castillos; casas ≥22 → chat "la villa se amurallara"; **piedra reemplaza la empalizada; nace el perímetro 2**; torres |
| 4 | Cuando hay castillo + 2 torres | Chat "la plaza fuerte esta en pie"; castillo, 2º TC, taller de asedio |
| 5 | Ejército ≥35 o trabuco | Oleada: grupos de 2-12 avanzan con TSA; arietes van a castillo/TC/torres; arqueros con fuego concentrado |
| 6 | Atacan la ciudad | Chat de defensa; guarnición dentro de TC/castillo/torres; retirada al centro si el ejército < 12; trabucos disparan a unidades |
| 7 | Ambas murallas ≥100% | Constructores vuelven a la economía; `ri-fortified-wall` en Imperial |

### 4.2. Tabla de tiempos y umbrales (para ajuste según partidas)

| Parámetro | Valor actual | Dónde | Cómo ajustarla |
|---|---|---|---|
| `t-director` | 2 s inicial, luego 10 s | rearme al final | Si los modos tardan en reaccionar: bajar a 5-6 s |
| `t-micro` | 3 s | rearme al final | Si el micro es tosco: 2 s (coste de CPU) |
| `t-push` (TSA) | 8 s (+10 town-size) | oleada | Avance muy lento → 6 s; muy precipitado → 12 s |
| `t-eco` | 20 s | mercado+reparto | Inerte → 15 s |
| Edades (aldeanos) | 25 / 32 / 75 | investigación | Fast feudal → 22/28; boom → 28/36/85 |
| Oleada: entrada / salida | ejército ≥35 o trabuco / <15 o ataque a la ciudad | director | Más agresivo → 28/12; más conservador → 45/20 |
| Retirada (`up-retreat-now`) | ejército < 12 en defensa | defensa coordinada | Más valiente → 8; más cauto → 16 |
| Puertas del perímetro 1 | muralla > 15 % | murallas | Si las puertas salen pronto/tarde: 10-25 % |
| Inicio perímetro 2 | exterior > 45 % | murallas | Interior más temprano → 35 % |
| Límites de tropas | 35 piqueros / 45 arqueros / 15 hostigadores / 20 UU / 6 arietes / 4 trabucos | milicia | Según composición que venza en tus partidas |

**Procedimiento de ajuste**: cambiar UN parámetro por partida, anotar el
resultado en esta tabla (columna "resultado"), y confirmar. Desarrollo
medido: cada ajuste es un commit pequeño con la evidencia de la partida.

### 4.3. Paso 2 — estado

| Ítem | Estado | Evidencia |
|---|---|---|
| Defensa coordinada (`up-retreat-now` / `up-gather-inside`) | **Hecho** | corpus 22×/87× + semántica oficial UP-docs |
| `up-loop` | **No existe** — excluido | 0 en corpus, ausente en la lista oficial de UserPatch y en el catálogo; la enumeración real usa `up-jump-rule` (no necesaria aquí). Regla `agent.md` §2.2 aplicada |
| `sn-free-siege-targeting` | **Hecho** | SN clásico 282; semántica documentada por Barbarian `[CORPUS]` |
| Más doctrinas de plaza | **Hecho (fase 1)** | 2º TC, distrito militar, bombard-towers; **pendiente**: doctrina front-creep (avanzar siege-workshops), unidades de élite (`ri-elite-cavalier`...) |
| Ajuste de tiempos según partidas | **Tabla lista §4.2** | requiere las partidas forty vs forty del usuario |

## 5. Instalación

Copiar `forty/forty.ai` y `forty/forty.per` en la carpeta `AI/` del
juego (UserPatch 1.5). Sin dependencias: es un solo par de archivos.

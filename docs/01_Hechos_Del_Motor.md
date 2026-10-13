# 01 — Hechos del motor (base con evidencia etiquetada)

Todo lo que aparece aquí lleva etiqueta de procedencia. Este documento no es un
catálogo exhaustivo: si algo no está aquí ni en CPSB, se contrasta además con
`UserPatchConst.per`, AIREf y el corpus siguiendo `agent.md` §2; nunca se
concluye que “no existe” a partir de una sola búsqueda.

## 1. El modelo de resolución de identificadores (la regla más importante)

**[CPSB] [RUNTIME]** En AoC/UserPatch, todo token que no sea número, operador o
cadena debe **resolver** a un identificador definido. Si no resuelve →
`ERR2005: Invalid identifier` y el AI se para en esa línea.

Un token resuelve por exactamente una de estas vías:

| Vía | Ejemplo | Quién lo define |
|---|---|---|
| (a) Literal numérico | `3`, `-1` | el propio texto |
| (b) `defconst` de la **cadena de carga** | `ri-loom` no; `gl-ataque` sí, `stance-aggressive` sí | `UserPatchConst.per` + los `defconst` del script y de los ficheros que carga |
| (c) Builtin del motor (CPSB) | `enemy`, `feudal-age`, `battering-ram-line`, `castle`, `my-player-number` | el juego |

**[RUNTIME] [CORPUS]** Trampa mortal: un identificador puede **existir en otra IA
y no en la tuya**. Cada script define sus propios alias:

```perl
; Barbarian.per:1184 — alias LOCAL de Barbarian:
(defconst aggressive 0)
; ...por eso ESTO funciona en Barbarian pero da ERR2005 en un script que
; no define 'aggressive':
(up-target-objects 0 action-default -1 aggressive)
```

La constante nativa equivalente es `stance-aggressive` (definida en
`UserPatchConst.per`). Este fue el error real de siege en `combat.per:103`.

**Regla**: copiar del corpus solo es válido si el token es builtin del motor o
si **también defines** el `defconst` en tu cadena de carga.

## 2. Constantes del sistema **[CPSB]**

El motor define por cada jugador: `my-player-number`, `my-civ`,
`my-unique-unit`, `my-unique-unit-upgrade`, `my-unique-research`. Las dos
últimas son la vía correcta para tecnologías de civilización (élite de la UU y
tech única del castillo) — nunca `ri-my-unique-elite-unit`.

## 3. `defconst` **[CPSB]**

- No puede redefinirse con **distinto** valor → `ERR2012: Constant Already
  Defined`. **Sí se permite** repetirlo con el **mismo** valor (citado textual
  del CPSB: «The error will not appear if the constant is defined more than once
  with the same value»).
- Algunas IAs redefinen constantes nativas redundantes (The Horde:
  `(defconst castle 82)` siendo `castle` builtin) — es legal si el valor cuadra,
  pero **no** prueba que el token no sea nativo.
- Prefija siempre tus constantes (`gl-`, `t-`, `sn-` no, nombres propios con
  sufijo): en foros hay casos de colisión entre ficheros cargados
  (`feudal`/`castle`/`imperial` como valores de goal chocando con defconsts de
  otros módulos) **[FORO: Steam, builder upgrades.per]**.

## 4. Reglas (`defrule`)

- **[CORPUS] [FORO]** Máximo **16 elementos** por regla (`ERR6002`). Recuento
  medido sobre Barbarian (su máximo real es 16): hecho/acción = 1 elemento;
  `or`/`and`/`not` = 1 + sus hijos. Objetivo recomendado: ≤ 15.
- **[CPSB]** Hechos antes de `=>`, acciones después (`ERR2008` si falta `=>`).
- **[CORPUS] [FORO]** `(goal X valor)` **solo compara igualdad**. Los
  comparadores `<`, `>`, `>=`, `<=` producen errores de sintaxis engañosos
  («Missing closing parenthesis»). Para rangos: reglas separadas por valor o
  `up-compare-goal`.
- **[RUNTIME]** `defconst` y `load` **no** van dentro de reglas.
- **[RUNTIME]** El script expandido debe contener ≥1 regla (`ERR8001`); un
  módulo cargado que solo declara constantes sí es válido (`siege/const.per` y
  `UserPatchConst.per` se cargaron en partidas reales).

## 5. Timers **[CPSB] [FORO: AIREf] [CORPUS]**

- Un timer está en uno de tres estados: disabled, running o triggered. Al
  agotarse queda en **triggered**, no en disabled.
- `(timer-triggered t)` puede ser verdadero en varias reglas y en varios pases,
  hasta que un `disable-timer` o un nuevo `enable-timer` cambie su estado.
- `enable-timer` reinicia el intervalo y limpia el trigger. Si varias reglas
  deben consumir el mismo pulso, el rearme debe ir **después** de todos sus
  consumidores en el orden global (= expansión de la cadena de `load`). Este
  es el invariante de `siege.per`, `forty.per` y `semiutils.per`.
- AoC 1.0c dispone de 10 timers por jugador; UserPatch, de 50.
  **[CPSB] [FORO: AIREf data-limits]**

## 6. Carga de ficheros **[RUNTIME]**

- `(load "carpeta\\modulo")` — el juego busca `carpeta\modulo.per` relativo al
  fichero actual; comprobado con rutas `siege\mod`.
- Si falta el fichero → `ERR5001: file open failed` **[FORO: BruteForce]**.
- `UserPatchConst.per` debe cargarse **antes** del primer comando `up-`; sin él,
  `position-self`, `action-move`, `search-local`, `stance-aggressive`… no
  resuelven.
- Requisito CPSB: cada IA necesita par `.ai` (vacío) + `.per` con el mismo nombre.

## 7. Mercado y recursos

- **[CORPUS] [CPSB]** Commodities de mercado: **`food`, `wood`, `stone`**.
  El oro es la moneda: `(buy-commodity gold)` → `ERR2005`.
- **[RUNTIME]** `(research ri-loom)` válido; `(research loom)` → `ERR2005`.
  Research = `ri-*` **o** nombres de edad (`feudal-age`, `castle-age`,
  `imperial-age`) **[CORPUS: Barbarian ×13]**.

## 8. UserPatch (`up-`)

- **[UP: changelog 2012-05-02]** Goals y timers comienzan en `-1`; toda máquina
  de estado debe inicializar su entrada explícitamente.
- **[FORO: AIREf data-limits]** UP ofrece goals 1–512. Los comandos que
  escriben pares/cuaternas automáticas no admiten los goals vanilla 1–40. El
  rango conservador del repo es 41–510 para puntos y 41–508 para
  `up-get-search-state`/cost data/guard state.
- **[FORO: AIREf]** `up-get-search-state G` escribe, en `G..G+3`, total local,
  último local, total remoto y último remoto.
- **[CPSB] [FORO: AIREf PlayerNumber]** Un fact con `any-*` enlaza
  `this-any-*` solo durante esa regla. La variable se usa en acciones
  compatibles, no como fact, y queda inválida fuera de la regla.
- **[RUNTIME]** UP 1.5 conoce nativamente los SNs extendidos (el bloque
  comentado de `UserPatchConst.per` no hace falta activarlo): `init.per` de
  siege carga SNs extendidos sin error.
- **[RUNTIME]** `sn-special-attack-type1 town-center` + `sn-special-attack-influence1` OK.
- **[CORPUS]** `up-target-objects <search> <accion> <formacion> <stance>` — 4
  slots: `0|1` (remoto/con `up-set-target-object`), `action-*`, `formation-*`
  (o `-1`), `stance-*` (o `-1`). Constantes stance nativas:
  `stance-aggressive 0`, `stance-defensive 1`, `stance-stand-ground 2`,
  `stance-no-attack 3` (`UserPatchConst.per:145-148`).
- **[CORPUS]** Operadores de hecho `g:` válidos (`game-time g:< gl-x`,
  `strategic-number g:== gl-y`, `cc-players-unit-type-count g:< goal n`).
- **[FORO: userpatch.aiscripters.net/unit.ids.html]** Trampas de conteo:
  los GROUP-ID solo funcionan con `cc-players-unit-type-count`
  (`players-unit-type-count` no los ve); las aldeanas enemigas (gold miner,
  etc.) solo se detectan con comandos `cc-`; posible bug de conteo en
  `watch-tower-line`.
- **[FORO: scripter64]** En 1.0c existe el «order list cache bug»: ordenar 100
  unidades atacar solo tarea 1 por turno; UP lo corrige. A 60fps las IAs
  reparten trabajo en tandas.

## 9. Strategic Numbers útiles **[FORO: guía Steam/CPSB]**

- `sn-initial-exploration-required 0` — sin esto, la IA no construye hasta
  explorar un % del mapa (¡no construye casas al inicio!).
- `sn-defer-dropsite-update 1` — sin esto, manda masas de aldeanos a
  dropsites lejanos a morir.
- `sn-dropsite-separation-distance` 3–5 para leñadores (el default 10 queda
  lejos) **[FORO: ladder aokh]**.
- Hay SNs documentados que **no funcionan** en la práctica **[FORO: aokh FAQ]**:
  verificar comportamiento, no solo sintaxis.

## 10. Codificación de ficheros **[FORO: aokh FAQ]**

Símbolos ocultos (UTF-8 con BOM, acentos de editores, comillas tipográficas)
producen errores in-game «imposibles de resolver». **Ficheros ASCII puros.**

## 11. Lo que NO existe (comprobado)

- Acciones directas `repair` / `can-repair`: **no están** en CPSB ni en el
  catálogo UP tras búsquedas por `repair`, `can-repair` y variantes. La IA sí
  puede reparar mediante su comportamiento automático, configurable en UP con
  `sn-object-repair-level`; lo que no existe es esa orden directa.
  **[CPSB] [FORO: AIREf SN 246]**
- `ri-fire-ship`, `ri-demolition-ship`, `ri-elite-cannon-galleon`: son
  unidades, no techs (ver `Script_Errors.md` §2.2–2.3).
- Comparadores en `(goal ...)`.
- `gold` como commodity.

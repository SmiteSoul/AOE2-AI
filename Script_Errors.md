# `Script_Errors.md`

# Registro de Errores de Compilación y Lógica — Scripts de IA para AoE2 (UserPatch 1.5)

Este documento recopila **todos los errores** que aparecieron durante el desarrollo, depuración y ensamblado de los scripts `forty.per`, `fortyV2.per` y `semiUtils.per`, junto con su **origen técnico** y la **solución aplicada**.

---

## Índice

1. [ERR6002 — Rule too long](#1-err6002--rule-too-long)
2. [ERR2005 — Identificadores inválidos en tecnologías](#2-err2005--identificadores-inválidos-en-tecnologías)
   - 2.1 [`ri-my-unique-elite-unit`](#21-ri-my-unique-elite-unit)
   - 2.2 [`ri-fire-ship`](#22-ri-fire-ship)
   - 2.3 [`ri-demolition-ship` y `ri-elite-cannon-galleon`](#23-ri-demolition-ship-y-ri-elite-cannon-galleon)
   - 2.4 [`scout-type`](#24-scout-type)
3. [Missing Closing Parenthesis — Comparadores en `goal`](#3-missing-closing-parenthesis--comparadores-en-goal)
4. [Comparaciones inválidas sobre `goal` (fallbacks doctrinales)](#4-comparaciones-inválidas-sobre-goal-fallbacks-doctrinales)
5. [`UserPatchConst` no cargado](#5-userpatchconst-no-cargado)
6. [Reglas duplicadas / código redundante](#6-reglas-duplicadas--código-redundante)
7. [Reglas sin `disable-self`](#7-reglas-sin-disable-self)
8. [Resumen de reglas de oro para evitar errores](#8-resumen-de-reglas-de-oro-para-evitar-errores)

---

## 1. ERR6002 — Rule too long

### Síntoma
```
ERR6002: Rule too long
```

### Origen
El compilador clásico de `.per` tiene un **límite de elementos por regla**. Cuando una `defrule` acumula demasiadas acciones en el bloque `=>`, el parser falla.

El caso típico fue el bloque **"PERSONALIDAD MILITAR SEMIUTILS EN IMPERIAL"**, que tenía **17 acciones `set-strategic-number`** en una sola regla.

### Código problemático
```perl
(defrule
    (current-age == imperial-age)
=>
    (set-strategic-number sn-number-defend-groups 0)
    (set-strategic-number sn-number-attack-groups 4)
    (set-strategic-number sn-minimum-attack-group-size 8)
    (set-strategic-number sn-maximum-attack-group-size 14)
    (set-strategic-number sn-group-form-distance 110)
    (set-strategic-number sn-scale-minimum-attack-group-size 0)
    (set-strategic-number sn-scale-maximum-attack-group-size 0)
    (set-strategic-number sn-task-ungrouped-soldiers 0)
    (set-strategic-number sn-garrison-rams 1)
    (set-strategic-number sn-enable-patrol-attack 1)
    (set-strategic-number sn-attack-intelligence 0)
    (set-strategic-number sn-special-attack-type1 663)
    (set-strategic-number sn-special-attack-influence1 180)
    (set-strategic-number sn-target-evaluation-distance 55)
    (set-strategic-number sn-target-evaluation-continent 160)
    (set-strategic-number sn-target-evaluation-siege-weapon 20)
    (set-strategic-number sn-target-evaluation-in-progress 20)
)
```

### Solución
**Dividir la regla en varias `defrule` más cortas**, cada una con `disable-self` para que solo se ejecute una vez al entrar en Imperial.

```perl
(defrule
    (current-age == imperial-age)
=>
    (set-strategic-number sn-number-defend-groups 0)
    (set-strategic-number sn-number-attack-groups 4)
    (set-strategic-number sn-minimum-attack-group-size 8)
    (set-strategic-number sn-maximum-attack-group-size 14)
    (set-strategic-number sn-group-form-distance 110)
    (set-strategic-number sn-scale-minimum-attack-group-size 0)
    (disable-self)
)

(defrule
    (current-age == imperial-age)
=>
    (set-strategic-number sn-scale-maximum-attack-group-size 0)
    (set-strategic-number sn-task-ungrouped-soldiers 0)
    (set-strategic-number sn-garrison-rams 1)
    (set-strategic-number sn-enable-patrol-attack 1)
    (set-strategic-number sn-attack-intelligence 0)
    (set-strategic-number sn-special-attack-type1 663)
    (disable-self)
)

(defrule
    (current-age == imperial-age)
=>
    (set-strategic-number sn-special-attack-influence1 180)
    (set-strategic-number sn-target-evaluation-distance 55)
    (set-strategic-number sn-target-evaluation-continent 160)
    (set-strategic-number sn-target-evaluation-siege-weapon 20)
    (set-strategic-number sn-target-evaluation-in-progress 20)
    (disable-self)
)
```

### Regla general
- **Máximo recomendado: 5–7 acciones por regla.**
- Si necesitas más, divide en reglas paralelas con la misma condición.
- Añade `disable-self` si la lógica solo debe ejecutarse una vez.

---

## 2. ERR2005 — Identificadores inválidos en tecnologías

### Síntoma
```
ERR2005: Invalid identifier
```

### Origen
El compilador no reconoce un `research-item` o `unit-type` en las líneas `can-research`, `research`, `can-train`, etc.

---

### 2.1 `ri-my-unique-elite-unit`

#### Código problemático
```perl
(defrule
    (can-research ri-my-unique-elite-unit)
=>
    (research ri-my-unique-elite-unit)
)
```

#### Origen
`ri-my-unique-elite-unit` aparece listado en CPSB, pero **no siempre es aceptado por el compilador** o por `UserPatchConst.per`. El alias correcto es la **system-defined constant**.

#### Solución
Usar las constantes de sistema `my-unique-unit-upgrade` y `my-unique-research`:

```perl
(defrule
    (can-research my-unique-unit-upgrade)
=>
    (research my-unique-unit-upgrade)
)

(defrule
    (can-research my-unique-research)
=>
    (research my-unique-research)
)
```

#### Regla general
Para tecnologías **específicas de civilización**, usar **siempre** las constantes de sistema:
- `my-unique-unit-upgrade` → mejora élite de la UU
- `my-unique-research` → tecnología única del castillo

---

### 2.2 `ri-fire-ship`

#### Código problemático
```perl
(defrule
    (goal gl-water-permit 1)
    (can-research ri-fire-ship)
=>
    (research ri-fire-ship)
)
```

#### Origen
`ri-fire-ship` **no existe** como research item en el CPSB/UserPatch. Lo que existe es la **unidad** `fire-ship-line`, pero el paso Fire Galley → Fire Ship se desbloquea con `ri-war-galley`, no con una tech dedicada.

#### Solución
Reemplazar por `ri-war-galley` (que desbloquea War Galley y también Fire Ship):

```perl
(defrule
    (goal gl-water-permit 1)
    (can-research ri-war-galley)
=>
    (research ri-war-galley)
)
```

---

### 2.3 `ri-demolition-ship` y `ri-elite-cannon-galleon`

#### Código problemático
```perl
(defrule
    (goal gl-water-permit 1)
    (can-research ri-demolition-ship)
=>
    (research ri-demolition-ship)
)

(defrule
    (goal gl-water-permit 1)
    (can-research ri-elite-cannon-galleon)
=>
    (research ri-elite-cannon-galleon)
)
```

#### Origen
Ambos son **unidades navales**, no research items:
- `demolition-ship` → unidad
- `elite-cannon-galleon` → unidad

El CPSB los lista en **dock units**, no en **dock research items**.

#### Solución
Eliminar esas reglas. La línea demo se cubre con `ri-heavy-demolition-ship`, y la línea cannon galleon se cubre con `ri-cannon-galleon`:

```perl
(defrule
    (goal gl-water-permit 1)
    (can-research ri-heavy-demolition-ship)
=>
    (research ri-heavy-demolition-ship)
)

(defrule
    (goal gl-water-permit 1)
    (can-research ri-cannon-galleon)
=>
    (research ri-cannon-galleon)
)
```

#### Regla general
Antes de usar un identificador `ri-*`, verificar en el CPSB si aparece bajo **research items** y no bajo **units**.

---

### 2.4 `scout-type`

#### Código problemático
```perl
(defrule
    (current-age == dark-age)
    (unit-type-count-total scout-type > 0)
=>
    (set-goal gl-intel-state in-ring-scan)
)
```

#### Origen
Doble causa:
1. `scout-type` no está definido como `defconst` de forma general en todos los contextos.
2. El bloque DUC de scouting mezclaba comandos `up-` con constantes de `UserPatchConst` sin garantizar su carga previa.

#### Solución
1. **Definir `scout-type` con un bloque `#load-if-defined`** al inicio del script, cubriendo Aztec/Incan/Mayan.
2. **Eliminar el subbloque DUC de scouting** del bloque 7, dejando solo la transición de estados.

```perl
; SCOUT TYPE GENERICO
#load-if-defined AZTEC-CIV
    (defconst scout-type -267)
#else
    #load-if-defined INCAN-CIV
        (defconst scout-type -267)
    #else
        #load-if-defined MAYAN-CIV
            (defconst scout-type -267)
        #else
            (defconst scout-type -286)
        #end-if
    #end-if
#end-if
```

Y en el bloque 7, la parte de scouting queda como:

```perl
(defrule
    (timer-triggered t-intel)
    (unit-type-count-total scout-type > 0)
    (current-age == dark-age)
=>
    (set-goal gl-intel-state in-ring-scan)
)

(defrule
    (timer-triggered t-intel)
    (unit-type-count-total scout-type > 0)
    (current-age >= feudal-age)
=>
    (set-goal gl-intel-state in-enemy-confirm)
)
```

#### Regla general
- Definir **siempre** `scout-type` con variantes por civilización antes de usarlo.
- No mezclar DUC con transiciones de estado ligeras.

---

## 3. Missing Closing Parenthesis — Comparadores en `goal`

### Síntoma
```
Missing closing parenthesis
```

### Origen
El fact `(goal ...)` **solo compara igualdad**. No acepta `<`, `>`, `>=`, `<=`.

Cuando escribes:
```perl
(goal gl-enemy-water-mass < 3)
```

El parser se descoloca y reporta un error de paréntesis, aunque la sintaxis de paréntesis sea correcta.

### Código problemático
```perl
(defrule
    (timer-triggered t-naval-combat)
    (goal gl-water-permit 1)
    (goal gl-enemy-water-mass < 3)
    (unit-type-count-total galley-line >= 10)
=>
    (set-goal gl-naval-combat-state nc-gain-control)
)
```

### Solución
**Descomponer en reglas separadas por valor posible.**

`< 3` equivale a `0`, `1`, `2`:

```perl
(defrule
    (timer-triggered t-naval-combat)
    (goal gl-water-permit 1)
    (goal gl-enemy-water-mass 0)
    (unit-type-count-total galley-line >= 10)
=>
    (set-goal gl-naval-combat-state nc-gain-control)
)

(defrule
    (timer-triggered t-naval-combat)
    (goal gl-water-permit 1)
    (goal gl-enemy-water-mass 1)
    (unit-type-count-total galley-line >= 10)
=>
    (set-goal gl-naval-combat-state nc-gain-control)
)

(defrule
    (timer-triggered t-naval-combat)
    (goal gl-water-permit 1)
    (goal gl-enemy-water-mass 2)
    (unit-type-count-total galley-line >= 10)
=>
    (set-goal gl-naval-combat-state nc-gain-control)
)
```

### Tabla de equivalencias

| Original | Equivale a |
|---|---|
| `(goal X < 2)` | `0`, `1` |
| `(goal X < 3)` | `0`, `1`, `2` |
| `(goal X > 0)` | todos los valores positivos |
| `(goal X >= 2)` | `2`, `3`, `4`, ... |
| `(goal X <= 1)` | `0`, `1` |

### Regla general
- `goal` **solo acepta igualdad**.
- Si necesitas rangos, usa **múltiples reglas** o **otro fact** si existe.

---

## 4. Comparaciones inválidas sobre `goal` (fallbacks doctrinales)

### Síntoma
Mismos errores que en la sección 3: `Missing closing parenthesis` y `ERR2005`.

### Origen
Intentar validar rangos con `goal`:

```perl
(goal gl-doctrine-land < dl-generic)
(goal gl-doctrine-land > dl-infantry)
(goal gl-doctrine-naval < dn-none)
(goal gl-doctrine-naval > dn-transport-support)
(goal gl-target-class-land < tg-land-none)
(goal gl-target-class-water < tg-water-none)
```

### Código problemático completo
```perl
(defrule
    (timer-triggered t-watchdog)
    (goal gl-doctrine-land < dl-generic)
=>
    (set-goal gl-doctrine-land dl-generic)
)

(defrule
    (timer-triggered t-watchdog)
    (goal gl-doctrine-land > dl-infantry)
=>
    (set-goal gl-doctrine-land dl-generic)
)

(defrule
    (timer-triggered t-watchdog)
    (goal gl-doctrine-naval < dn-none)
=>
    (set-goal gl-doctrine-naval dn-none)
)

(defrule
    (timer-triggered t-watchdog)
    (goal gl-doctrine-naval > dn-transport-support)
=>
    (set-goal gl-doctrine-naval dn-none)
)

(defrule
    (timer-triggered t-watchdog)
    (goal gl-target-class-land < tg-land-none)
=>
    (set-goal gl-target-class-land tg-land-none)
)

(defrule
    (timer-triggered t-watchdog)
    (goal gl-target-class-water < tg-water-none)
=>
    (set-goal gl-target-class-water tg-water-none)
)
```

### Solución
Reemplazar por **fallbacks contextuales** que reimponen valores válidos según la situación real del juego:

```perl
; doctrine fallback si algo raro queda sin definir
(defrule
    (timer-triggered t-watchdog)
    (current-age == dark-age)
=>
    (set-goal gl-doctrine-land dl-generic)
)

(defrule
    (timer-triggered t-watchdog)
    (goal gl-water-permit 0)
=>
    (set-goal gl-doctrine-naval dn-none)
)

(defrule
    (timer-triggered t-watchdog)
    (goal gl-water-permit 1)
    (goal gl-enemy-naval-comp en-unknown)
=>
    (set-goal gl-doctrine-naval dn-galley-control)
)

; target fallback
(defrule
    (timer-triggered t-watchdog)
    (goal gl-target-class-land tg-land-none)
    (current-age >= castle-age)
=>
    (set-goal gl-target-class-land tg-land-production)
)

(defrule
    (timer-triggered t-watchdog)
    (goal gl-target-class-water tg-water-none)
    (goal gl-water-permit 1)
    (players-building-type-count any-enemy dock > 0)
=>
    (set-goal gl-target-class-water tg-water-dock)
)

(defrule
    (timer-triggered t-watchdog)
    (goal gl-target-class-water tg-water-none)
    (goal gl-water-permit 1)
    (players-building-type-count any-enemy dock == 0)
=>
    (set-goal gl-target-class-water tg-water-fleet)
)
```

### Regla general
- **Nunca validar rangos con `goal`.**
- Usar **fallbacks contextuales** basados en:
  - edad actual,
  - `gl-water-permit`,
  - presencia de docks enemigos,
  - composición detectada.

---

## 5. `UserPatchConst` no cargado

### Síntoma
```
ERR2005: Invalid identifier
```

sobre **todos** los comandos `up-` (`up-get-point`, `up-find-local`, `up-target-point`, `up-get-search-state`, etc.).

### Origen
El script usa comandos de UserPatch (`up-`) pero **no carga** `UserPatchConst.per` al inicio. Sin ese archivo, los identificadores como:
- `position-self`
- `position-center`
- `action-move`
- `search-local`
- `find-closest`

quedan **sin definir**.

### Código problemático
```perl
; ==========================================================
; semiUtils.per
; BLOQUE 1/10
; ==========================================================
; (no hay load de UserPatchConst)
```

### Solución
Poner **al inicio absoluto** del script:

```perl
(load "UserPatchConst")
```

**Requisitos:**
- `UserPatchConst.per` debe existir en la carpeta de scripting.
- Debe ir **antes** del primer comando `up-`.
- No basta con declarar un fallback parcial; hay que cargar el archivo completo.

### Alternativa
Si el entorno no encuentra `UserPatchConst.per`, copiar su contenido **dentro** del script, o arreglar la ruta de instalación de UserPatch.

### Regla general
- **Siempre** `(load "UserPatchConst")` arriba del todo.
- No inventar valores manuales para constantes UP.

---

## 6. Reglas duplicadas / código redundante

### Síntoma
No produce error de compilación, pero genera comportamiento errático o desperdicio.

### Origen
En `semiUtils` y `fortyV2` aparecieron bloques repetidos:

```perl
; repetido dos veces
(defrule
    (goal gl-mode m-all-in)
    (current-age >= castle-age)
    (building-type-count-total barracks < 2)
    (can-build barracks)
=>
    (build barracks)
)
```

Y en el bloque naval:

```perl
; ri-war-galley duplicado
(defrule
    (goal gl-water-permit 1)
    (can-research ri-war-galley)
=>
    (research ri-war-galley)
)

; ... y otra vez:
(defrule
    (goal gl-water-permit 1)
    (can-research ri-war-galley)
=>
    (research ri-war-galley)
)
```

### Solución
- **Eliminar duplicados**.
- Revisar con búsqueda de patrones repetidos antes de compilar.

---

## 7. Reglas sin `disable-self`

### Síntoma
No produce error, pero **se ejecuta cada tick**, causando:
- consumo de CPU innecesario,
- reasignación constante de SNs,
- comportamientos oscilantes.

### Origen
Reglas de inicialización o configuración por edad sin `disable-self`:

```perl
(defrule
    (current-age == imperial-age)
=>
    (set-strategic-number sn-number-defend-groups 0)
    (set-strategic-number sn-number-attack-groups 4)
    ; ...
)
```

### Solución
Añadir `(disable-self)` al final del bloque de acciones:

```perl
(defrule
    (current-age == imperial-age)
=>
    (set-strategic-number sn-number-defend-groups 0)
    (set-strategic-number sn-number-attack-groups 4)
    (disable-self)
)
```

### Regla general
- **Toda regla de setup, init o configuración única** debe terminar en `(disable-self)`.
- Solo las reglas de **lógica cíclica** (defensa, producción, timers) se ejecutan continuamente.

---

## 8. Resumen de reglas de oro para evitar errores

| # | Regla | Motivo |
|---|---|---|
| 1 | `(load "UserPatchConst")` al inicio absoluto | Evita ERR2005 en todos los comandos `up-` |
| 2 | Máximo 5–7 acciones por `defrule` | Evita ERR6002 |
| 3 | `disable-self` en reglas de setup | Evita sobrecarga y oscilación |
| 4 | `goal` solo compara igualdad | Nunca usar `<`, `>`, `>=`, `<=` |
| 5 | Para rangos, usar múltiples reglas | 0, 1, 2, ... |
| 6 | Verificar `ri-*` en tabla de research items | Evita ERR2005 |
| 7 | Usar `my-unique-unit-upgrade` / `my-unique-research` | Evita ERR2005 con UUs |
| 8 | Definir `scout-type` por civilización | Evita ERR2005 con scouts |
| 9 | No mezclar DUC con transiciones de estado | Reduce errores y coste |
| 10 | Eliminar reglas duplicadas | Evita comportamiento errático |

---

## Apéndice: Comandos `up-` que requieren `UserPatchConst`

- `up-get-point`
- `up-full-reset-search`
- `up-find-local`
- `up-find-remote`
- `up-find-player`
- `up-get-search-state`
- `up-target-point`
- `up-target-objects`
- `up-set-target-point`
- `up-set-target-object`
- `up-filter-distance`
- `up-modify-sn`
- `up-compare-goal`
- `up-find-player`

Si alguno de estos genera `ERR2005`, es casi seguro que `UserPatchConst` no está cargado.

---

## Apéndice: Identificadores de investigación verificados

### Válidos
- `ri-careening`, `ri-dry-dock`, `ri-shipwright`
- `ri-war-galley`, `ri-galleon`, `ri-fast-fire-ship`
- `ri-heavy-demolition-ship`, `ri-cannon-galleon`
- `ri-ballistics`, `ri-chemistry`, `ri-elite-skirmisher`
- `ri-halberdier`, `ri-light-cavalry`, `ri-hussar`
- `ri-siege-engineers`, `ri-onager`, `ri-siege-onager`
- `my-unique-unit-upgrade`, `my-unique-research`

### Inválidos (unidades, no techs)
- `ri-fire-ship`
- `ri-demolition-ship`
- `ri-elite-cannon-galleon`
- `ri-my-unique-elite-unit` (usar `my-unique-unit-upgrade`)

---

**Última actualización:** durante la depuración de `semiUtils.per` bloques 1–10.  
**Autor:** sesión de depuración asistida.  
**Uso:** referencia técnica para evitar repetir errores en futuras IAs de AoE2 UserPatch 1.5.

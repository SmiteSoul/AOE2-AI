# semiUtils — IA generalista modular (en preparación)

IA generalista para **Age of Empires II: The Conquerors + UserPatch 1.5**, diseñada
para ser adaptativa y robusta. Es el objetivo principal de este repositorio.

## Archivos previstos

| Archivo | Propósito |
|---|---|
| `semiUtils.ai` | Archivo vacío que "engancha" la IA en el juego (mismo nombre que el `.per`). |
| `semiUtils.per` | Archivo principal: constantes globales y `(load ...)` de todos los módulos. |
| `semiUtils-const.per` | `defconst` de goals, timers, techs y parámetros de estrategia. |
| `semiUtils-init.per` | Inicialización: strategic numbers, goals iniciales, detección de civ/mapa. |
| `semiUtils-eco.per` | Economía: reparto de aldeanos, granjas, campamentos, mercado/tributos. |
| `semiUtils-build.per` | Orden de construcción y colocación de edificios. |
| `semiUtils-train.per` | Colas de entrenamiento y mejora de unidades según la composición enemiga. |
| `semiUtils-combat.per` | Ataque/defensa, TSA, control de grupos y micro con DUC (UserPatch). |
| `semiUtils-diplo.per` | Alianzas, chat/taunts, respuesta a mensajes (UserPatch). |

Los módulos concretos pueden variar; la idea es **un módulo por responsabilidad**,
cargado desde `semiUtils.per` con `(load "semiUtils\\<modulo>")`.

## Convenciones de código

- Máx. **16 elementos por `defrule`** (si no, `Rule too long`).
- `(load "..\\UserPatchConst")` (o copia local) **antes** de cualquier comando `up-`.
- El hecho `(goal g v)` **solo compara igualdad**; para rangos usar `up-compare-goal`
  o una regla por valor.
- Todo goal/timer/constante lleva nombre vía `defconst` (prefijos `gl-`, `gt-`, `sn-`).
- Comentarios en español con `;`.

## Referencia útil

- `../reference/UserPatchConst.per` — constantes de UserPatch (obligatorio para `up-`).
- `../reference/CPSB.pdf` — guía oficial de scripting (facts/actions).
- `../reference/ais/` — IAs de terceros para estudio (arquitecturas modulares:
  `the-general/`, `binary/`, `kaia/kaia2/`).

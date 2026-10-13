# 05 — Unificación de forty / fortyV2 (análisis y blueprint histórico)

> **Estado:** este documento conserva la medición y la propuesta previas a la
> implementación. El resultado eligió un monolito autocontenido, no el árbol
> `src/` propuesto abajo. La arquitectura vigente está en [`docs/06`](06_Forty_Feudo.md)
> y la auditoría posterior en [`docs/07`](07_Investigacion_AoC_UP15_y_Auditoria.md#83-forty).

Fecha: 2026-10-12. Alcance histórico: `forty/forty.per` (1.758 líneas), `forty/fortyV2.per`
(6.217 líneas), `semiUtils/semiutils.per` (1.549 líneas) — los tres subidos al
repo. Objetivo declarado por la autora del proyecto:

- **semiUtils** → «crear la IA perfecta mediante **reactividad**».
- **forty** → «una IA capaz de armar de forma organizada y con sentido
  **fortalezas y ciudades o pueblos**».

## 1. Qué es cada fichero (medido, no supuesto)

| | `forty.per` (v1) | `fortyV2.per` | `semiutils.per` |
|---|---|---|---|
| Identidad (cabecera) | «REINO FORTIFICADO — IA defensiva standalone» | «IA GENERALISTA MODULAR» | personalidades + diplo + modos |
| Líneas / reglas | 1.758 / 190 | 6.217 / 606 | 1.549 / ~200 |
| defconst | **6** | **307** | **19** |
| UserPatch | NO (vanilla puro: 10 menciones `up-`) | SÍ (102 usos `up-`, carga `UserPatchConst`) | parcial |
| Estructura | 1 fichero, bloques INIT 1-4 | máquinas de estado (estrategia, eco, infraestructura, combate) + motor DUC + scratch/score | bloques 1/10 + director de modos |
| Señas de identidad | `gl-mode` (m-attack/m-boom/m-defend), `t-director`, `t-pulse`, base compacta, `defend-soldier-count` | doctrinas **`bd-*`** de construcción, `dl-*` doctrina terrestre, `dn-*` naval, `duc-*` focos DUC | `gl-personality` (p-barbaro…p-religioso), `gl-diplo` (d-war/d-allied/d-neutral) |

## 2. Hallazgos clave del análisis

1. **No son dos versiones de la misma IA**: v1 es una IA *vanilla* de reino
   fortificado; V2 es un *framework generalista* con UP. Cero defconst
   compartidos entre V2 y los otros dos.
2. **v1 nació del esqueleto de semiUtils**: sus 6 defconst son exactamente el
   modelo de director de semiUtils (`gl-mode` + modos + `t-director`/`t-pulse`).
   La herencia ya existe de facto.
3. **fortyV2 ya contiene el cerebro de fortalezas que forty necesita**: las
   doctrinas de construcción `bd-*` — `bd-castle-network`, `bd-defense-core`,
   `bd-eco-expand`, `bd-front-creep`, `bd-land-production`, `bd-minimal`,
   `bd-naval-production`, `bd-rebuild` — gestionadas por la máquina de estados
   de infraestructura.
4. **V2 y semiUtils comparten 236 líneas de código idénticas** (concepto de
   bloques 1/10) pero evolucionaron por separado: framework común sin
   modularizar.
5. v1 tiene una virtud que V2 perdió: **funciona sin UserPatch** (vanilla 1.0c).

## 3. Decisión de arquitectura (blueprint)

**forty unificado = núcleo director (semiUtils) + doctrinas de construcción
(fortyV2) + identidad «Reino Fortificado» (v1), sobre UserPatch.**

```
forty/
├── forty.ai                      (entrada)
├── forty.per                     (entry: carga módulos en orden)
└── src/
    ├── UserPatchConst.per        (copia canónica, como siege)
    ├── core.per                  (director: gl-mode, gl-personality,
    │                              t-director/t-pulse — del esqueleto común)
    ├── doctrine.per              (bd-* de fortyV2: castle-network,
    │                              defense-core, eco-expand, front-creep...)
    ├── kingdom.per               (identidad v1: base compacta, plaza,
    │                              muralla perimetral, red de torres)
    ├── eco.per / build.per / train.per / combat.per
    └── scenario.per              (modo escenario: ejército inicial + defensa)
```

**semiUtils** queda como motor independiente de reactividad (personalidades +
diplomacia) y puede **compartir `core.per`** con forty (mismo director).

## 4. Fases de implementación

| Fase | Contenido | Riesgo |
|---|---|---|
| **F1 — Modularizar** | Partir `fortyV2.per` en `src/` (constantes, máquinas de estado, DUC, doctrinas `bd-*`); sin cambiar comportamiento. Parametrizar el lint (`tools/lint_siege.py`) para que audite cualquier carpeta de IA. | bajo |
| **F2 — Personalidad** | Portar el director de v1 + personalidades de semiUtils a `core.per`; los modos `m-attack/m-boom/m-defend` seleccionan doctrinas `bd-*`. | medio |
| **F3 — Reino** | Absorber los INIT 1-4 de v1 (base compacta, defensa) como `kingdom.per`; mapear `bd-castle-network`/`bd-defense-core` al «castillo + murallas + puertas con sentido». | medio |
| **F4 — Escenarios** | Modo escenario (tropas iniciales, defensa de plaza) — mismas lecciones de micro que siege. | bajo |
| **F5 — Vanilla opcional** | Decidir si se conserva un perfil sin UP (v1 intacto como `forty/legacy/`) o se asume UP como línea base. | decisión |

## 5. Qué NO hacer

- No fusionar los 8k de líneas de golpe sin pasar por F1 (sin módulos no hay
  lint ni revisión posible).
- No romper la identidad de v1 (el error clásico: convertir forty en «otra
  generalista» — perdería su razón de ser).
- No copiar identificadores entre los tres ficheros sin verificar resolución
  (misma regla de oro que enseñó `aggressive` en siege).

## 6. Resultado posterior

La implementación unificada se realizó como `forty/forty.per` autocontenido
(1534 líneas y 101 reglas a 2026-10-13 `[REPO]`), manteniendo `fortyV2` en
`legacy/` en vez de ejecutar F1. El blueprint modular queda como alternativa
histórica; no es el siguiente paso vigente. Las correcciones y la prueba pendiente están en
[`docs/07` §§8.3 y 11.2](07_Investigacion_AoC_UP15_y_Auditoria.md).

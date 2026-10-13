# forty — El Reino Fortificado

IA de **fortalezas, ciudades y pueblos con sentido** para Age of Empires II:
The Conquerors + UserPatch 1.5. Objetivo: construir de forma organizada
(plaza, muralla perimetral, red de castillos y torres), sobrevivir, y
contraataque con criterio.

## Estado actual

| Archivo | Qué es | Líneas |
|---|---|---|
| `forty.per` + `forty.ai` | **v1** — «Reino Fortificado», IA defensiva standalone **vanilla** (funciona sin UserPatch). Director de modos (`m-attack/m-boom/m-defend`), INIT 1-4: exploración, economía, base compacta, grupos de defensa. | 1.758 |
| `fortyV2.per` + `fortyV2.ai` | **V2** — framework generalista con UserPatch: máquinas de estado (estrategia, eco, infraestructura, combate), motor DUC y **doctrinas de construcción `bd-*`** (castle-network, defense-core, eco-expand, front-creep…). | 6.217 |

## Unificación en marcha

No son dos versiones de la misma IA: v1 es el *reino* (identidad) y V2 es el
*cerebro* (doctrinas de construcción + estados). El plan para unificarlos con
`semiUtils` (reactividad) está analizado en
[`../docs/05_Unificacion_Forty.md`](../docs/05_Unificacion_Forty.md):
**forty unificado = núcleo director (semiUtils) + doctrinas `bd-*` (fortyV2) +
identidad «Reino Fortificado» (v1)**, modularizado como `siege/` y auditado con
`tools/lint_siege.py`.

## Referencia útil

- `../reference/ais/`: `brutal2/` (arena, murallas), `barbarian-2.18/`
  (defensa reactiva y micro), `the-horde-3.9/` (defensa clásica).
- `../reference/UserPatchConst.per`, `../reference/CPSB.pdf`.
- `../docs/01_Hechos_Del_Motor.md` — hechos 100% confirmados del motor.
- `../Script_Errors.md` — errores reales y su solución.

# 04 — Auditoría multiagente: informe del panel

Fecha: 2026-10-12. Alcance: **todo** el código `.per` de `siege/` (8 ficheros,
108 reglas, 705 constantes en cadena de carga), con el linter como línea base.

## Metodología

Cinco auditorías especializadas independientes (cada una con su mandato, su
checklist y su propio script de análisis), más el linter como control:

| Agente | Mandato | Herramienta |
|---|---|---|
| 1 — Parser/gramática | ERR*, paréntesis, ASCII/BOM, `#load-if`, ERR2012, `load` | script propio |
| 2 — Identificadores | resolución, namespaces, typos por distancia de edición | script propio |
| 3 — Semántica CPSB | dominios de slots (`up-target-objects`, `up-remove-objects`, timers, escrow) | script propio |
| 4 — Lógica runtime | invariantes de timers, reglas contradictorias/muertas, máquinas de estado | script propio |
| 5 — Corpus/pitfalls | UserPatchConst vs canónica, DUC completo, trampas de foros | script propio |

## Resultado del triage

| # | Hallazgo | Veredicto | Acción |
|---|---|---|---|
| A1 | `—` (em-dash) en comentarios de 7 ficheros `.per` | **REAL** (viola ASCII estricto; aokh FAQ: símbolos ocultos = errores irresolubles) | ✅ corregido (`-`) + check ASCII permanente en el linter |
| A2 | 9 tokens «no resolubles» (SNs extendidos, `castle`, `enemy`, `true`) | **FALSO POSITIVO** del agente: son nativos del motor (UP SNs runtime-proven; `castle`/`enemy` builtins; `true` comando) | linter mantiene la clasificación correcta; ver §Aprendizajes |
| A2 | avisos typo distancia-1 (`research-complete`, pares food/wood) | **RUIDO**: `research-complete` es nombre real en UserPatchConst (L111); los pares de SNs son hermanos legítimos | ninguno |
| A3 | 12 errores de slots/timers | **ARTEFACTO del script auditor** (regex capturaba el `)` de cierre: `stance-aggressive)`, `8)`) | regex corregido → 19 checks **LIMPIOS** |
| A4 | `t-push` con enable entre consumidores ×3 | **FALSO POSITIVO semántico**: es un *despachador* de 4 reglas mutuamente excluyentes; todas rearman; el único que hace trabajo (crecer TSA) va primero y nunca pierde el trigger | documentado como patrón válido |
| A4 | «regla de setup sin disable-self» (máquina de estados) | **FALSO POSITIVO**: una salida de máquina de estados debe re-ejecutarse en cada reentrada; `disable-self` la rompería | documentado |
| A5 | posible GROUP-ID con `players-unit-type-count` | **RUIDO** (el regex cazó `sn-group-form-distance`) | ninguno |
| A5 | `UserPatchConst.per` propia == canónica de referencia | ✅ idénticas (md5) | — |

**Bugs reales corregidos**: 1 (em-dashes). **Bug real que faltaba cazar con el
lint**: ninguno (los 2 bugs de runtime anteriores — `loom`, `aggressive` — ya
estaban cubiertos). El código `.per` de siege queda **validado por 6 vías**.

## Aprendizajes permanentes (ya codificados en `tools/lint_siege.py`)

1. **El catálogo de nativos UP está en el bloque comentado** de
   `UserPatchConst.per` (`;(defconst sn-wall-targeting-mode …)`). UP 1.5
   conoce esos nombres en runtime (probado en partida); el linter los lee a
   propósito **sin strip de comentarios** como catálogo de nativos, y con
   strip como `defconst` activos de la cadena. Mecanismo ahora explícito.
2. **Un `defconst` del corpus no prueba que un token no sea nativo** (caso
   `castle 82` de The Horde). Builtins de CPSB + curación explícita mandan.
3. **Nuevo check ERR2012**: mismo nombre con distinto valor en la cadena de
   carga = error (mismo valor: permitido, según CPSB).
4. **Nuevo check ASCII estricto** por fichero `.per`.
5. **Nuevo check de invariantes de timer** (refinado): solo es peligroso un
   consumidor **con trabajo** después de un rearme no-init; los despachadores
   cuya única acción es `enable-timer` están exentos (patrón `t-push`).
6. **Nuevos checks de dominio de slots**: `up-target-objects` (0|1 /
   `action-*` / `formation-*` / `stance-*` o `-1`), `up-remove-objects`
   (`search-*` / `object-data-*` / operador), segundos de timer > 0, cuentas
   de `up-find-*` > 0, escrow 0–100.

## Suite de regresión del linter (7 familias inyectadas → todas cazadas)

| Familia | Inyección | Detectada por |
|---|---|---|
| 1 | `(research loom)` | namespace `ri-*` + resolución |
| 2 | `(buy-commodity gold)` | dominio de commodities |
| 3 | `aggressive` sin defconst | regla de resolución (alias local) |
| 4 | `batering-ram-line` | posición de corpus + resolución |
| 5 | em-dash en comentario | check ASCII |
| 6 | consumidor de `t-eco` con trabajo tras el rearme | invariante de timers |
| 7 | `(defconst ram-full 5)` duplicado de `ram-full 4` | ERR2012 |

## Patrones validados por el panel (no son bugs)

- **Despachador de timer** (`t-push`): N reglas `(timer-triggered t)` con
  condiciones mutuamente excluyentes, cada una con `(enable-timer t 8)` como
  única acción. Cobertura completa del espacio de estados; seguro bajo
  cualquier semántica de trigger.
- **Salidas de máquina de estados sin `disable-self`**: correcto por diseño
  (deben refrescarse en cada pase/reentrada).
- **DUC con `up-target-objects 0`** + listas `up-find-*` + guards de stance:
  3 resets, 7 finds, 3 targets, 0 targets opcionales — estructura completa.

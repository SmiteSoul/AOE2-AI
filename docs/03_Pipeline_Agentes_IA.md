# 03 — Pipeline de implementación para agentes de IA

Cómo debe trabajar un agente (o un humano) en este repo. Cada fase tiene su
criterio de salida; **no se salta ninguna**.

## Pipeline (7 fases)

### F0 — Investigar (antes de tocar código)
- Leer: [`01_Hechos_Del_Motor.md`](01_Hechos_Del_Motor.md),
  [`02_Prevencion_Errores.md`](02_Prevencion_Errores.md),
  [`../Script_Errors.md`](../Script_Errors.md), CPSB (`reference/CPSB.pdf`) y
  [`../reference/ais/README.md`](../reference/ais/README.md).
- Para cada hecho que vayas a usar: etiquetar procedencia
  (CPSB/RUNTIME/CORPUS/FORO). Si no hay etiqueta posible, **no se usa**.
- **Salida**: lista de requisitos + hechos confirmados que aplican.

### F1 — Diseñar
- Máquina de estados con `goals` (prefijo `gl-`), timers (prefijo `t-`),
  constantes nombradas; tabla de SNs por fase.
- Decidir el orden de carga (define el orden global de reglas).
- **Salida**: esquema de goals/timers/módulos, sin código aún.

### F2 — Escribir (módulo a módulo)
- Orden recomendado: `const` → `init` → `eco` → `build` → `train` → `combat`.
- Vanilla `defrule` (nada de macros binarias), ASCII estricto, ≤ 15 elementos
  por regla, `disable-self` en setups, rearmes de timer al final del entry.
- **Cada token nuevo**: o es numérico, o está en la cadena de carga, o es
  builtin del CPSB. Nada de «en Barbarian lo vi».

### F3 — Lint (obligatorio y automatizado)
```bash
python3 tools/lint_siege.py
```
Cubre: resolución de identificadores, aridad, posiciones de comando, dominios
cerrados (commodities, `ri-*`), 16 elementos, paréntesis, `goal` solo
igualdad, `defconst`/timers usados sin definir, `load` inexistentes.

### F4 — Regresión del validador
Tras cualquier cambio del linter, re-inyectar bugs conocidos en copias
temporales y confirmar que los caza (familia `loom`, `gold`, `aggressive`,
typos). Un linter no probado no es una garantía.

### F5 — Test en juego incremental
- Instalar en `AI/` del juego (ver `siege/README.md`).
- El parser reporta el **primer** error con fichero+línea; arreglar, re-lint,
  repetir.
- Aprovechar el orden de carga: si falla `combat.per:103`, todo lo anterior
  (`UserPatchConst`, `const`, `init`, `eco`, `build`, `train`) quedó
  **probado en runtime**. Llevar la lista de módulos probados.

### F6 — Registrar
- Todo error nuevo → [`../Script_Errors.md`](../Script_Errors.md)
  (síntoma, origen técnico, solución).
- Todo hecho nuevo confirmado → [`01_Hechos_Del_Motor.md`](01_Hechos_Del_Motor.md)
  con su etiqueta.

### F7 — Iterar
- Afinar números (umbrales, techos) solo con código que pasa lint + runtime.

## Skills del agente que importan aquí

| Skill | Para qué | Ejemplo en este repo |
|---|---|---|
| **Validación posicional** | Un argumento solo es válido en su posición de comando | cazar `(research loom)` |
| **Regla de resolución** | Todo token debe resolver en la cadena de carga | cazar `aggressive` |
| **Minería de corpus** | Extraer usos reales de IAs de primer nivel | dominio de commodities, aridades |
| **Disciplina de procedencia** | Etiquetar CPSB/RUNTIME/CORPUS/FORO | `docs/01` |
| **Forensia de runtime** | fichero+línea del error → causa raíz + alcance probado | módulos ya validados al vuelo |
| **Regresión del validador** | El linter se prueba con bugs inyectados | test `loom/gold/aggressive/typo` |
| **Extracción del CPSB** | `pypdf` sobre `reference/CPSB.pdf` a texto para greps | verificación `ri-*`, citas ERR2012 |
| **Investigación web triageada** | Foros/Steam/changelogs como evidencia etiquetada | casos GIANT-MAP, rushprep-cost |
| **Higiene git** | Commits atómicos por problema, ASCII, sin artefactos | historial de `arena/...` |

## Herramientas

- **`tools/lint_siege.py`** (este repo): el linter principal.
- **Extensión VS Code «AoE II AI Tools»** (KnightThyme): linter con los
  códigos ERR* del juego, contador de reglas, signatures. Complemento válido
  para quien edite en VS Code **[FORO: Marketplace]**.
- **`reference/CPSB.pdf`** + `reference/UserPatchConst.per` + corpus
  `reference/ais/`**: la triple fuente de verdad.
- **UserPatch 1.5** en el juego de destino (1.0c + UP).

## Anti-patrones (prohibidos)

1. Escribir un identificador porque «existía en otra IA» sin definirlo.
2. Comparar `(goal ...)` con `<`, `>`, `>=`, `<=`.
3. Macros binarias (estilo `#define`) en las IAs de este repo.
4. Reglas > 16 elementos (o > 15 sin razón).
5. Rearmar timers antes de sus consumidores.
6. Ficheros con acentos/símbolos no ASCII.
7. Dar por bueno un SN sin verificar su comportamiento (hay SNs documentados
   que no funcionan **[FORO]**).

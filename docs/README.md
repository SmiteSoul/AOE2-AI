# Documentación técnica — IA scripting para AoE2 (UserPatch 1.5)

Documentación quirúrgica del proyecto: qué está **100% confirmado** del motor,
cómo prevenir errores **antes** de que ocurran, cómo deben trabajar los agentes
de IA en este código, y cómo están construidas las IAs de referencia.

| Documento | Qué contiene | Cuándo usarlo |
|---|---|---|
| [`01_Hechos_Del_Motor.md`](01_Hechos_Del_Motor.md) | Base de hechos del motor con **etiqueta de procedencia** (CPSB / RUNTIME / CORPUS / FORO). | Antes de escribir cualquier código: no afirmar nada que no esté aquí o en el CPSB. |
| [`02_Prevencion_Errores.md`](02_Prevencion_Errores.md) | Taxonomía completa de errores (ERR*), detección **antes de ejecutar** y casos reales. | Antes de cada test en partida y al depurar. |
| [`03_Pipeline_Agentes_IA.md`](03_Pipeline_Agentes_IA.md) | Pipeline de implementación paso a paso + skills/herramientas del agente. | Siempre que se cree o modifique una IA. |
| [`referencia/`](referencia/README.md) | Arquitectura de Barbarian, The General, The Horde y Kaia: cómo se construyen y conectan. | Al diseñar módulos nuevos o investigar patrones. |

Documentos relacionados en la raíz:

- [`../Script_Errors.md`](../Script_Errors.md) — registro histórico de errores
  reales (forty/fortyV2/semiUtils/siege) con síntoma, origen y solución.
- [`../tools/lint_siege.py`](../tools/lint_siege.py) — linter que automatiza las
  comprobaciones de este manual.
- [`../siege/README.md`](../siege/README.md) — la IA siege y sus invariantes.

## Niveles de prueba usados en estos documentos

- **[CPSB]** — escrito en el manual oficial (Computer Player Strategy Builder).
- **[RUNTIME]** — ejecutado en el juego real (AoC 1.0c + UserPatch 1.5) sin error.
- **[CORPUS]** — presente en el código vivo de IAs de primer nivel de
  `reference/ais/` (Barbarian, The General, The Horde, ...).
- **[FORO]** — reportado en foros de la comunidad (aiscripters, aokh, Steam,
  Reddit) o changelogs oficiales de UserPatch; con fuente.
- **[FOLKLORE]** — creencia extendida sin prueba directa; **no usar como base**.

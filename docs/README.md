# Documentación técnica — IA scripting para AoE2 (UserPatch 1.5)

Documentación técnica del proyecto: qué está respaldado por CPSB, runtime,
corpus o comunidad; cómo prevenir errores **antes** de que ocurran; cómo deben
trabajar los agentes de IA; y cómo están construidas las IAs de referencia.

> **Protocolo vinculante del agente:** [`../agent.md`](../agent.md) —
> nada se salta; todo se documenta, se revisa y se evalúa; lo que no se
> sabe se investiga (foros/fuentes) o se pregunta.

| Documento | Qué contiene | Cuándo usarlo |
|---|---|---|
| [`01_Hechos_Del_Motor.md`](01_Hechos_Del_Motor.md) | Base de hechos del motor con **etiqueta de procedencia** (CPSB / RUNTIME / CORPUS / FORO). | Antes de escribir código; contrastar además el catálogo UP/AIREf cuando el comando no sea vanilla. |
| [`02_Prevencion_Errores.md`](02_Prevencion_Errores.md) | Taxonomía completa de errores (ERR*), detección **antes de ejecutar** y casos reales. | Antes de cada test en partida y al depurar. |
| [`03_Pipeline_Agentes_IA.md`](03_Pipeline_Agentes_IA.md) | Pipeline de implementación paso a paso + skills/herramientas del agente. | Siempre que se cree o modifique una IA. |
| [`04_Auditoria_Multiagente.md`](04_Auditoria_Multiagente.md) | Informe del panel de auditoría multiagente (5 agentes especializados, triage y patrones validados). | Tras cada auditoría completa o cambio grande. |
| [`05_Unificacion_Forty.md`](05_Unificacion_Forty.md) | Análisis histórico de forty/fortyV2/semiUtils y blueprint previo a la implementación. | Para rastrear decisiones; usar 06/07 para el estado vigente. |
| [`06_Forty_Feudo.md`](06_Forty_Feudo.md) | Diseño de la ciudad-fortaleza medieval (feudo → muralla → plaza fuerte) y su traducción a `.per`; investigación histórica + estructura del `forty.per` unificado. | Para entender o extender la IA forty. |
| [`07_Investigacion_AoC_UP15_y_Auditoria.md`](07_Investigacion_AoC_UP15_y_Auditoria.md) | Investigación integral de AoC 1.0c + UP 1.5: modelo del motor, goals/timers/SNs, DUC/TSA, herramientas web, radiografía y correcciones de los tres proyectos. | Fuente de contexto completa y plan de validación runtime. |
| [`referencia/`](referencia/README.md) | Arquitectura de Barbarian, The General, The Horde y Kaia: cómo se construyen y conectan. | Al diseñar módulos nuevos o investigar patrones. |

Documentos relacionados en la raíz:

- [`../Script_Errors.md`](../Script_Errors.md) — registro histórico de errores
  reales (forty/fortyV2/semiUtils/siege) con síntoma, origen y solución.
- [`../tools/lint_siege.py`](../tools/lint_siege.py) — linter de `siege`,
  `forty` y `semiUtils` que automatiza las comprobaciones de este manual.
- [`../tools/test_lint_siege.py`](../tools/test_lint_siege.py) — regresiones
  ejecutables del linter.
- [`../siege/README.md`](../siege/README.md) — la IA siege y sus invariantes.

## Niveles de prueba usados en estos documentos

- **[CPSB]** — escrito en el manual oficial (Computer Player Strategy Builder).
- **[RUNTIME]** — ejecutado en el juego real (AoC 1.0c + UserPatch 1.5) sin error.
- **[CORPUS]** — presente en el código vivo de IAs de primer nivel de
  `reference/ais/` (Barbarian, The General, The Horde, ...).
- **[FORO]** — reportado en foros de la comunidad (aiscripters, aokh, Steam,
  Reddit) o changelogs oficiales de UserPatch; con fuente.
- **[FOLKLORE]** — creencia extendida sin prueba directa; **no usar como base**.

# IAs de referencia — cómo están construidas

Análisis de las IAs de `reference/ais/` con dos objetivos: entender **cómo se
conecta todo** en un script de nivel mundial, y separar lo **verificado** de lo
supuesto. Todas las métricas están medidas sobre este repo (oct 2026).

## Métricas comparadas

| IA | .per | Líneas | Reglas | defconst | `load` | usos `up-` | Estilo |
|---|---|---|---|---|---|---|---|
| **Barbarian 2.18** | 97 | 126.476 | 8.819 | 7.478 | 118 | 28.601 | modular + estrategias |
| **The General 1.3** | 41 | 118.634 | 7.915 | 10.643 | 324 | 40.285 | micro-librería de funciones |
| **The Horde 3.9** | 1 | 34.466 | 2.297 | 2.052 | 0 | 3.199 | monolito autocontenido |
| **Promi** | 18 | 48.542 | 3.715 | 3.173 | 17 | 10.362 | modular |
| **Brutal2** | 38 | 26.683 | 2.634 | 684 | 21 | 3.909 | modular |
| **Training** | 8 | 12.200 | 1.030 | 159 | 4 | 16 | didáctico |
| **Binary** | 34 | 5.586 | 28 | 962 | 19 | 684 | librería de datos/hechos |
| **kaia** | 18 | 1.915 | 181 | 66 | 12 | 10 | ligero, educativo |
| **Crusher** | 12 | 1.627 | 74 | 766 | 8 | 153 | experimental |

Lecturas **[CORPUS]**: (1) los pesos pesados viven de `up-` (28–40k usos):
sin UserPatch no hay nivel top; (2) el ratio defconst/líneas (~6–8%) muestra
que todo se nombra con constantes; (3) modularizar es la norma (salvo The
Horde), con `load` en cascada; (4) The General es un caso extremo: 324 `load`
organizados como funciones reutilizables.

## Guías individuales

- [`barbarian.md`](barbarian.md) — el número 1: estrategias, foco enemigo DUC,
  g: facts.
- [`the-general.md`](the-general.md) — arquitectura de funciones, DUC,
  `up-get-search-state`.
- [`the-horde.md`](the-horde.md) — el monolito: cómo sobrevive sin `load`.
- [`kaia.md`](kaia.md) — la más legible: ideal como plantilla de aprendizaje.

## Cómo usar este material (disciplina)

1. **Un patrón del corpus no es un identificador válido.** Ver
   [`../01_Hechos_Del_Motor.md`](../01_Hechos_Del_Motor.md) §1 (caso `aggressive`).
2. Para copiar un patrón: reproducir su **estructura completa** (p. ej. el
   encadenado DUC incluye `up-full-reset-search` previo, etc.) — copiar a
   medias da silencio, no error.
3. Verificar cada token contra CPSB/UserPatchConst antes de pegarlo.

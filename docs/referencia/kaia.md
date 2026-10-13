# kaia — la referencia didáctica

**Ubicación**: `reference/ais/kaia/` (18 ficheros; `Kaia.per`, `kaia-old/`,
`kaia2/`). **Perfil**: 1.915 líneas, 181 reglas, 66 defconst — la más pequeña y
legible del corpus de primer nivel. Ideal para aprender y plantillar.

## Cómo se construye

- **[CORPUS]** Tres generaciones del mismo proyecto coexisten:
  - `Kaia.per` — entry;
  - `kaia-old/` — versión por módulos clásica (`Kaia-init.per`,
    `Kaia-economy.per`, `Kaia-build.per`, `Kaia-training.per`,
    `Kaia-research.per`, `Kaia-military.per`, `Kaia-market.per`,
    `Kaia-strategy.per`, `Kaia-resign.per`, `Kaia-debug.per`);
  - `kaia2/` — reestructuración limpia: `main/init.per` +
    `shared/constants.per` + `build/`, `research/`, etc. (en construcción).
- **[CORPUS]** Separa explícitamente `shared/constants.per` — el reconocimiento
  de que las constantes son un módulo compartido, no un estorbo.

## Cómo se conecta todo

- Entry `Kaia.per` → `load` de módulos en orden (init → eco → build → …);
  cada módulo es autosuficiente salvo las constantes compartidas.
- Módulo `debug` dedicado: tener un `Kaia-debug.per` es una técnica en sí
  (chat-to-all/`chat-local` de estado, impresión de goals).

## Técnicas que merecen copiarse

1. **Plantilla de módulos** de kaia-old: es la arquitectura que usa siege
   (`const/init/eco/build/train/combat`) con otro nombre.
2. `shared/constants.per` como único punto de verdad de constantes.
3. Módulo de debug separado que se puede silenciar de una pieza.
4. `Kaia-resign.per` como módulo: las reglas de rendición/condiciones de
   fin de juego en su propio sitio.

## Lo que NO copiar

- Poco que decir: su escala evita casi todos los antipatrones. Solo vigilar
  que `kaia2/` (versión en desarrollo) no se tome como referencia de
  completitud.

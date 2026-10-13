# The General 1.3 — la micro-librería de funciones

**Ubicación**: `reference/ais/the-general/` (41 ficheros; wrapper
`The Captain.per` / `The Conscript.per` sobre la carpeta `The General 1.3/`).
**Perfil**: 118k líneas, 7.915 reglas, 10.643 defconst, **324 `load`**, 40k usos
`up-` — la arquitectura más «de ingeniería» del corpus.

## Cómo se construye

- **[CORPUS]** Estructura de funciones reutilizables: `Functions/` contiene
  mini-ficheros con comportamientos cerrados (`Build Line Lumber.per`,
  `Reset DUC.per`, `Store Local List.per`…). Los módulos de negocio
  (`Attacking.per`, `Army Control.per`, `Gathering.per`, `Market Trading.per`,
  `Resign.per`, `Tribute.per`) los componen.
- **[CORPUS]** Catálogos de constantes separados y **por civilización**:
  `Civ Tech Tree Constants.per`, `Civ Unique Constants.per` — la lección de
  `scout-type`/UU se resuelve aquí con catálogos, no con trucos.
- `UserPatchConst.per` propio incluido en su árbol.

## Cómo se conecta todo

- **[CORPUS]** DUC.per centraliza el control directo:
  `up-get-search-state g-local-total` escribe los goals extendidos 309–312
  (local/remoto totales y «last», definidos en `Initialization.per:2061-2064`),
  `up-set-target-object` + `up-target-objects` option 1 exige target previo, y
  el garrison usa `action-garrison`.
- **[CORPUS]** `Escrow.per` dedicado: el escrow (`set-escrow-percentage`,
  `release-escrow`) se trata como subsistema propio, no disperso.

## Técnicas que merecen copiarse

1. **Funciones como ficheros**: un comportamiento = un `load` reutilizable.
2. **Catálogos por civ** en vez de condicionales sueltos.
3. **El estado de búsqueda DUC como contrato**: `up-get-search-state` guarda
   contadores en goals tras cada manipulación de listas (patrón que usa siege).
4. Wrapper de entrada fino (`.ai`/`.per` pequeños que cargan el cuerpo).

## Lo que NO copiar

- `up-target-objects 1` sin `up-set-target-object` previo (silencio).
- Su densidad de `defconst` (10k) sin organización: aquí hay catálogos; en un
  script pequeño sería ruido.

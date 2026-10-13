# The Horde 3.9 — el monolito de Archon

**Ubicación**: `reference/ais/the-horde-3.9/The Horde.per` (¡un solo fichero!).
**Perfil**: 34.466 líneas, 2.297 reglas, 2.052 defconst, **0 `load`**, 3.199
usos `up-`. UP 1.4 / AoFE según su cabecera.

## Cómo se construye

- **[CORPUS]** Todo en un fichero autocontenido: cabecera de ajustes preferidos
  (mapas que NO juega: «no juega mapas que requieren transporte de aldeanos»,
  Michi detectado vía `ai_info_map_type`…), después constantes, después
  bloques temáticos separados por comentarios.
- **[CORPUS]** Define sus propios alias de stance: `(defconst aggressive 0)`,
  `(defconst stand-ground 2)`, `(defconst no-attack 3)` (L334-337) — con el
  comentario `; Define AttackStance Constants`.
- **[CORPUS]** **Redefine constantes nativas redundantes**: `(defconst castle 82)`
  (L170) siendo `castle` builtin del motor — legal con el mismo valor, pero
  engaña a cualquier análisis superficial (el linter de siege lo tuvo que
  tratar como excepción).

## Cómo se conecta todo

- Sin `load`: la conexión es por **orden de secciones dentro del fichero** y
  por una rejilla densa de goals (`defconst` + goals compartidos entre bloques).
- **[CORPUS]** Usa `up-get-search-state`, `up-find-*`, DUC de garrison y
  `sn-garrison-rams`; planificación naval con goals de composición enemiga.

## Técnicas que merecen copiarse

1. **Cabecera de condiciones de juego**: declarar qué mapas/modos la IA no
  soporta (documenta límites operativos reales).
2. **Agrupación temática con comentarios** — legibilidad sin ficheros.
3. Definir explícitamente cualquier alias que se use (buenas prácticas
   suyas… siempre que se copie el `defconst` con el alias).

## Lo que NO copiar

- El formato monolito para proyectos grandes: 34k líneas sin `load` son
  inviables de auditar (a nosotros nos costó localizar patrones).
- Sus alias sin contexto: `castle 82`, `aggressive 0` son **suyos**.

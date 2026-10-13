# Barbarian 2.18 — el asediador del ecosistema competitivo

**Ubicación**: `reference/ais/barbarian-2.18/` (97 ficheros .per).
**Perfil**: la IA más fuerte del circuito UP (scripter16). 126k líneas, 8.819
reglas, 28.6k usos `up-`.

## Cómo se construye

- **Estrategias como constantes de alto nivel**: `defconst aggressive-strategy
  xbow-rush` / `knight-rush` / `castle-push` / `scorpion-rush`… Un goal global
  apunta a la estrategia activa y el resto de módulos se condiciona a ella.
  **[CORPUS]**
- **Alias locales propios**: `(defconst aggressive 0)`, `(defconst stand-ground 2)`,
  `(defconst no-attack 3)` (Barbarian.per:1184-1187) para stances — cada IA
  nombra lo suyo; NO copiar sin definir **[CORPUS]** (origen del bug siege
  `combat.per:103`).
- **Prefijos de namespaces**: `gl-strategy-*`, `gl-tim-*`, grupos numéricos
  documentados con comentarios inline.

## Cómo se conecta todo

- **[CORPUS]** El entry carga módulos con `load` (118 cargas) por fases.
- **Foco enemigo DUC** (patrón verificado L8721):
  `(up-get-player-fact this-any-enemy player-number 0 <goal>)` →
  `(up-modify-sn sn-focus-player-number g:= <goal>)` → `up-find-remote` →
  `(stance-toward focus-player enemy)` como guardia.
- **[CORPUS]** Operadores `g:` en hechos planos: `game-time g:< goal`,
  `strategic-number g:== goal`, `cc-players-unit-type-count g:< goal`.
- **[CORPUS]** Murallas/stance DUC (L9465-9485): `wall-class` con
  `up-find-*`, formaciones (`formation-stagger` L49219), conteos
  `monastery-class` en `unit-type-count-total` (L29636).

## Técnicas que merecen copiarse (estructura, no identificadores)

1. Máquina de estrategias arriba, ejecutores abajo (separación configuración/
   comportamiento).
2. Encadenado DUC completo con guardias de stance y reset de búsqueda.
3. Goals como memoria persistente documentada (`defconst` 418 = nivel de
   agresividad…).

## Lo que NO copiar

- Sus alias (`aggressive`, `stand-ground`, `no-attack`) **sin** los `defconst`
  correspondientes → ERR2005.
- Su volumen: 8.800 reglas incluyen toneladas de micro por civilización que
  una IA nueva no necesita.

# 02 — Prevención de errores: detectarlos ANTES de que ocurran

Compañero de [`../Script_Errors.md`](../Script_Errors.md) (que registra los
errores **reales** ya sufridos). Aquí: la taxonomía completa, cómo cazar cada
clase **sin ejecutar el juego**, y los casos de foro que enseñan las trampas
menos obvias.

## 1. Taxonomía de errores del parser

| Código | Mensaje | Causa | ¿Se detecta sin juego? |
|---|---|---|---|
| ERR2001 | Missing opening parenthesis | `( =` faltante | ✅ balance de paréntesis |
| ERR2002 | Missing keyword | Faltan parámetros o el nombre del hecho/acción | ✅ aridad por comando |
| ERR2004/2005 | Invalid / Missing identifier | Token que **no resuelve** (alias ajeno, typo, constante de otra versión) | ✅ **regla de resolución** del linter |
| ERR2008 | Missing arrow | `defrule` sin `=>` | ✅ |
| ERR2011 | Missing closing parenthesis | `) =` faltante (¡y también lo dispara comparar `goal` con `<`/`>`) | ✅ balance + chequeo de `goal` |
| ERR2012 | Constant already defined | `defconst X` con **distinto** valor repetido (mismo valor: OK) | ✅ colisiones de `defconst` |
| ERR5001 | File open failed | `(load ...)` que no resuelve a fichero real | ✅ comprobando rutas |
| ERR6002 | Rule too long | > 16 elementos por regla | ✅ recuento de elementos |
| ERR8001 | No rules | El script expandido no contiene ningún `defrule` | ✅ |

Fuentes: CPSB; extensión «AoE II AI Tools» (VS Marketplace) que replica estos
códigos; hilos de Steam/foros.ageofempires.com **[FORO]**.

## 2. Checklist pre-vuelo (obligatoria antes de cada test en partida)

1. `python3 tools/lint_siege.py . <siege|forty|semiUtils>` → debe decir
   `OK sin errores`; ejecutar también los otros dos proyectos y
   `python3 -m unittest -v tools.test_lint_siege`.
2. Todo token identificado resuelve: numérico / `defconst` de la cadena de
   carga / builtin del motor (ver [`01_Hechos_Del_Motor.md`](01_Hechos_Del_Motor.md) §1).
3. Ningún alias copiado del corpus sin definir (`aggressive`, `stand-ground`…).
4. Ningún identificador de **otra versión del juego** (ver caso GIANT-MAP).
5. Ficheros ASCII puros; `.ai` + `.per` con el mismo nombre; `load` correctos.
6. Reglas de setup con `(disable-self)`; rearmes de timer **al final**.
7. Reglas ≤ 15 elementos.

## 3. Casos reales que fijan las reglas

### 3.1 `aggressive` (siege — ERR2005 en `combat.per:103`) **[RUNTIME]**
Copiamos `(up-target-objects 0 action-default -1 aggressive)` del corpus, donde
funciona porque **Barbarian define** `(defconst aggressive 0)` y The Horde
`(defconst aggressive 0)`. Sin ese `defconst`, ERR2005. Solución:
`stance-aggressive`, constante nativa de `UserPatchConst.per`. Lección: el
corpus prueba *usos*, no *existencia universal*.

### 3.2 `loom` (siege — ERR2005 en `eco.per:12`) **[RUNTIME]**
`(research loom)` → el identificador de tech es `ri-loom`. Lección: namespace
`ri-*` obligatorio en research (salvo nombres de edad).

### 3.3 `buy-commodity gold` (siege — cazado antes de volar) **[CORPUS]**
El oro es la moneda; commodities = food/wood/stone. Lección: los nombres de
parámetro tienen **dominios cerrados**.

### 3.4 Constantes de otra versión del juego **[FORO: Steam/forums.ageofempires.com]**
Updates de AoE2DE rompieron IAs oficiales: `GIANT-MAP` → `HUGE-MAP` (renombraron
el tamaño de mapa sin actualizar el AI), `sn-preferred-trade-distance` con un
identificador muerto en `ai (HD version).per2:4466`, `elite wonder rush.per2`
con comparadores a constantes inexistentes, `rushprep-cost` y afines perdidos en
`Promisory/Buildings.per` (arreglado sustituyéndolos por los valores numéricos
de `customConstants.per`). Lección: los identificadores están **acoplados a la
versión de datos**; tras un update del juego, revalidar TODO.

### 3.5 Colisión de constantes entre módulos **[FORO: Steam]**
`goal end-age feudal` con `(defconst feudal 1)` en un módulo y otro `feudal`
distinto en otro fichero cargado → error de identificador en cascada. Solución
aplicada por la comunidad: prefijar (`end-feudal`, `end-castle`).

### 3.6 Caracteres invisibles **[FORO: aokh FAQ]**
Un editor que guarde UTF-8/BOM produce «un error in-game que no puedes
solucionar» porque el parser bebe del byte crudo. Solución: ASCII estricto.

### 3.7 `Missing closing parenthesis` por comparar `goal` **[registro propio]**
`(goal X < 3)` no es un error de paréntesis: el parser se descoloca porque
`goal` solo admite igualdad. Ver `Script_Errors.md` §3–4.

### 3.8 ERR5001 en cargas **[FORO: BruteForce]**
`file brutal / userpatch.per ERR5001: file open failed` — rutas de `load` con
barras incorrectas o fichero movido.

## 4. Errores que el juego NO detecta (lógica, no sintaxis)

- Reglas de setup sin `disable-self` → se reejecutan cada tick, SNs oscilan.
- Reglas duplicadas → comportamiento errático.
- DUC mal encadenado (falta `up-set-target-object` antes de
  `up-target-objects 1`) → silencio, no error.
- Rearmar un timer antes de todos sus consumidores → el nuevo `enable-timer`
  limpia `triggered` y las reglas posteriores pierden ese pulso.
- `players-unit-type-count` sobre GROUP-IDs que solo ve `cc-` **[FORO]**.

Para esta clase: revisión de código + tests de comportamiento; el linter marca
los patrones peligrosos conocidos.

## 5. Flujo de depuración cuando el juego reporta error

1. Anotar **fichero + línea + código** exactos (el diálogo da los tres).
2. Si es ERR2005: buscar el token exacto en esa línea → ¿está en la cadena de
   carga? ¿es alias de otra IA? ¿es de otra versión del juego?
3. Corregir + `python3 tools/lint_siege.py . <proyecto>` y ejecutar la
   regresión de los otros proyectos.
4. Registrar el caso en [`../Script_Errors.md`](../Script_Errors.md) con
   síntoma/origen/solución (disciplina del repo).
5. Volver a probar: el parser se detiene en el **primer** error; puede haber
   más detrás (los hilos de Steam documentan ir línea a línea).

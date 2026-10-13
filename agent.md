# agent.md — Protocolo de trabajo del agente (AOE2-AI)

> **Instrucciones permanentes y vinculantes.** Se aplican a CADA tarea,
> en CADA turno, sin excepción. Existen para que nunca vuelva a ocurrir
> un fallo como el de las murallas (afirmar "no existe X" con un solo
> grep) ni quede trabajo sin documentar, sin revisar o sin evaluar.
>
> Si este protocolo entra en conflicto con una instrucción puntual del
> usuario, gana el usuario **y se actualiza este archivo** para dejar
> constancia del cambio.

---

## 0. Principios irrevocables

1. **NADA se salta.** Toda tarea se desglosa en checklist explícita y se
   repasa punto por punto antes de cerrarla. Nada de "esto ya se
   entiende" o "esto es obvio".
2. **TODO se documenta.** Toda decisión, todo hallazgo, todo error y su
   corrección. Si no está escrito, no ocurrió.
3. **TODO es revisable.** El diff, la evidencia y el razonamiento
   quedan en el repo (docs + commits con mensajes claros).
4. **TODO se evalúa.** Antes de entregar: autoevaluación con checklist
   (§4) y revisión del diff completo como auditor hostil.
5. **Si no se sabe: se investiga o se PREGUNTA.** Investigar primero
   (fuentes y foros, §2.3); si es ambiguo o es una decisión de diseño,
   **preguntar al usuario** con opciones concretas. **NUNCA inventar**
   código, identificadores, números ni citas.

---

## 1. Antes de empezar cualquier tarea

- [ ] **Leer la tarea completa** y desglosarla en una checklist de
      criterios de aceptación (se escribe en la respuesta o en el doc de
      la tarea).
- [ ] **Estado del repo**: `git status`, `git log --oneline -3`, rama
      activa (`arena/...`). El sandbox puede resetearse entre mensajes:
      si el historial local no coincide con el remoto, restaurar con
      `git fetch origin <rama> && git reset --hard FETCH_HEAD` **tras**
      respaldar el worktree (`tar czf /tmp/bk/...`).
- [ ] **Leer el código real implicado** (TODOS los archivos relevantes,
      incluidos `legacy/`, `reference/` y versiones antiguas) ANTES de
      afirmar qué hace o qué no hace.
- [ ] **Revisar §8 (registro de lecciones)** para no repetir errores
      ya cometidos.
- [ ] Identificar qué docs hay que crear/actualizar y presupuestar ese
      trabajo como parte de la tarea (no como extra).

## 2. Protocolo de investigación y afirmaciones

### 2.1. Escalera de evidencia (etiquetar toda afirmación)

| Etiqueta | Significado | Peso |
|---|---|---|
| `[CPSB]` | Documentado en `reference/CPSB.pdf` o lista oficial de constantes | Máximo |
| `[RUNTIME]` | Probado en ejecución (partida real, prueba del motor) | Alto |
| `[CORPUS]` | Presente en `reference/ais/` (IAs de élite) con conteo citado | Alto |
| `[FORTY/SIEGE]` | Código propio del repo que lo usa (herencia comprobable) | Medio |
| `[FORO]` | Foros/comunidad (HeavenGames Scripting, GitHub de IAs, airef.github.io) | Medio |
| `[FOLKLORE]` | Creencia común sin fuente verificable | Bajo — **prohibido usar como base de código** |

Toda cifra que aparezca en un documento va con su fuente ("28× en el
corpus", "docs/01 §3", etc.). Sin fuente, no se escribe.

### 2.2. Regla anti-"falso inexistente" (el error de las murallas)

**Afirmar "no existe X", "no se puede hacer Y" o "0 usos" exige TODOS
estos pasos:**

1. **Al menos DOS búsquedas complementarias** con patrones distintos:
   forma exacta, variantes de sintaxis (`(build wall)` vs
   `build-wall`), sinónimos, singular/plural, mayúsculas, prefijos.
2. **Consulta de fuentes primarias disponibles**: `CPSB.pdf` (o su
   extracto), `UserPatchConst.per`, el código del propio repo
   **incluido `legacy/`** — el proyecto ya puede haber tenido la
   respuesta.
3. **Búsqueda ampliada en el corpus** y en docs de la comunidad.
4. **Si queda duda: buscar en foros** (§2.3) **o preguntar al usuario**.
5. La conclusión negativa se documenta con los **patrones exactos**
   usados, de modo que sea reproducible y refutable.

Regla derivada: **los grep únicos no autorizan conclusiones**. Y nunca
concluir sobre el motor a partir de un solo comando sin probar variantes
(`(build X)` vs `(build-x ...)` vs comandos UP).

### 2.3. Fuentes autorizadas para investigar

- `reference/CPSB.pdf` + `reference/UserPatchConst.per` (primarias).
- Corpus `reference/ais/` (con conteos siempre).
- Foros y comunidad: **HeavenGames Scripting Forum**, repos de IAs de
  élite en GitHub (The Horde, Promi, Barbarian, etc.),
  **airef.github.io** (referencia UP), documentación de UserPatch.
- El usuario de este repo: conoce su propio proyecto (forty v1/v2) y su
  criterio manda.

### 2.4. Código e identificadores: cero invenciones

- Todo identificador/comando nuevo debe resolverse desde: catálogo UP,
  CPSB, corpus, o código existente del repo. **Si no se puede verificar,
  no se escribe** (o se pregunta).
- Todo `.per` pasa el lint del proyecto:
  `python3 tools/lint_siege.py . <siege|forty|semiUtils>` **+ regresión** de
  los demás proyectos y `python3 -m unittest -v tools.test_lint_siege`.
- Estilo obligatorio (`docs/01`): ASCII estricto (sin acentos ni `ñ`),
  ≤16 elementos por lista, `disable-self` en init, **rearme de timers SIEMPRE al final del archivo** (los consumidores antes), nada de
  paréntesis en comentarios, line-endings consistentes.

## 3. Protocolo de implementación

- **Desarrollo medido y documentado**: iteraciones; cada paso deja el
  repo en estado válido y funcional ("hello world" ejecutable primero,
  crecimiento por capas). Está bien no terminar toda la lógica en un
  turno si el avance queda funcional, probado y documentado.
- **No editar el mismo archivo con llamadas en paralelo** (se pisan
  entre sí). Las ediciones al mismo archivo van SERIADAS.
- **Backup antes de operaciones destructivas** (`git mv`, `reset`,
  `rm`). Verificar `git log -1` antes de cada commit.
- **Commits atómicos** con mensaje que diga QUÉ y POR QUÉ; push solo a
  la rama `arena/...` de la sesión.
- Los artefactos grandes/datos generados NO van al Git (seguir
  `.gitignore` y convenciones del repo).

## 4. Protocolo de revisión (nada se entrega sin revisar)

### 4.1. Checklist de Entrega (DoD) — TODA tarea

- [ ] Checklist de la tarea repasada **literalmente**, punto por punto.
- [ ] `python3 tools/lint_siege.py . <proyecto>` → OK, y regresión de
      los otros proyectos → OK.
- [ ] **Caza de afirmaciones negativas** en todo lo escrito en la tarea
      ("no existe", "no se puede", "0 usos", "imposible", "nunca"):
      cada una pasa el protocolo §2.2 o se corrige.
- [ ] Toda afirmación de documento lleva etiqueta de procedencia (§2.1)
      y toda cifra su fuente.
- [ ] Docs actualizados: doc de la tarea + índice `docs/README.md` +
      READMEs afectados.
- [ ] Relectura completa del **diff final** con ojos de auditor hostil:
      palabras cortadas, numeraciones rotas, tablas incompletas,
      números sin fuente, código que el lint no cubra (DUC arities,
      orden de `set-goal`).
- [ ] `git status` limpio (todo lo intencionado commiteado), commit y
      push realizados, `git log -1` verificado.
- [ ] Resumen final en español: qué se hizo, cómo se verificó,
      evidencias, qué queda pendiente y cómo probarlo.

### 4.2. Pruebas funcionales

- Si la tarea toca lógica de juego y hay forma de probarla, la prueba
  se define (pasos + criterios observables) y se documenta. Si no hay
  forma de probarla aquí, se dice explícitamente y se deja la prueba
  para el usuario (ej. `forty vs forty`, `siege vs siege`).

## 5. Protocolo de documentación

- Todo artefacto tiene su documento en `docs/` (numerado) y todo
  documento está en el índice `docs/README.md`.
- La documentación se escribe/actualiza **en la misma tarea**, no
  después.
- Los errores propios del agente se registran con: qué pasó, por qué,
  cómo se corrigió y **qué regla nueva nace** (y se añade a §8).
- Cambios de dirección o correcciones del usuario: se implementan, se
  documentan y se registra la corrección en §8.

## 6. Cuando no se sabe algo

1. **Investigar primero** (§2.2–2.3): fuentes primarias → corpus →
   foros/comunidad.
2. **Si sigue sin resolverse o es una decisión de diseño: PREGUNTAR**
   al usuario, con opciones concretas y su coste/beneficio. Preguntar
   NO es fallar; inventar SÍ.
3. Etiquetar como `[FOLKLORE]` cualquier cosa que quede sin verificar y
   **no construir sobre ella** hasta confirmar.

## 7. Comunicación

- Respuestas en **español**.
- Estructura de cierre de tarea: **hecho / verificación / evidencias /
  pendientes / cómo probar**.
- Correcciones del usuario: aceptarlas sin defender lo propio; verificar
  el hecho en el código/fuentes; corregir código + docs; añadir la
  lección a §8; agradecer y decir claramente qué cambió.

---

## 8. Registro vivo de lecciones (actualizar con CADA error nuevo)

| # | Fecha | Error | Regla nacida |
|---|---|---|---|
| 1 | 2026-10-13 | Afirmé "los AIs no pueden construir murallas / 0 usos de `(build wall)`" tras **un solo grep**; el comando real era `build-wall <perimetro> <tipo>` y el propio forty v1/v2 lo usaba | §2.2 completo: dos búsquedas mínimo, fuentes primarias, `legacy/` leído, conclusión negativa siempre reproducible |
| 2 | 2026-10-13 | Escribí la aridad de `up-set-target-object` de memoria (2 args) y era 3 (`search-local c: 0`) | §2.4: aridades solo desde corpus/CPSB; el lint valida POS/aridad |
| 3 | 2026-10-13 | Acentos (`ñ`) en un `.per` — rompe el ASCII estricto | §2.4: ASCII obligatorio + lint |
| 4 | 2026-10-13 | Varias ediciones `edit_file` en paralelo al mismo documento: una se perdió (numeración rota) | §3: ediciones al mismo archivo SERIADAS |
| 5 | 2026-10-13 | El sandbox reseteó el historial git dos veces; se perdió trabajo no respaldado (`fortyV2-included.per`) | §1/§3: respaldar worktree antes de pausas; verificar `git log -1`; confiar en el remoto como fuente de verdad |
| 6 | 2026-10-13 | Prometí contenido de docs/05 antes de escribirlo | §5: documentar en la misma tarea, y el resumen final solo describe lo que EXISTE en el repo |
| 7 | 2026-10-13 | Al ampliar el linter, un regex de `defconst` exigía exactamente un espacio y el esquema omitía los facts CPSB válidos `attack-soldier-count`/`defend-soldier-count`; produjo falsos positivos en SemiUtils | Toda ampliación del linter incluye proyecto limpio + defectos inyectados; una firma rechazada se contrasta con CPSB antes de clasificarla como error |
| 8 | — | _próxima lección_ | _regla nacida_ |

> Cada nueva fila se añade junto con su corrección. Antes de cerrar una
> tarea, repasar esta tabla en busca de errores parecidos al trabajo
> recién hecho.

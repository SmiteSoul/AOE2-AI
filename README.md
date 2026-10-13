# Proyecto de IA Avanzada para Age of Empires II (UserPatch 1.5)

Este repositorio contiene una colección de scripts de Inteligencia Artificial (`.per`) diseñados para funcionar con **Age of Empires II: The Conquerors** y el parche **UserPatch 1.5**. El objetivo es crear IAs generalistas, adaptativas y robustas, que vayan más allá de los scripts estándar del juego.

## 📂 Estructura del Repositorio

- **`agent.md`**: **Protocolo de trabajo del agente (LEER PRIMERO)** — reglas permanentes: nada se salta, todo se documenta, se revisa y se evalúa; lo que no se sabe se investiga (foros/fuentes) o se pregunta. Incluye el registro vivo de lecciones.
- **`/semiUtils/`**: IA generalista monolítica `semiutils.per` (1511 líneas, 145 reglas; [medición reproducible](docs/07_Investigacion_AoC_UP15_y_Auditoria.md#81-métricas-ejecutables-tras-la-corrección)) con director de modos, diplomacia y timers. Ver [`semiUtils/README.md`](semiUtils/README.md).
    - `semiutils.per`: Archivo principal autocontenido (const/init/eco/build/combat).
- **`/forty/`**: **`forty`**, la ciudad-fortaleza medieval unificada (un solo `forty.ai`/`forty.per`): fases de ciudad, murallas de doble perímetro, director de modos, micro DUC. Ver [`forty/README.md`](forty/README.md) y [`docs/06_Forty_Feudo.md`](docs/06_Forty_Feudo.md).
- **`/siege/`**: **`siege`**, IA de asedio pura ya implementada (arietes cargados, brechas, TSA, evaluación de objetivos). Ver [`siege/README.md`](siege/README.md).
- **`/tools/`**: validación estática de los tres proyectos — `lint_siege.py` (resolución, gramática, aridad, goals DUC, estados, wildcards, muros, duplicados y timers) + `test_lint_siege.py` (9 regresiones).
- **`/docs/`**: hechos del motor con evidencia, prevención de errores, pipeline, arquitecturas del corpus e [investigación/auditoría integral de AoC + UP 1.5](docs/07_Investigacion_AoC_UP15_y_Auditoria.md). Ver [`docs/README.md`](docs/README.md).
- **`/reference/`**:
    - `UserPatchConst.per`: Archivo de constantes de UserPatch. **Esencial** para que los comandos `up-` funcionen.
    - `CPSB.pdf`: manual base de scripting de AoE2; fuente primaria para la gramática y la semántica vanilla.
    - `ais/`: IAs de terceros importadas como referencia de estudio (Barbarian 2.18, The Horde, Kaia, The General, Binary, Crusher, Brutal2, Promi, Training). Ver [`reference/ais/README.md`](reference/ais/README.md) para el índice y las fuentes.
- **`Script_Errors.md`**: registro histórico de errores de parser/runtime (ERR6002, ERR2005, comparadores en `goal`, `UserPatchConst`, etc.) con origen técnico y solución. Ver [`Script_Errors.md`](Script_Errors.md).
- **`README.md`**: Este archivo.

## ⚙️ Requisitos

- **Age of Empires II: The Conquerors** (versión 1.0c).
- **UserPatch 1.5** instalado. Puedes encontrarlo en [userpatch.aiscripters.net](https://userpatch.aiscripters.net/).

> **Estado de validación (2026-10-13):** `siege`, `forty` y `semiUtils` pasan
> el linter y sus regresiones estáticas. Las correcciones de esta auditoría
> todavía requieren partidas reales en AoC 1.0c + UP 1.5; ver el plan en
> [`docs/07`](docs/07_Investigacion_AoC_UP15_y_Auditoria.md#11-plan-de-validación-en-el-juego).

## 📥 Material importado y atribución

Los archivos bajo `reference/` (constantes de UserPatch, CPSB y las IAs de
`reference/ais/`) son **material de terceros** descargado de repositorios
públicos de GitHub e incluido aquí con fines de estudio y referencia. Los
derechos pertenecen a sus autores originales; si alguno solicita su retirada,
se elimina. El detalle de cada fuente está en [`reference/README.md`](reference/README.md).

## 🐞 Correcciones Clave Aplicadas

Este proyecto no es solo una colección de scripts, sino que documenta un proceso de depuración profunda. Los errores más comunes que se corrigieron fueron:

1.  **Constantes de UserPatch visibles**: Siege carga `UserPatchConst` antes de los comandos `up-`; Forty incorpora el mismo catálogo en su monolito.
2.  **Identificadores Válidos**: Se reemplazaron identificadores inexistentes en el motor (ej. `ri-fire-ship`) por los correctos (`ri-war-galley`).
3.  **Uso Correcto de `goal`**: El fact `(goal ...)` solo compara igualdad. Se eliminaron todas las comparaciones (`<`, `>`) y se reescribieron como reglas independientes para cada valor posible.
4.  **Optimización de Reglas**: Se dividieron reglas demasiado largas para evitar el error `Rule too long` (máx. 16 elementos por regla) y se eliminaron bloques duplicados.
5.  **Goals DUC extendidos**: Los puntos usan 100–101 y `up-get-search-state` usa 102–105; los slots vanilla 1–40 no sirven para pares/cuaternas automáticos de UP.
6.  **Estados inicializados**: Forty fija explícitamente director, ciudad, oleada y chat porque los goals comienzan en `-1`.
7.  **Wildcards seguros**: `this-any-*` solo se consume dentro de la regla que lo enlaza y en acciones compatibles; Siege/Forty eligen enemigo con `up-find-player`.
8.  **Timers multicast**: los consumidores preceden al rearme final, que de otro modo borraría el estado `triggered` para las reglas posteriores.

El **registro histórico** de errores de parser está en [`Script_Errors.md`](Script_Errors.md); la investigación, los defectos lógicos encontrados y el plan de prueba runtime están en [`docs/07_Investigacion_AoC_UP15_y_Auditoria.md`](docs/07_Investigacion_AoC_UP15_y_Auditoria.md).

## 🤖 Uso con Agentes de IA

Este repositorio está estructurado para ser consumido por agentes de IA de codificación. Se recomienda:

- **DevHive**: Para un pipeline de desarrollo autónomo que gestione especificaciones y tareas.
- **Assembler Agent Pattern**: Para coordinar múltiples agentes (planificador, desarrollador, QA) que trabajen sobre el repositorio.
- **GitScape**: Para compilar el repositorio en una "Skill" que agentes como Cursor o Claude Code puedan usar para entender el proyecto en profundidad.

## 🔗 Referencias y IAs de Nivel Similar

Para inspirarte en la complejidad y estructura de IAs avanzadas, aquí tienes enlaces a proyectos destacados:

- **AIREf**: índice vivo de comandos, strategic numbers, límites, bugs y DUC; hay que filtrar siempre AoC/UP/DE ([airef.github.io](https://airef.github.io/)).
- **AI Strategy Builder**: generador desde hojas compatible con DE y UP 1.5; actualmente alpha ([TMB-2197/aoe2-ai-strategy-builder](https://github.com/TMB-2197/aoe2-ai-strategy-builder)).
- **AlphaScripter**: evolución genética y automatización orientada a AoC + UP 1.5 ([mboop127/AlphaScripter](https://github.com/mboop127/AlphaScripter)).
- **PyAge2**: entorno Gym/simulación acelerada probado por su autor en UP 1.5/1.6; requiere inyección Win32 y aislamiento de investigación ([kachayev/pyage2](https://github.com/kachayev/pyage2)).
- **Repositorio de darkeclipz**: Barbarian 2.18, Kaia, Horde y otros scripts clásicos ([darkeclipz/aoe2-ai](https://github.com/darkeclipz/aoe2-ai)).
- **AoE2 AI Module (FLWL)**: API/DLL que expone funciones internas; no es sustituto portable de un `.per` ([FLWL/aoe2-ai-module](https://github.com/FLWL/aoe2-ai-module)).
- **Foros de AI Scripters**: comunidad central para discusión y pruebas ([forums.aiscripters.com](https://forums.aiscripters.com/)).

La evaluación versionada de estas herramientas está en [`docs/07` §10](docs/07_Investigacion_AoC_UP15_y_Auditoria.md#10-ecosistema-de-herramientas-evaluado).

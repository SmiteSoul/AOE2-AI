# Proyecto de IA Avanzada para Age of Empires II (UserPatch 1.5)

Este repositorio contiene una colección de scripts de Inteligencia Artificial (`.per`) diseñados para funcionar con **Age of Empires II: The Conquerors** y el parche **UserPatch 1.5**. El objetivo es crear IAs generalistas, adaptativas y robustas, que vayan más allá de los scripts estándar del juego.

## 📂 Estructura del Repositorio

- **`/semiUtils/`**: Contendrá la IA generalista `semiUtils.per` y sus módulos. *(en preparación)*
    - `semiUtils.per`: Archivo principal que carga todos los módulos.
    - `semiUtils-*.per`: Módulos especializados (const, init, eco, build, train, combat, etc.).
- **`/forty/`**: Contendrá la IA `forty.per`, una versión mejorada de una IA defensiva existente. *(en preparación)*
- **`/reference/`**:
    - `UserPatchConst.per`: Archivo de constantes de UserPatch. **Esencial** para que los comandos `up-` funcionen.
    - `CPSB.pdf`: La guía de scripting de AoE2 (opcional, pero muy útil).
    - `ais/`: IAs de terceros importadas como referencia de estudio (Barbarian 2.18, The Horde, Kaia, The General, Binary, Crusher, Brutal2, Promi, Training). Ver [`reference/ais/README.md`](reference/ais/README.md) para el índice y las fuentes.
- **`README.md`**: Este archivo.

## ⚙️ Requisitos

- **Age of Empires II: The Conquerors** (versión 1.0c).
- **UserPatch 1.5** instalado. Puedes encontrarlo en [userpatch.aiscripters.net](https://userpatch.aiscripters.net/).

## 📥 Material importado y atribución

Los archivos bajo `reference/` (constantes de UserPatch, CPSB y las IAs de
`reference/ais/`) son **material de terceros** descargado de repositorios
públicos de GitHub e incluido aquí con fines de estudio y referencia. Los
derechos pertenecen a sus autores originales; si alguno solicita su retirada,
se elimina. El detalle de cada fuente está en [`reference/README.md`](reference/README.md).

## 🐞 Correcciones Clave Aplicadas

Este proyecto no es solo una colección de scripts, sino que documenta un proceso de depuración profunda. Los errores más comunes que se corrigieron fueron:

1.  **Carga de `UserPatchConst`**: Se aseguró que `(load "UserPatchConst")` esté presente antes de cualquier comando `up-` para evitar errores de identificador inválido.
2.  **Identificadores Válidos**: Se reemplazaron identificadores inexistentes en el motor (ej. `ri-fire-ship`) por los correctos (`ri-war-galley`).
3.  **Uso Correcto de `goal`**: El fact `(goal ...)` solo compara igualdad. Se eliminaron todas las comparaciones (`<`, `>`) y se reescribieron como reglas independientes para cada valor posible.
4.  **Optimización de Reglas**: Se dividieron reglas demasiado largas para evitar el error `Rule too long` (máx. 16 elementos por regla) y se eliminaron bloques duplicados.

## 🤖 Uso con Agentes de IA

Este repositorio está estructurado para ser consumido por agentes de IA de codificación. Se recomienda:

- **DevHive**: Para un pipeline de desarrollo autónomo que gestione especificaciones y tareas.
- **Assembler Agent Pattern**: Para coordinar múltiples agentes (planificador, desarrollador, QA) que trabajen sobre el repositorio.
- **GitScape**: Para compilar el repositorio en una "Skill" que agentes como Cursor o Claude Code puedan usar para entender el proyecto en profundidad.

## 🔗 Referencias y IAs de Nivel Similar

Para inspirarte en la complejidad y estructura de IAs avanzadas, aquí tienes enlaces a proyectos destacados:

- **AlphaScripter**: Usa algoritmos genéticos para evolucionar scripts de IA para AoE2 ([mboop127/AlphaScripter](https://github.com/mboop127/AlphaScripter)).
- **Repositorio de scripts de Code-of-Empires**: Colección de scripts de IA personalizados para AoE2DE.
- **Repositorio de darkeclipz**: Contiene la IA **Barbarian 2.18**, una de las más respetadas, junto a otras como Kaia y Horde ([darkeclipz/aoe2-ai](https://github.com/darkeclipz/aoe2-ai)).
- **AoE2 AI Module (FLWL)**: Librería que extiende las capacidades del scripting más allá del sistema de reglas, exponiendo funciones internas del juego ([FLWL/aoe2-ai-module](https://github.com/FLWL/aoe2-ai-module)).
- **Foros de AI Scripters**: La comunidad central para discusión y ayuda sobre scripting de IA para AoE2 ([forums.aiscripters.com](https://forums.aiscripters.com/)).
- **AoE2 AI Scripting Encyclopedia**: Referencia exhaustiva de comandos, strategic numbers y DUC ([airef.github.io](https://airef.github.io/)).

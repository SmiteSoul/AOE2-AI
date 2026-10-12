# Proyecto de IA Avanzada para Age of Empires II (UserPatch 1.5)

Este repositorio contiene una colección de scripts de Inteligencia Artificial (`.per`) diseñados para funcionar con **Age of Empires II: The Conquerors** y el parche **UserPatch 1.5**. El objetivo es crear IAs generalistas, adaptativas y robustas, que vayan más allá de los scripts estándar del juego.

## 📂 Estructura del Repositorio

- **`/semiUtils/`**: Contiene la IA generalista `semiUtils.per` y sus módulos.
    - `semiUtils.per`: Archivo principal que carga todos los módulos.
    - `semiUtils-*.per`: Módulos especializados (const, init, eco, build, train, combat, etc.).
- **`/forty/`**: Contiene la IA `forty.per`, una versión mejorada de una IA defensiva existente.
- **`/reference/`**:
    - `UserPatchConst.per`: Archivo de constantes de UserPatch. **Esencial** para que los comandos `up-` funcionen.
    - `CPSB.pdf`: La guía de scripting de AoE2 (opcional, pero muy útil).
- **`README.md`**: Este archivo.

## ⚙️ Requisitos

- **Age of Empires II: The Conquerors** (versión 1.0c).
- **UserPatch 1.5** instalado. Puedes encontrarlo en [userpatch.aiscripters.net](https://userpatch.aiscripters.net/)[reference:7].

## 🐞 Correcciones Clave Aplicadas

Este proyecto no es solo una colección de scripts, sino que documenta un proceso de depuración profunda. Los errores más comunes que se corrigieron fueron:

1.  **Carga de `UserPatchConst`**: Se aseguró que `(load "UserPatchConst")` esté presente antes de cualquier comando `up-` para evitar errores de identificador inválido[reference:8].
2.  **Identificadores Válidos**: Se reemplazaron identificadores inexistentes en el motor (ej. `ri-fire-ship`) por los correctos (`ri-war-galley`)[reference:9].
3.  **Uso Correcto de `goal`**: El fact `(goal ...)` solo compara igualdad. Se eliminaron todas las comparaciones (`<`, `>`) y se reescribieron como reglas independientes para cada valor posible.
4.  **Optimización de Reglas**: Se dividieron reglas demasiado largas para evitar el error `Rule too long` y se eliminaron bloques duplicados.

## 🤖 Uso con Agentes de IA

Este repositorio está estructurado para ser consumido por agentes de IA de codificación. Se recomienda:

- **DevHive**: Para un pipeline de desarrollo autónomo que gestione especificaciones y tareas[reference:10].
- **Assembler Agent Pattern**: Para coordinar múltiples agentes (planificador, desarrollador, QA) que trabajen sobre el repositorio[reference:11].
- **GitScape**: Para compilar el repositorio en una "Skill" que agentes como Cursor o Claude Code puedan usar para entender el proyecto en profundidad[reference:12].

## 🔗 Referencias y IAs de Nivel Similar

Para inspirarte en la complejidad y estructura de IAs avanzadas, aquí tienes enlaces a proyectos destacados:

- **AlphaScripter**: Usa algoritmos genéticos para evolucionar scripts de IA para AoE2[reference:13].
- **Repositorio de scripts de Code-of-Empires**: Colección de scripts de IA personalizados para AoE2DE[reference:14].
- **Repositorio de darkeclipz**: Contiene la IA **Barbarian 2.18**, una de las más respetadas, junto a otras como Kaia y Horde[reference:15].
- **AoE2 AI Module (FLWL)**: Librería que extiende las capacidades del scripting más allá del sistema de reglas, exponiendo funciones internas del juego[reference:16].
- **Foros de AI Scripters**: La comunidad central para discusión y ayuda sobre scripting de IA para AoE2[reference:17].

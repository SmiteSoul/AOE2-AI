# ais/ — IAs de terceros importadas como referencia

Colección de scripts `.per` de IAs reconocidas de la comunidad, útiles para
estudiar arquitecturas, patrones de reglas, DUC, manejo de goals/escrow, etc.
**Todos son obra de sus autores; se incluyen solo como material de estudio.**

| Carpeta | IA | Descripción | Fuente |
|---|---|---|---|
| `barbarian-2.18/` | **Barbarian 2.18** (por II2N/TheMax) | La IA competitiva de referencia para UserPatch (micro con DUC, decenas de estrategias, DM, team games). Archivo principal de ~1,9 MB + módulos. | [darkeclipz/aoe2-ai](https://github.com/darkeclipz/aoe2-ai) |
| `the-horde-3.9/` | **The Horde 3.9** | IA clásica muy respetada, enfoque macro sólido. | [darkeclipz/aoe2-ai](https://github.com/darkeclipz/aoe2-ai) |
| `kaia/` | **Kaia** (3 versiones) | `Kaia.per` (versión simple), `kaia2/` (versión modular nueva) y `kaia-old/` (modular anterior). Buena referencia de arquitectura limpia por módulos. | [darkeclipz/aoe2-ai](https://github.com/darkeclipz/aoe2-ai) |
| `training/` | **Training 1–7** | IAs de dificultad progresiva usadas para entrenar/tornear; perfectas para aprender por niveles (incl. `Training4/TSA366.per`, un TSA completo). | [darkeclipz/aoe2-ai](https://github.com/darkeclipz/aoe2-ai) |
| `the-general/` | **The General 1.3** (+ *The Captain*, *The Conscript*) | IA modular grande para UP: carpetas `Functions/`, DUC, escrow, control de ejército. Modelo de arquitectura para `semiUtils`. | [airef/the-general-ai](https://github.com/airef/the-general-ai) |
| `binary/` | **Binary** | IA modular con `Functions/` reutilizables, interfaz pública entre módulos y buenas prácticas de constantes. | [01010100b/AoE2](https://github.com/01010100b/AoE2) |
| `crusher/` | **Crusher** | IA moderna pequeña y legible, organizada por edades (`dark/`, `feudal/`, `castle/`…). Incluye su `LICENSE`. | [CalvinNeo/Age-of-Empires-Crusher](https://github.com/CalvinNeo/Age-of-Empires-Crusher) |
| `brutal2/` | **Brutal2** | IA de **arena** de alto nivel (fast imperial, boom, defensa con murallas). Inspiración directa para `forty/`. | [SiegeEngineers/WololoKingdoms](https://github.com/SiegeEngineers/WololoKingdoms) (`resources/Script.AI/Brutal2`) |
| `promi/` | **Promi** (versión UserPatch) | IA moderna muy estudiada de la comunidad, con módulos de TSA, unidades, amenazas, etc. (también existe versión para DE). | [SiegeEngineers/WololoKingdoms](https://github.com/SiegeEngineers/WololoKingdoms) (`resources/Script.AI/Promi`) |

## No incluidos (pero disponibles en las fuentes)

- **BruteForce 3.1** e **Immobile Units AI GOLD** — en `resources/Script.AI/` de
  [SiegeEngineers/WololoKingdoms](https://github.com/SiegeEngineers/WololoKingdoms).
- **Alpha / AlphaScripter** — el script "evolucionado" (`best.txt`) no es un
  `.per` jugable sino el genoma del algoritmo genético; el código que lo genera
  está en [mboop127/AlphaScripter](https://github.com/mboop127/AlphaScripter)
  (`ai_writer.py` lo puede renderizar a `.per`).
- **AoE2 AI Module (FLWL)** — librería DLL/gRPC para extender el scripting más
  allá de las reglas: <https://github.com/FLWL/aoe2-ai-module>

## Cómo usarlas

Estas IAs están aquí para **leerlas**, no para el juego. Para probar una en el
juego, copia su carpeta (con su `.ai`/`.per`) al directorio `AI/` de la
instalación de AoC con UserPatch y selecciónala en la partida.

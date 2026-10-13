# reference/ — Documentación y material de referencia

Material de referencia para el desarrollo de IAs de AoE2 (UserPatch 1.5).
Todo lo importado aquí es **material de terceros descargado de repositorios
públicos de GitHub**, incluido con fines de estudio. Los derechos pertenecen a
sus autores originales; si alguno solicita su retirada, se elimina sin problema.

## Contenido

| Ruta | Qué es | Fuente |
|---|---|---|
| `UserPatchConst.per` | Constantes oficiales de **UserPatch 1.5** (`defconst` de los comandos `up-*`, FactId/ObjectData ampliados, etc.). **Obligatorio** cargarlo antes de usar comandos `up-`. | [airef/the-general-ai](https://github.com/airef/the-general-ai) (copia canónica de UP 1.5) |
| `CPSB.pdf` | *Computer Player Strategy Builder Guide* — guía oficial de scripting de Ensemble Studios (lista de facts, actions y strategic numbers). | [darkeclipz/aoe2-ai](https://github.com/darkeclipz/aoe2-ai) |
| `ais/` | Colección de IAs de terceros para estudio. Ver [`ais/README.md`](ais/README.md). | varios (ver índice) |

## Referencias en línea (no descargables desde aquí)

- UserPatch 1.5 (web oficial, guía `Reference.html` incluida en el zip del parche):
  <http://userpatch.aiscripters.net/> · referencia: <http://userpatch.aiscripters.net/reference.html>
- CPSB.pdf en la web oficial de UserPatch: <http://userpatch.aiscripters.net/CPSB.pdf>
- AoE2 AI Scripting Encyclopedia (excelente buscador de comandos/SNs/DUC):
  <https://airef.github.io/>
- Foros de la comunidad (scripts, torneos, ayuda): <https://forums.aiscripters.com/>
- Guía de scripting en Steam: <https://steamcommunity.com/sharedfiles/filedetails/?id=1238296169>

## Notas

- Las variantes de `UserPatchConst.per` incluidas dentro de algunas IAs en
  `ais/` (p. ej. `binary/Binary/UserPatchConst.per`, `brutal2/UserPatchConst.per`)
  se conservan **tal cual en su fuente** para que cada IA sea autocontenida;
  pueden diferir ligeramente según la versión de UserPatch para la que se
  empaquetaran.
- No se importaron binarios ni `.zip` duplicados de las fuentes (editores,
  paquetes comprimidos, etc.), solo scripts `.per`/`.ai`, documentación y
  licencias.

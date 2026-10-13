# FORTY — El Reino Fortificado

Una IA capaz de **armar de forma organizada y con sentido fortalezas y
ciudades o pueblos**, y de **gestionarse y organizarse**: FORTY.

> **Estado: VERSION UNIFICADA (v1 + v2), funcional.** Un solo `.per` y
> un solo `.ai`, autocontenidos, para AoC + UserPatch 1.5. Diseño
> completo en [`docs/06_Forty_Feudo.md`](../docs/06_Forty_Feudo.md);
> análisis de unificación en
> [`docs/05_Unificacion_Forty.md`](../docs/05_Unificacion_Forty.md).

## Estructura

| Archivo | Contenido |
|---|---|
| `forty.ai` + `forty.per` | **La IA** (1334 líneas): director de modos + fases de ciudad, economía del feudo, construcción por fases (aldea → villa → muralla → plaza), investigación rápida, milicia, defensa con aldeanos, asalto con oleadas + TSA + micro DUC (fuego concentrado, asedio a edificios), mercado. |
| `legacy/forty-v1.per/.ai` | La primera identidad ("El Reino Fortificado", `gl-mode`), preservada. |
| `legacy/fortyV2.per/.ai` | Los 6217 líneas de la rama mecánica (incl. módulo `feudalAgeDynamic`), preservadas como referencia. |
| `legacy/fortyV2-included.per` | `fortyV2` + constantes UP (copia monolito para probar V2 tal cual). |

## Doctrina urbana (resumen)

La ciudad crece por fases, como un feudo medieval:

1. **Aldea**: casas, granja, molino, campamentos (sobrevivir).
2. **Villa**: plaza de mercado, gremio (blacksmith), cuarteles, iglesia.
3. **Muralla**: torres con cuadrillas + anillo de casas (el burgage como
   muro — el motor no deja construir murallas de piedra, ver docs/06) +
   explotación de piedra.
4. **Plaza fuerte**: **castillo** (el keep), taller de asedio, establos,
   universidad, más torres y casas.

Un "bailiff" (el director) gobierna los modos: gestionar y crecer,
defender la ciudad atacada, o lanzar campañas organizadas.

## Cómo probarla

Copiar `forty.ai` y `forty.per` a la carpeta `AI/` del juego (las dos
carpetas `forty` de dos instalaciones, o `forty` vs `forty` en DE con la
copia unificada). La prueba del proyecto: **forty vs forty**.

## Verificación

`python3 tools/lint_siege.py . forty` → OK sin errores (resolución de
identificadores, gramática, aridades, constantes y POS del corpus).

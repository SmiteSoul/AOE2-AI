# FORTY — El Reino Fortificado

Una IA capaz de **armar de forma organizada y con sentido fortalezas y
ciudades o pueblos**, y de **gestionarse y organizarse**: FORTY.

> **Estado: versión unificada (v1 + v2), corregida estáticamente.** Un solo
> `.per` y un solo `.ai`, autocontenidos, para AoC 1.0c + UserPatch 1.5. El linter
> pasa; la validación completa en partida sigue pendiente. Diseño en
> [`docs/06_Forty_Feudo.md`](../docs/06_Forty_Feudo.md), auditoría y plan de
> prueba en [`docs/07`](../docs/07_Investigacion_AoC_UP15_y_Auditoria.md).

## Estructura

| Archivo | Contenido |
|---|---|
| `forty.ai` + `forty.per` | **La IA** (1534 líneas, 101 reglas): director de modos + fases de ciudad, economía del feudo, construcción por fases (aldea → villa → muralla → plaza), investigación, milicia, defensa coordinada, oleadas + TSA + micro DUC y mercado. |
| `legacy/forty-v1.per/.ai` | La primera identidad ("El Reino Fortificado", `gl-mode`), preservada. |
| `legacy/fortyV2.per/.ai` | Las 6217 líneas de la rama mecánica (incl. módulo `feudalAgeDynamic`), preservadas como referencia. |
| `legacy/fortyV2-included.per` | `fortyV2` + constantes UP (copia monolito para probar V2 tal cual). |

Métricas del ejecutable: [conteo de `docs/07` §8.1](../docs/07_Investigacion_AoC_UP15_y_Auditoria.md#81-métricas-ejecutables-tras-la-corrección).
Las cifras de `legacy/` describen los artefactos históricos preservados.

## Doctrina urbana (resumen)

La ciudad crece por fases, como un feudo medieval:

1. **Aldea**: casas, granja, molino, campamentos (sobrevivir).
2. **Villa**: plaza de mercado, gremio (blacksmith), cuarteles, iglesia.
3. **Muralla**: **murallas de verdad** (doble perímetro): exterior de
   empalizada en Feudal → piedra en Castillo, interior de piedra, con
   `build-gate`, más torres con cuadrillas y el anillo de casas
   (burgage) por dentro + explotación de piedra.
4. **Plaza fuerte**: **castillo** (el keep), taller de asedio, establos,
   universidad, más torres y casas.

Un "bailiff" (el director) gobierna los modos: gestionar y crecer,
defender la ciudad atacada, o lanzar campañas organizadas.

## Cómo probarla

Copiar `forty.ai` y `forty.per` a la carpeta `AI/` del juego y seleccionar
`forty` para ambos jugadores. La prueba principal del proyecto es **forty vs
forty** en AoC 1.0c + UP 1.5; los criterios observables están en
[`docs/07` §11.2](../docs/07_Investigacion_AoC_UP15_y_Auditoria.md#112-forty-vs-forty).

## Verificación

```bash
python3 tools/lint_siege.py . forty
python3 -m unittest -v tools.test_lint_siege
```

Ambos pasan estáticamente. La auditoría corrigió la inicialización de las
cuatro máquinas de estado, el ciclo castillo/plaza, los goals extendidos DUC y
la selección de enemigo; falta confirmar su comportamiento dentro del juego.

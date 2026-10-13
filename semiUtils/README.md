# semiUtils — Conquistador diplomático

IA generalista para **Age of Empires II: The Conquerors 1.0c + UserPatch
1.5**. La implementación actual no es el esqueleto modular que describía el
README antiguo: es un monolito clásico y autocontenido.

> **Estado (2026-10-13):** corregida y validada estáticamente; prueba completa
> en partida pendiente. Auditoría: [`docs/07`](../docs/07_Investigacion_AoC_UP15_y_Auditoria.md#84-semiutils).

## Archivos

| Archivo | Contenido |
|---|---|
| `semiutils.ai` | Archivo vacío que registra la IA en el selector del juego. |
| `semiutils.per` | 1511 líneas, 145 reglas y 19 `defconst`; no contiene llamadas ejecutables `up-*`. |

Fuente de las métricas:
[conteo de `docs/07` §8.1](../docs/07_Investigacion_AoC_UP15_y_Auditoria.md#81-métricas-ejecutables-tras-la-corrección).

## Arquitectura real

El script incluye, en este orden conceptual:

1. goals de personalidad, modo y diplomacia, todos inicializados;
2. tres timers (`t-director`, `t-pulse`, `t-diplo`);
3. init de economía, exploración, grupos y objetivos;
4. producción de aldeanos y edificios por edad;
5. planificación y construcción del perímetro 1, puerta y castillos;
6. granjas, distribución económica, mercado e investigación;
7. producción militar normal y modo all-in;
8. comercio, tributos, taunts y diplomacia IA/humano;
9. director de ataque/defensa y pulsos de refuerzo;
10. rearmes de los tres timers al final, después de sus consumidores.

## Correcciones de la auditoría

- Se añadió `enable-wall-placement 1` antes de `build-wall`/`build-gate`.
- Se eliminó la segunda copia exacta de las tres reglas de edificios all-in.
- Nueve signos de exclamación invertida Latin-1 se convirtieron a ASCII.
- Se retiraron doce usos ilegales de `this-any-*` como facts; el wildcard o
  taunt enlaza al jugador y las acciones compatibles consumen la variable.
- Los consumidores dejaron de rearmar timers prematuramente; los rearmes
  disjuntos están al final.
- El retorno a boom exige que la ciudad no esté bajo ataque, para no pisar
  `m-defend` en el mismo pase.

Evidencia y límites: [`docs/07` §§3–4, 8.4 y 11.4](../docs/07_Investigacion_AoC_UP15_y_Auditoria.md).

## Instalación

Copiar ambos archivos a la carpeta `AI/` de la instalación, respetando el
nombre en minúsculas:

```text
AI/
├── semiutils.ai
└── semiutils.per
```

Seleccionar `semiutils` como IA.

## Verificación

```bash
python3 tools/lint_siege.py . semiUtils
python3 -m unittest -v tools.test_lint_siege
```

El linter cubre resolución, gramática, 16 elementos, ASCII, duplicados,
wildcards, planificación de muros, estados y orden de timers. No prueba
pathfinding, balance ni diplomacia multijugador: seguir el plan runtime de
[`docs/07` §11.4](../docs/07_Investigacion_AoC_UP15_y_Auditoria.md#114-semiutils).

## Referencias

- [`../reference/CPSB.pdf`](../reference/CPSB.pdf) — gramática y semántica base.
- [`../reference/UserPatchConst.per`](../reference/UserPatchConst.per) — catálogo UP.
- [`../reference/ais/`](../reference/ais/) — corpus de arquitecturas y patrones.

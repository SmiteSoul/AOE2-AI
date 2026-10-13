# SIEGE — El Asediador Impenetrable

IA de asedio pura para **Age of Empires II: The Conquerors 1.0c + UserPatch
1.5**. Su objetivo es aplastar al enemigo con maquinaria de asedio: arietes
cargados de infantería, evaluación de objetivos, economía especializada,
unidades a distancia y apertura de brechas en las murallas.

> **Estado (2026-10-13):** lint y regresiones pasan; la auditoría estática no
> sustituye la prueba completa en partida, que sigue pendiente.

## Instalacion

Copia el **contenido** de esta carpeta dentro del directorio `AI/` de tu
instalacion de AoC con UserPatch:

```
AI/
├── siege.ai
├── siege.per
└── siege/
    ├── UserPatchConst.per
    └── ...modulos
```

Selecciona `siege` como IA de cualquier jugador. No usa trampas (no cheat salvo
la dificultad Hardest del motor).

## Diseno

| Modulo | Que hace |
|---|---|
| `siege.per` | Punto de entrada: carga `UserPatchConst` y todos los modulos. |
| `siege/const.per` | Goals de estado/producción (1–46), punto DUC 100–101, estado de búsqueda 102–105, timers y parámetros ajustables (`ts-*`, `ram-full`...). |
| `siege/init.per` | Numeros estrategicos: **`sn-garrison-rams 1`**, **`sn-wall-targeting-mode 1`**, perfil de `sn-target-evaluation-*`, `sn-special-attack-type1 town-center`. |
| `siege/eco.per` | Reparto de aldeanos por edad (madera/oro altos), reajuste dinamico, escrow para mejoras de asedio, mercado y avance de edad. |
| `siege/build.per` | Base economica + hasta 4 **talleres de asedio**, castillos (trebuchets), universidad, monasterio. |
| `siege/train.per` | Arietes/mangonel/escorpiones/trebuchets, alabarderos (guarnicion) y arqueros; todas las mejoras de asedio (`ri-siege-ram`, `ri-siege-onager`, `ri-heavy-scorpion`, `ri-siege-engineers`...). |
| `siege/combat.per` | Ciclos de oleada (attack groups + **TSA**), **brechas** (DUC arietes -> `wall-class`), **carga de arietes** (DUC `action-garrison`) y **fuego concentrado** a distancia con formacion escalonada. |

## Los 5 rasgos pedidos y como se implementan

1. **Armas de asedio**: produccion continua de la linea `battering-ram-line`,
   `mangonel-line`, `scorpion-line` y `trebuchet`; prioridad total a las
   mejoras del taller de asedio con escrow.
2. **Evaluacion de objetivos inteligente**:
   - `sn-target-evaluation-siege-weapon 10` (documentado en el CPSB): la
     maquinaria ataca objetivos estacionarios y el resto de unidades no pierde
     tiempo en ellos.
   - `sn-target-evaluation-in-progress 40`: mantener el foco una vez elegido.
   - `sn-special-attack-type1 town-center` + `influence1 20`: sesgo hacia el
     corazon enemigo.
   - `sn-target-evaluation-distance 25` / `time-kill-ratio 30` / `boat -10`.
3. **Economia para el ejercito de asedio**: reparto 35-40% comida / 30% madera /
   20-25% oro / 10% piedra, reajustes dinamicos cuando la madera u oro flaquean,
   mercado de compensacion y escrow dedicado a las mejoras caras.
4. **Arietes cargados de tropas**: `sn-garrison-rams 1` (el motor carga
   infanteria en los arietes antes de que el grupo de ataque parta) + rutina DUC
   que rellena con `action-garrison` los arietes con hueco (en AoC caben 4
   unidades; solo la infanteria mejora velocidad y ataque del ariete).
5. **Unidades a distancia y brechas**: arqueros con fuego concentrado DUC y
   formacion `formation-stagger` (menos dano de mangonelas enemigas), y
   apertura de brechas con `sn-wall-targeting-mode 1` mas DUC enviado arietes
   contra `wall-class` cuando el TSA no esta bloqueado (evita la confusion de
   unidades documentada en `up-target-objects`).

## Ajustes rapidos

Todos en `siege/const.per` y `siege/init.per`:

- Mas asedio: sube `gl-ram-want` / `gl-mango-want` / `gl-scorp-want` en
  `train.per` o el techo de talleres en `build.per`.
- Mas agresivo: baja `military-population >= 30` del inicio de oleada o sube
  `ts-step`.
- Mas defensivo: sube `sn-number-defend-groups` en `init.per`.

## Micromanejo (importado de patrones de The General / corpus)

Implementado en `combat.per` + `init.per`:

- **Oleadas escalonadas**: grupos de 2-12 unidades (`sn-minimum/maximum-
  attack-group-size`) en vez de un bloque unico; `sn-group-form-distance 30`
  para que las tropas no se queden reagrupando sin usar.
- **Recogida de tropas de escenario**: `sn-task-ungrouped-soldiers 1`,
  `sn-allow-civilian-defense 1`, `sn-consecutive-idle-unit-limit 1`.
- **Roles**: en la fase de brecha, los arietes solo buscan `wall-class` y
  `gate-class`; los **piqueros escoltan los arietes** y los **arqueros
  protegen la bateria** (accion `action-guard`); al abrirse el paso, los
  arqueros pasan a fuego concentrado con `formation-stagger` y **los arietes
  priorizan edificios** por orden: castillo, centro urbano, torres, resto.
- **Selección de jugador**: cada rutina obtiene un enemigo válido con
  `up-find-player enemy find-closest`; no depende de una variable
  `this-any-enemy` sin wildcard asociado.
- **Conciencia de brecha / pathfinding**: patrón de The General
  (`up-set-target-object` + `up-path-distance`; 65535 = sin camino) sobre el
  par extendido 100–101. Si hay camino corto hasta la base enemiga,
  `gl-target-walls` -> 0 y **se deja de tumbar puertas irrelevantes**; además
  la fase de brecha tiene time-box de 75s (`t-walls`).

Pendiente de prueba en partida (se confirmará o se ajustará): el comportamiento
de `action-guard` con listas de objetos y `up-get-point position-enemy`; la
validación estática solo confirma firmas y enums, no su efecto táctico.

## Orden de carga (importante para los timers)

`siege.per` carga los módulos en orden y **al final** rearma `t-eco` y
`t-micro`. Un timer agotado permanece en estado `triggered` hasta
`disable-timer` o un nuevo `enable-timer`; rearmarlo antes limpiaría el trigger
y las reglas posteriores no lo verían. Si editas los módulos, no muevas esos
rearmes antes de sus consumidores.

## Auditoria (lint) — obligatoria tras cualquier edicion

`tools/lint_siege.py` valida el proyecto contra CPSB, constantes UP y el corpus:

- paréntesis, loads, resolución, aridad y argumentos por posición;
- límite de **16 elementos por regla** y semántica de `(goal g v)`;
- goals extendidos de puntos/estado DUC (100–105 en Siege);
- enlace y posición legal de `this-any-*`;
- máquinas de estado sin entrada, duplicados, muros sin planificación;
- slots DUC y orden global de consumidores/rearmes de timers.

Ejecución desde la raíz:

```bash
python3 tools/lint_siege.py . siege
python3 -m unittest -v tools.test_lint_siege
```

Los dos comandos pasan. Tras una prueba en partida, vuelve a ejecutarlos antes
de commitear.

Ademas, el registro historico de errores del motor (ERR6002, ERR2005,
comparadores en `goal`, `UserPatchConst`...) con su solucion esta en
[`../Script_Errors.md`](../Script_Errors.md), y la documentacion completa
(hechos confirmados, prevencion, pipeline para agentes, IAs de referencia) en
[`../docs/README.md`](../docs/README.md).

## Limitaciones conocidas

- No existe una acción directa `repair`; la reparación automática sí puede
  configurarse con `sn-object-repair-level` en UP. Evidencia y búsquedas:
  [`docs/01` §11](../docs/01_Hechos_Del_Motor.md#11-lo-que-no-existe-comprobado).
- En partidas con varios enemigos, las rutinas DUC eligen al enemigo más
  cercano en cada pulso; la coordinación estratégica con `target-player`
  todavía debe evaluarse en juego.
- Dos partidas históricas confirmaron hasta `eco/build/train` y localizaron los
  antiguos errores `loom`/`aggressive`. Las correcciones DUC de esta auditoría
  y el combate completo aún no se han probado en runtime.
- `action-guard` con listas y `up-get-point position-enemy` siguen siendo los
  comportamientos prioritarios a observar. Plan detallado en
  [`docs/07` §11.3](../docs/07_Investigacion_AoC_UP15_y_Auditoria.md#113-siege).

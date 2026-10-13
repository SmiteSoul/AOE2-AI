# SIEGE — El Asediador Impenetrable

IA de asedio pura para **Age of Empires II: The Conquerors + UserPatch 1.5**.
Su unico objetivo es aplastar al enemigo con maquinaria de asedio: arietes
cargados de infanteria, evaluacion de objetivos inteligente, economia
obsesionada con el ejercito de asedio, unidades a distancia bien llevadas y
apertura de brechas en las murallas.

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
| `siege/const.per` | Goals (1-33, 40-46), timers y parametros ajustables (`ts-*`, `ram-full`...). |
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

## Orden de carga (importante para los timers)

`siege.per` carga los modulos en orden y **al final** rearma `t-eco` y
`t-micro`: `enable-timer` deja el timer sin marcar dentro del pase actual,
asi que las reglas de rearme deben ir *despues* de todos los consumidores
del timer. Si editas los modulos, no muevas esas reglas de sitio.

## Auditoria (lint) — obligatoria tras cualquier edicion

`tools/lint_siege.py` valida todo el proyecto con la gramatica real del
motor (medida sobre los 360k tokens de referencia de `reference/ais/`):

- parentesis balanceados y `(load ...)` que resuelven a ficheros reales;
- limite de **16 elementos por regla** (ERR6002; mi maximo: 15);
- `(goal g v)` solo compara igualdad (el hecho goal no admite <, >...);
- **argumentos validados por posicion de comando** contra el corpus
  (atrapa fallos como `(research loom)` — lo valido es `ri-loom`;
  y `(buy-commodity gold)` — el oro es la moneda, no un commodity:
  solo `food/wood/stone`);
- aridad exacta por comando, comandos desconocidos, goals/timers sin
  `defconst`, colisiones de constantes con `UserPatchConst`.

Ejecucion: `python3 tools/lint_siege.py` (desde la raiz del repo).
Tras un test en partida, vuelve a ejecutarlo antes de commitear.

Ademas, el registro historico de errores del motor (ERR6002, ERR2005,
comparadores en `goal`, `UserPatchConst`...) con su solucion esta en
[`../Script_Errors.md`](../Script_Errors.md), y la documentacion completa
(hechos confirmados, prevencion, pipeline para agentes, IAs de referencia) en
[`../docs/README.md`](../docs/README.md).

## Limitaciones conocidas

- El motor no permite ordenar reparaciones (`repair` no existe en el CPSB).
- Con varios enemigos, el DUC de brechas/fuego usa `this-any-enemy` (un enemigo
  concreto); el TSA se encarga del resto.
- Probada con dos partidas de prueba reales: la 1ª confirmó en runtime
  `UserPatchConst/const/init` (falló `eco.per` con `loom`); la 2ª confirmó
  además `eco/build/train` completos (falló `combat.per:103` con `aggressive`,
  ya corregido a `stance-aggressive`). Pendiente de prueba completa de
  `combat.per` y de los rearmes de timers.

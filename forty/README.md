# forty — IA defensiva mejorada (en preparación)

Versión mejorada de una IA defensiva existente, para **Age of Empires II:
The Conquerors + UserPatch 1.5**. Objetivo: una IA que priorice la supervivencia
(murallas, torres, unidades de defensa, boom económico) y contraataque cuando
tenga ventaja.

## Archivos previstos

| Archivo | Propósito |
|---|---|
| `forty.ai` | Archivo vacío que "engancha" la IA en el juego. |
| `forty.per` | Archivo principal: carga de módulos y constantes. |

Posible desglose en módulos (`forty-*.per`) si el script crece: muro/torres,
reacción a rush, boom, y transición a ataque.

## Referencia útil

- En `../reference/ais/` hay IAs defensivas/de arena que inspiran este trabajo:
  - `brutal2/` — IA de arena de alto nivel (fast imp, boom, murallas).
  - `barbarian-2.18/` — defensa reactiva y micro de élite.
  - `the-horde-3.9/` — enfoque defensivo clásico.
- `../reference/UserPatchConst.per` y `../reference/CPSB.pdf` para la sintaxis.

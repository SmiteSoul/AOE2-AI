#!/usr/bin/env python3
"""Linter para scripts .per de este repositorio (siege y futuras IAs).

Comprobaciones (inspiradas en los errores reales del motor):
  1. Parentesis balanceados y (load ...) que resuelven a ficheros reales.
  2. Ninguna regla supera 16 elementos (ERR6002 Rule too long). Se cuentan
     hechos, acciones y los operadores or/and/not, igual que Barbarian (su
     maximo real es 16).
  3. Toda regla tiene hechos, '=>' y acciones.
  4. (goal g v) SOLO compara igualdad (el hecho goal no admite <, >...).
  5. Espacios de nombres POR POSICION: cada argumento de (can-)research,
     (can-)train, (can-)build, unit-type-count*, up-find-*, commodities...
     debe existir en el corpus de referencia EN ESA MISMA POSICION de comando.
     (Atrapo fallos como '(research loom)' — 'loom' existe en el corpus pero
     no como argumento de research; el valido es 'ri-loom'.)
  6. Aridad exacta por comando (esquemas conocidos del CPSB/UserPatch).
  7. Comandos desconocidos (no aparecen en el corpus ni en UserPatchConst).
  8. goals/timers usados sin defconst.
  9. Commodity valido: food/wood/stone (oro NO se compra: es la moneda).

Uso:  python3 tools/lint_siege.py [raiz_del_repo]
"""
import re
import sys
import glob
import os
from collections import defaultdict

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REF = glob.glob(os.path.join(ROOT, 'reference/ais/**/*.per'), recursive=True)
SIEGE = [f for f in sorted(glob.glob(os.path.join(ROOT, 'siege/siege/*.per')))
         if 'UserPatchConst' not in f] + [os.path.join(ROOT, 'siege/siege.per')]
UPC_PATH = os.path.join(ROOT, 'siege/siege/UserPatchConst.per')
CPSB_TXT = '/tmp/cpsb.txt'  # opcional: texto extraido de reference/CPSB.pdf


def strip(src: str) -> str:
    out = []
    for ln in src.splitlines():
        res = ''; ins = False
        for ch in ln:
            if ch == '"':
                ins = not ins
            if ch == ';' and not ins:
                break
            res += ch
        out.append(res)
    return '\n'.join(out)


def paren_children(text):
    kids = []; depth = 0; start = None
    for idx, ch in enumerate(text):
        if ch == '(':
            if depth == 1:
                start = idx
            depth += 1
        elif ch == ')':
            depth -= 1
            if depth == 1 and start is not None:
                kids.append(text[start:idx + 1])
    return kids


def count_el(c):
    if c.startswith('(or') or c.startswith('(and') or c.startswith('(not'):
        return 1 + sum(count_el(x) for x in paren_children(c))
    return 1


def parse_rules(src):
    rules = []; i = 0
    while True:
        j = src.find('(defrule', i)
        if j < 0:
            break
        depth = 0; k = j
        while k < len(src):
            if src[k] == '(':
                depth += 1
            elif src[k] == ')':
                depth -= 1
                if depth == 0:
                    break
            k += 1
        rules.append(src[j:k + 1]); i = k + 1
    return rules


# ---- argumentos por posicion, extraidos del corpus de referencia ----
POS = {
    'train': r'\(train ([^\s()]+)',
    'can-train': r'\(can-train ([^\s()]+)',
    'build': r'\(build ([^\s()]+)',
    'can-build': r'\(can-build ([^\s()]+)',
    'research': r'\(research ([^\s()]+)',
    'can-research': r'\(can-research ([^\s()]+)',
    'can-research-with-escrow': r'\(can-research-with-escrow ([^\s()]+)',
    'research-completed': r'\(research-completed ([^\s()]+)',
    'unit-type-count': r'\(unit-type-count ([^\s()]+)',
    'unit-type-count-total': r'\(unit-type-count-total ([^\s()]+)',
    'building-type-count': r'\(building-type-count ([^\s()]+)',
    'building-type-count-total': r'\(building-type-count-total ([^\s()]+)',
    'players-building-type-count': r'\(players-building-type-count \S+ ([^\s()]+)',
    'players-unit-type-count': r'\(players-unit-type-count \S+ ([^\s()]+)',
    'up-find-local': r'\(up-find-local \S+: ([^\s()]+)',
    'up-find-remote': r'\(up-find-remote \S+: ([^\s()]+)',
    'set-strategic-number': r'\(set-strategic-number ([^\s()]+)',
    'strategic-number': r'\(strategic-number ([^\s()]+)',
    'up-modify-sn': r'\(up-modify-sn ([^\s()]+)',
    'set-escrow-percentage': r'\(set-escrow-percentage ([^\s()]+)',
    'release-escrow': r'\(release-escrow ([^\s()]+)',
    'sell-commodity': r'\(sell-commodity ([^\s()]+)',
    'buy-commodity': r'\(buy-commodity ([^\s()]+)',
    'can-sell-commodity': r'\(can-sell-commodity ([^\s()]+)',
    'can-buy-commodity': r'\(can-buy-commodity ([^\s()]+)',
    'up-remove-objects-od': r'\(up-remove-objects \S+ ([^\s()]+)',
    'up-target-objects-action': r'\(up-target-objects [^\s()]+ ([^\s()]+)',
    'up-target-objects-form': r'\(up-target-objects [^\s()]+ [^\s()]+ ([^\s()]+)',
    'up-target-objects-stance': r'\(up-target-objects [^\s()]+ [^\s()]+ [^\s()]+ ([^\s()]+)',
}
# sufijos -> comando base para comparar con el set del corpus
POS_BASE = {k: k.split('-action')[0].split('-form')[0].split('-stance')[0].split('-od')[0]
            for k in POS}

# aridad en TOKENS (los prefijos c:/g:/s: cuentan como token propio)
SCHEMA = {
    'or': 2, 'and': 2, 'not': 1, 'true': 0, 'disable-self': 0, 'attack-now': 0,
    'goal': 2, 'set-goal': 2, 'up-compare-goal': 3, 'up-modify-goal': 3,
    'timer-triggered': 1, 'enable-timer': 2, 'disable-timer': 1,
    'current-age': 2, 'game-time': 2, 'military-population': 2,
    'unit-type-count': 3, 'unit-type-count-total': 3,
    'building-type-count': 3, 'building-type-count-total': 3,
    'housing-headroom': 2, 'population-headroom': 2, 'idle-farm-count': 2,
    'wood-amount': 2, 'food-amount': 2, 'gold-amount': 2, 'stone-amount': 2,
    'dropsite-min-distance': 3, 'resource-found': 1,
    'players-building-type-count': 4, 'players-unit-type-count': 4,
    'strategic-number': 3, 'set-strategic-number': 2, 'up-modify-sn': 3,
    'can-build': 1, 'build': 1, 'can-train': 1, 'train': 1,
    'can-research': 1, 'research': 1, 'can-research-with-escrow': 1,
    'research-completed': 1,
    'set-escrow-percentage': 2, 'release-escrow': 1,
    'can-sell-commodity': 1, 'sell-commodity': 1,
    'can-buy-commodity': 1, 'buy-commodity': 1,
    'chat-to-all': 1,
    'town-under-attack': 0, 'enemy-buildings-in-town': 0,
    'stance-toward': 2,
    'up-full-reset-search': 0, 'up-find-local': 4, 'up-find-remote': 4,
    'up-remove-objects': 4, 'up-get-search-state': 1,
    'up-target-objects': 4, 'up-get-player-fact': 4,
    'up-set-target-object': 2, 'up-filter-include': 4,
}
AGES = {'feudal-age', 'castle-age', 'imperial-age', 'dark-age'}
COMMODITIES = {'food', 'wood', 'stone'}  # oro NO es commodity de mercado


def main():
    errors = []
    upc = open(UPC_PATH, encoding='utf-8', errors='replace').read()
    upc_names = {m.lower() for m in re.findall(r'\(defconst ([A-Za-z0-9_-]+)', upc)}

    corpus = '\n'.join(strip(open(f, encoding='utf-8', errors='replace').read()) for f in REF)
    corpus_ns = re.sub(r'"[^"]*"', '""', corpus)
    pos = defaultdict(set)
    cmd_names = set()
    for name, pat in POS.items():
        for m in re.findall(pat, corpus_ns):
            if not re.match(r'^-?\d+$', m):
                pos[name].add(m.lower())
    for m in re.findall(r'\(([a-z][a-z0-9-]*)', corpus_ns):
        cmd_names.add(m)
    ri_ok = {m.lower() for m in re.findall(r'\bri-[a-z0-9-]+', corpus_ns)}
    if os.path.exists(CPSB_TXT):
        cpsb = open(CPSB_TXT, encoding='utf-8', errors='replace').read()
        ri_ok |= {m.lower() for m in re.findall(r'\bri-[a-z0-9-]+', cpsb)}

    defconsts = set(); used_goals = set(); defined_goals = set()
    used_timers = set(); defined_timers = set()
    for f in SIEGE:
        s = strip(open(f, encoding='utf-8').read())
        for m in re.finditer(r'\(defconst ([A-Za-z0-9_-]+)', s):
            n = m.group(1).lower()
            defconsts.add(n)
            if n.startswith('gl-'):
                defined_goals.add(n)
            if n.startswith('t-'):
                defined_timers.add(n)

    for f in SIEGE:
        raw = open(f, encoding='utf-8').read()
        s = strip(raw)
        if s.count('(') != s.count(')'):
            errors.append(f'{f}: parentesis desbalanceados')
        for m in re.findall(r'\(load "([^"]+)"\)', raw):
            p = os.path.join(ROOT, 'siege', m.replace('\\', '/'))
            if not p.endswith('.per'):
                p += '.per'
            if not os.path.exists(p):
                errors.append(f'{f}: load inexistente {m}')
        s_ns = re.sub(r'"[^"]*"', '""', s)

        # comandos desconocidos
        for m in re.finditer(r'\(([a-z][a-z0-9-]*)', s_ns):
            c = m.group(1).lower()
            if c not in cmd_names and c not in SCHEMA and c not in defconsts and c != 'defrule':
                errors.append(f"{f}: comando desconocido '({c}'")

        # aridad
        for m in re.finditer(r'\(([a-z][a-z0-9-]*)((?:\s+[^\s()]+)*)\s*\)', s_ns):
            c = m.group(1).lower(); args = m.group(2).split()
            if c in SCHEMA and len(args) != SCHEMA[c]:
                errors.append(f'{f}: ({c} ...) con {len(args)} tokens, esperados {SCHEMA[c]}')

        # argumentos posicionales
        for name, pat in POS.items():
            base = POS_BASE[name]
            for v in re.findall(pat, s_ns):
                v = v.lower()
                if re.match(r'^-?\d+$', v) or v in defconsts or v in upc_names:
                    continue
                if base == 'research' or base == 'can-research' or base == 'can-research-with-escrow' or base == 'research-completed':
                    if v in ri_ok or v in AGES:
                        continue
                    errors.append(f"{f}: ({base} {v}) no es ri-* ni edad valida")
                    continue
                if base in ('buy-commodity', 'sell-commodity', 'can-buy-commodity', 'can-sell-commodity'):
                    if v not in COMMODITIES:
                        errors.append(f"{f}: ({base} {v}) commodity invalido (solo food/wood/stone)")
                        continue
                if v in pos[name]:
                    continue
                errors.append(f"{f}: [{name}] argumento '{v}' no visto en esa posicion en el corpus")

        # goals
        for m in re.finditer(r'\((?:set-goal|goal) ([A-Za-z0-9_-]+) ([^ )]+)', s_ns):
            used_goals.add(m.group(1).lower())
            if m.group(2) in ('>', '<', '>=', '<=', '!=') or m.group(2).startswith('g:'):
                errors.append(f'{f}: (goal ...) con comparacion ({m.group(0)})')
        for m in re.finditer(r'\((?:enable-timer|timer-triggered) ([A-Za-z0-9_-]+)', s_ns):
            used_timers.add(m.group(1).lower())

        # limites de reglas
        for r in parse_rules(s):
            if not re.search(r'=>', r):
                errors.append(f'{f}: regla sin => :: {r[:50]!r}')
                continue
            kids = paren_children(r)
            arrow = r.find('=>')
            if not [k for k in kids if r.find(k) < arrow]:
                errors.append(f'{f}: regla sin hechos :: {r[:50]!r}')
            if not [k for k in kids if r.find(k) > arrow]:
                errors.append(f'{f}: regla sin acciones :: {r[:50]!r}')
            n = sum(count_el(k) for k in kids)
            if n > 16:
                errors.append(f'{f}: regla con {n} elementos > 16 :: {r[:50]!r}')

    for g in sorted(used_goals - defined_goals):
        if not re.match(r'^\d+$', g):
            errors.append(f'goal usado sin defconst: {g}')
    for t in sorted(used_timers - defined_timers):
        if not re.match(r'^\d+$', t):
            errors.append(f'timer usado sin defconst: {t}')

    print('=== LINT .per ===')
    if errors:
        for e in errors:
            print('ERROR:', e)
        sys.exit(1)
    print('OK sin errores.')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Linter quirurgico para scripts .per de este repositorio (siege y futuras IAs).

Fundamento: en AoC/UserPatch TODO token que no sea numero, operador o cadena
debe RESOLVER a un identificador definido. Un token puede resolver por:

  (a) literal numerico;                       (p. ej. 3, -1)
  (b) defconst de la cadena de carga;         (UserPatchConst.per + defconsts
                                               del propio script en carga)
  (c) builtin del motor (CPSB);               (enemy, feudal-age,
                                               battering-ram-line, c:, g:...)

LO QUE NO RESUELVE = ERR2005 en juego. El error clasico: copiar del corpus
de referencia un alias que la IA ajena define y nosotros no
(p. ej. Barbarian define (defconst aggressive 0) y usa
(up-target-objects 0 action-default -1 aggressive); si tu script escribe
'aggressive' sin definirlo -> ERR2005).

Ademas valida:
  - parentesis balanceados y (load ...) que resuelven a ficheros reales;
  - limite de 16 elementos por regla (ERR6002; medido con el mismo recuento
    que Barbarian: hecho/accion = 1, or/and/not = 1 + hijos);
  - (goal g v) SOLO compara igualdad;
  - aridad exacta por comando (esquemas del CPSB/UserPatch);
  - espacios de nombres por POSICION de comando (research = ri-* o edad;
    commodities de mercado = food/wood/stone — el oro es la moneda);
  - goals/timers usados sin defconst; comandos desconocidos.

Uso:  python3 tools/lint_siege.py [raiz_del_repo]
"""
import re
import sys
import glob
import os
from collections import defaultdict

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJ = sys.argv[2] if len(sys.argv) > 2 else 'siege'

REF = glob.glob(os.path.join(ROOT, 'reference/ais/**/*.per'), recursive=True)
# Uso: python3 tools/lint_siege.py [raiz] [proyecto]
#   proyecto 'siege' (por defecto): paquete siege/siege/*.per + siege/siege.per
#   proyecto 'forty': forty/forty.per (unico archivo autocontenido)
if PROJ == 'forty':
    SIEGE = [os.path.join(ROOT, 'forty', 'forty.per')]
else:
    SIEGE = [f for f in sorted(glob.glob(os.path.join(ROOT, 'siege/siege/*.per')))
             if 'UserPatchConst' not in f] + [os.path.join(ROOT, 'siege/siege.per')]
UPC_PATH = os.path.join(ROOT, 'siege/siege/UserPatchConst.per')
CPSB_TXT = '/tmp/cpsb.txt'  # opcional: texto extraido de reference/CPSB.pdf

# --- tokens de sintaxis, no identificadores ---
OPS = {'==', '<', '>', '<=', '>=', '!=', '=', '+', '-', '*', '/'}
NUM_RE = re.compile(r'^-?\d+(\.\d+)?$')
PREFIX_RE = re.compile(r'^[cgs]:')  # c: 3 | g:== | g:= | s:+ ...


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


def tokens_of(list_text):
    """Tokens de una lista (sin parentesis), descartando cadenas."""
    inner = re.sub(r'"[^"]*"', '', list_text.strip()[1:-1])
    return [t for t in inner.split() if t]


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
    'stance-toward': r'\(stance-toward \S+ ([^\s()]+)',
}
POS_BASE = {k: re.sub(r'-(action|form|stance|od)$', '', k) for k in POS}

# aridad en TOKENS (los prefijos c:/g:/s: cuentan como token propio)
SCHEMA = {
    # --- defensa coordinada (UP-docs + corpus: up-retreat-now 22x, up-gather-inside 87x) ---
    'up-retreat-now': 0,
    'up-gather-inside': 4,
    # --- sistema de murallas (forty v1/v2 + corpus: build-wall 11x, build-gate 6x) ---
    'enable-wall-placement': 1,
    'can-build-wall': 2,
    'build-wall': 2,
    'can-build-gate': 1,
    'build-gate': 1,
    'wall-completed-percentage': 3,
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
    'up-set-target-object': 3, 'up-filter-include': 4,
}
AGES = {'feudal-age', 'castle-age', 'imperial-age', 'dark-age'}
COMMODITIES = {'food', 'wood', 'stone'}  # oro NO es commodity de mercado


def main():
    errors = []
    # ---- UserPatchConst: catalogo completo (activo + bloque comentado) ----
    # OJO documentado: el regex NO stripa comentarios A PROPOSITO. El bloque
    # extendido de SNs de UserPatchConst.per esta comentado '(defconst sn-...)'
    # porque UP 1.5 conoce esos nombres nativamente (runtime-proven); leerlos
    # tambien de los comentarios crea el catalogo explicito de nativos UP.
    upc = open(UPC_PATH, encoding='utf-8', errors='replace').read()
    upc_names = {m.lower() for m in re.findall(r'\(defconst ([A-Za-z0-9_-]+)', upc)}
    upc_active = {m.lower() for m in re.findall(r'\(defconst ([A-Za-z0-9_-]+)', strip(upc))}

    corpus_raw = '\n'.join(open(f, encoding='utf-8', errors='replace').read() for f in REF)
    corpus = strip(corpus_raw)
    corpus_ns = re.sub(r'"[^"]*"', '""', corpus)

    # ---- sets del corpus ----
    pos = defaultdict(set)
    cmd_names = set()
    for name, pat in POS.items():
        for m in re.findall(pat, corpus_ns):
            if not re.match(r'^-?\d+$', m):
                pos[name].add(m.lower())
    for m in re.findall(r'\(([a-z][a-z0-9-]*)', corpus_ns):
        cmd_names.add(m)

    # identificadores usados en el corpus vs definidos con defconst en el corpus
    corpus_used = {t.lower() for t in re.findall(r'\b[a-zA-Z][a-zA-Z0-9_-]*\b', corpus_ns)}
    corpus_defined = {m.lower() for m in re.findall(r'\(defconst ([A-Za-z0-9_-]+)', corpus_ns)}

    # builtin del motor = usado en el corpus pero NUNCA definido por el corpus,
    # o presente en UserPatchConst, o keyword curado del motor.
    # OJO: las palabras de la PROSA del CPSB no valen como prueba de builtin
    # (de ahi salio el bug 'aggressive': la palabra aparece en el texto del
    # CPSB como termino en ingles, pero NO es identificador valido en
    # up-target-objects; los alias del corpus que alguien define con defconst
    # quedan excluidos de builtin aunque aparezcan en el CPSB).
    cpsb_ids = set()
    cpsb_text = ''
    if os.path.exists(CPSB_TXT):
        cpsb_text = open(CPSB_TXT, encoding='utf-8', errors='replace').read()
        cpsb_ids = {t.lower() for t in re.findall(r'\b[a-zA-Z][a-zA-Z0-9_-]+\b', cpsb_text)}
    CURATED = {
        # operadores y prefijos de operando (aunque se filtran antes)
        'c', 'g', 's',
        # player-facts / constantes de jugador (engine + UP)
        'my-player-number', 'this-any-enemy', 'this-any-ally', 'this-any-computer',
        'any-ally', 'any-enemy', 'any-computer', 'any-neutral',
        'target-player', 'focus-player', 'my-target-object', 'target-object',
        'commodity-selling-price', 'commodity-buying-price',
        # stance-toward / set-stance
        'ally', 'neutral', 'enemy',
        # edades, recursos, tiempos
        'dark-age', 'feudal-age', 'castle-age', 'imperial-age', 'post-imperial-age',
        'food', 'wood', 'gold', 'stone', 'population-cap', 'mill',
        # sn-especiales comunes (por si acaso)
        'town-center', 'farm', 'mining-camp', 'lumber-camp', 'dock', 'monastery',
        # edificios nativos del motor (CPSB los usa en sus ejemplos de codigo).
        # OJO: que una IA del corpus los 'defconst-e' no los convierte en alias
        # (The Horde redefine (defconst castle 82); castle sigue siendo builtin).
        'castle', 'barracks', 'archery-range', 'stable', 'siege-workshop',
        'market', 'blacksmith', 'house', 'watch-tower', 'guard-tower',
        'bombard-tower', 'wonder', 'outpost', 'outpost', 'gate', 'wall',
        'fortified-wall', 'farm', 'town-center',
    }
    BUILTIN = (corpus_used - corpus_defined) | upc_names | (cpsb_ids - corpus_defined) | CURATED

    # alias locales del corpus (definidos por alguna IA pero no builtin):
    # NUNCA validos en siege sin defconst propio. Clase del bug 'aggressive'.
    ALIAS_CORPUS = corpus_defined - upc_names

    ri_ok = {m.lower() for m in re.findall(r'\bri-[a-z0-9-]+', corpus_ns)} | \
            {m.lower() for m in re.findall(r'\bri-[a-z0-9-]+', cpsb_text)}

    # ---- cadena de carga de siege ----
    defconsts = set(); used_goals = set(); defined_goals = set()
    used_timers = set(); defined_timers = set()
    const_vals = {}   # nombre -> (valor, fichero) para ERR2012
    for f in SIEGE:
        s = strip(open(f, encoding='utf-8').read())
        for m in re.finditer(r'\(defconst ([A-Za-z0-9_-]+) ([^();\s]+)', s):
            n = m.group(1).lower(); v = m.group(2)
            if n in const_vals and const_vals[n][0] != v:
                errors.append(f"{f}: ERR2012 {n} redefinido con distinto valor "
                              f"({const_vals[n][0]} en {const_vals[n][1]} -> {v})")
            const_vals.setdefault(n, (v, f))
            defconsts.add(n)
            if n.startswith('gl-'):
                defined_goals.add(n)
            if n.startswith('t-'):
                defined_timers.add(n)
    CHAIN = defconsts | upc_active

    def resolvable(tok: str) -> bool:
        t = tok.lower()
        return t in CHAIN or t in BUILTIN or t in cmd_names

    for f in SIEGE:
        raw = open(f, encoding='utf-8').read()
        s = strip(raw)
        # ASCII estricto: simbolos ocultos de editor = errores in-game irresolubles
        bad = sorted({c for c in raw if ord(c) > 127})
        if bad:
            errors.append(f'{f}: caracteres no-ASCII {bad!r} (ASCII estricto obligatorio)')
        if s.count('(') != s.count(')'):
            errors.append(f'{f}: parentesis desbalanceados')
        for m in re.findall(r'\(load "([^"]+)"\)', raw):
            p = os.path.join(ROOT, 'siege', m.replace('\\', '/'))
            if not p.endswith('.per'):
                p += '.per'
            if not os.path.exists(p):
                errors.append(f'{f}: load inexistente {m}')
        s_ns = re.sub(r'"[^"]*"', '""', s)

        # --- comandos desconocidos ---
        for m in re.finditer(r'\(([a-z][a-z0-9-]*)', s_ns):
            c = m.group(1).lower()
            if c not in cmd_names and c not in SCHEMA and c not in defconsts and c != 'defrule':
                errors.append(f"{f}: comando desconocido '({c}'")

        # --- aridad ---
        for m in re.finditer(r'\(([a-z][a-z0-9-]*)((?:\s+[^\s()]+)*)\s*\)', s_ns):
            c = m.group(1).lower(); args = m.group(2).split()
            if c in SCHEMA and len(args) != SCHEMA[c]:
                errors.append(f'{f}: ({c} ...) con {len(args)} tokens, esperados {SCHEMA[c]}')

        # --- argumentos posicionales ---
        for name, pat in POS.items():
            base = POS_BASE[name]
            for v in re.findall(pat, s_ns):
                v = v.lower()
                if NUM_RE.match(v) or v in defconsts or v in upc_names:
                    continue
                if base in ('research', 'can-research', 'can-research-with-escrow', 'research-completed'):
                    # my-unique-*: constantes de sistema CPSB, verificadas en corpus
                    # ((research my-unique-research) 114x, (research my-unique-unit-upgrade) 56x)
                    SYSTEM_RESEARCH = {'my-unique-research', 'my-unique-unit-upgrade'}
                    if v in ri_ok or v in AGES or v in SYSTEM_RESEARCH:
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

        # --- REGLA DE RESOLUCION: todo token identificador debe resolver ---
        def check_list(lst, where):
            head = lst[1:].lstrip()
            if head.startswith('or ') or head.startswith('and ') or head.startswith('not ') \
               or head.startswith('or)') or head.startswith('and)') or head.startswith('not)'):
                for ch in paren_children(lst):
                    check_list(ch, where)
                return
            if head.startswith('load '):
                return
            toks = []
            for t in tokens_of(lst):
                if PREFIX_RE.match(t):          # c: | g:== | s:+ ...
                    continue
                toks.append(t)
            skip = 1 if toks else 0             # nombre de comando
            if toks and toks[0] == 'defconst':
                skip = 2                        # defconst + nombre propio
            for t in toks[skip:]:
                if t in ('c:', 'g:', 's:') or t in OPS or t == '=>':
                    continue
                if NUM_RE.match(t):
                    continue
                if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', t):
                    continue  # lo cubre aridad/otros checks
                if resolvable(t):
                    continue
                extra = ''
                if t in ALIAS_CORPUS:
                    extra = (f" — es un alias LOCAL de alguna IA de referencia"
                             f" (defconst propio alli); define tu (defconst {t} N)"
                             f" o usa la constante nativa equivalente")
                errors.append(f"{where}: identificador no resoluble '{t}'{extra}")

        for r in parse_rules(s):
            for kid in paren_children(r):
                check_list(kid, f)
        for m in re.finditer(r'\(defconst ([A-Za-z0-9_-]+) ((?:[^()]+))\)', s_ns):
            if not NUM_RE.match(m.group(2).strip()) and not resolvable(m.group(2).strip()):
                errors.append(f"{f}: (defconst {m.group(1)} {m.group(2).strip()}) valor no resoluble")

        # --- goals ---
        for m in re.finditer(r'\((?:set-goal|goal) ([A-Za-z0-9_-]+) ([^ )]+)', s_ns):
            used_goals.add(m.group(1).lower())
            if m.group(2) in ('>', '<', '>=', '<=', '!=') or m.group(2).startswith('g:'):
                errors.append(f'{f}: (goal ...) con comparacion ({m.group(0)})')
        for m in re.finditer(r'\((?:enable-timer|timer-triggered) ([A-Za-z0-9_-]+)', s_ns):
            used_timers.add(m.group(1).lower())

        # --- limites de reglas ---
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

    # ---- dominios de slots (semantica CPSB/UserPatch) y invariantes de timer ----
    ACTIONS = {'action-default', 'action-move', 'action-patrol', 'action-guard',
               'action-follow', 'action-stop', 'action-ground', 'action-garrison',
               'action-delete', 'action-unload', 'action-train', 'action-gather',
               'action-lock', 'action-work', 'action-ungarrison', 'action-drop-relic',
               'action-pack', 'action-unpack', 'action-none'}
    FORMS = {'formation-line', 'formation-box', 'formation-stagger', 'formation-flank'}
    STANCES = {'stance-aggressive', 'stance-defensive', 'stance-stand-ground', 'stance-no-attack'}

    def rules_seq():
        """(fichero, indice_global, texto_regla) en orden global de carga."""
        pos = 0
        for f in SIEGE:
            s = strip(open(f, encoding='utf-8').read())
            for r in parse_rules(s):
                pos += 1
                yield f, pos, r

    trig, enab = defaultdict(list), defaultdict(list)
    for f, pos, r in rules_seq():
        s = re.sub(r'"[^"]*"', '""', r)
        for m in re.finditer(r'\(up-target-objects ([^()\s]+) ([^()\s]+) ([^()\s]+) ([^()\s]+)', s):
            a, b, c, d = m.groups()
            if a not in ('0', '1'):
                errors.append(f'{f}: up-target-objects slot1={a} (esperado 0|1)')
            if b not in ACTIONS and b != '-1':
                errors.append(f'{f}: up-target-objects accion invalida {b}')
            if c not in FORMS and c != '-1':
                errors.append(f'{f}: up-target-objects formacion invalida {c}')
            if d not in STANCES and d != '-1':
                errors.append(f'{f}: up-target-objects stance invalida {d}')
        for m in re.finditer(r'\(up-remove-objects ([^()\s]+) ([^()\s]+) ([^()\s]+)', s):
            a, b, c = m.groups()
            if a not in ('search-local', 'search-remote'):
                errors.append(f'{f}: up-remove-objects slot1={a}')
            if not b.startswith('object-data'):
                errors.append(f'{f}: up-remove-objects slot2={b} (esperado object-data-*)')
            if c not in ('==', '<', '>', '<=', '>=', '!='):
                errors.append(f'{f}: up-remove-objects op={c}')
        for m in re.finditer(r'\(enable-timer ([^()\s]+) ([^()\s]+)', s):
            if not re.match(r'^\d+$', m.group(2)) or int(m.group(2)) <= 0:
                errors.append(f'{f}: enable-timer {m.group(1)} segundos invalidos {m.group(2)}')
        for m in re.finditer(r'\(up-find-(?:local|remote) [^()\s]+: ([^()\s]+) [^()\s]+: ([^()\s]+)', s):
            if not re.match(r'^-?\d+$', m.group(2)) or int(m.group(2)) <= 0:
                errors.append(f'{f}: up-find-* cuenta invalida {m.group(2)}')
        try:
            for m in re.finditer(r'\(set-escrow-percentage ([^()\s]+) ([^()\s]+)', s):
                if not 0 <= int(m.group(2)) <= 100:
                    errors.append(f'{f}: escrow {m.group(1)}={m.group(2)} fuera de 0-100')
        except ValueError:
            pass
        # invariantes de timer: los consumidores con TRABAJO no pueden ir
        # detras de un rearme no-init (el enable limpia el trigger del pase).
        # Los despachadores cuyo unico action es enable-timer estan exentos.
        ds = '(disable-self)' in r
        for m in re.finditer(r'\(timer-triggered ([^()\s]+)\)', s):
            t = m.group(1)
            trig[t].append((pos, f, ds))
            actions_part = s.split('=>', 1)[-1] if '=>' in s else ''
            work = [a for a in paren_children(actions_part.strip() and actions_part)
                    if not a.startswith('(enable-timer')]
            has_work = bool(re.search(r'\((?!enable-timer)[a-z]', actions_part))
            trig[t][-1] = (pos, f, ds, has_work)
        for m in re.finditer(r'\(enable-timer ([^()\s]+)', s):
            tt = m.group(1)
            facts_part = s.split('=>', 1)[0] if '=>' in s else s
            # Ladrón de trigger = rearme en la MISMA regla que consume el timer,
            # o enable en regla (true) sin disable-self (se ejecuta cada pase).
            # Un enable ligado a un evento puntual (inicio de oleada...) NO roba.
            stealer = (f'(timer-triggered {tt})' in s) or ('(true)' in facts_part and not ds)
            enab[tt].append((pos, f, ds, stealer))
    for t in sorted(set(trig) | set(enab)):
        if trig[t] and not enab[t]:
            errors.append(f'timer {t}: timer-triggered sin enable-timer en todo el script (nunca rearma)')
        for pos, f, ds, has_work in trig[t]:
            if not has_work:
                continue
            prev = [p for p, ff, dds, st in enab[t] if p < pos and st]
            if prev:
                errors.append(f'timer {t}: consumidor con trabajo en {f}@regla {pos} DESPUES de '
                              f'rearme que roba el trigger @{prev[-1]} — no verá el timer en el pase')

    print('=== LINT .per (resolucion + gramatica) ===')
    if errors:
        for e in errors:
            print('ERROR:', e)
        sys.exit(1)
    print('OK sin errores.')


if __name__ == '__main__':
    main()

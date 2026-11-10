"""Kinzi U+1064 micro-rule (LIVE in Block7 when KINZI_ENABLED). residual down accept; medial or AA host.
Zawgyi kinzi U+1064 is drawn AFTER its host cluster: C M* V* U+1064  ->  U+1004 U+103A U+1039 C M* V*
e.g. Cisco L159 သစ်ွၤာ (101E 1001 103D 1064 102C) -> သင်္စွာ ; Social L2251 patterns similarly.
Accept per match iff residual ZG-ext strictly drops AND no new ZG-ext char AND result has no
orphan U+1039 (1039 must be followed by a consonant).

Noman tighten 2026-10-30: accept only if host has medial U+103B–U+103E OR U+102C/U+102B (ာ/ါ)
in the V group — reject bare C+ိ/ီ±other short V +1064 (FP အီၤ→င်္အီ, တီၤ→င်္တီ).
"""
import re
KINZI_ENABLED = True
ZG_EXT = re.compile('[\u1033\u1034\u105A\u1060-\u109F]')
C = '\u1000-\u1021'
RX = re.compile(f'([{C}])([\u103b-\u103e]*)([\u102b-\u1032\u1036]*)\u1064')
BAD = re.compile(f'\u1039(?![{C}])')
AA = re.compile('[\u102b\u102c]')  # ါ/ာ required if no medial


def residual(t):
    return len(ZG_EXT.findall(t))


def _host_ok(medials, vowels):
    """Noman: need medial OR ာ/ါ in V; reject bare C+short-V+1064."""
    if medials:
        return True
    return bool(AA.search(vowels or ''))


def fix_line(u, log=None):
    pos, n = 0, 0
    while True:
        m = RX.search(u, pos)
        if not m:
            return u, n
        if not _host_ok(m.group(2), m.group(3)):
            pos = m.start() + 1
            continue
        c = u[:m.start()] + '\u1004\u103a\u1039' + m.group(1) + m.group(2) + m.group(3) + u[m.end():]
        new = set(ZG_EXT.findall(c)) - set(ZG_EXT.findall(u))
        if residual(c) < residual(u) and not new and len(BAD.findall(c)) <= len(BAD.findall(u)):
            if log is not None:
                log.append((u, c))
            u = c
            n += 1
            # stay at same pos to allow overlapping later matches after rewrite
            continue
        pos = m.start() + 1


def fix_text(t, log=None):
    L, n = [], 0
    for u in t.split('\n'):
        o, x = fix_line(u, log)
        L.append(o)
        n += x
    return '\n'.join(L), n

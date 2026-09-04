#!/usr/bin/env python3
"""Gera stats-dark.svg e stats-light.svg: o card de metricas do README.

Uso:  GITHUB_TOKEN=<token> python .github/scripts/gen_stats.py

Sem token o script desenha com dados de exemplo e avisa -- serve pra conferir
o layout offline. Quem roda pra valer e o .github/workflows/stats.yml, todo dia.

A paleta vem do gen_hero.py de proposito: as cores ficam definidas num lugar so.
"""

import json
import os
import sys
import urllib.request
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_hero import THEMES

USER = "GusGgk"
W, H = 1180, 420
BAR = 46                       # barra de titulo, igual a do hero
PAD = 36                       # margem lateral
TILE_Y, TILE_H, TILE_GAP = 84, 120, 16
LANG_N = 5                     # quantas linguagens listar
LANG_Y, LANG_STEP = 268, 28
TRACK_X, TRACK_W = 232, 780    # trilho das barras de linguagem

TITLE = "gukumagai@gmail.com - % ./gustavo.sh --stats"

# (chave, rotulo, legenda)
TILES = [
    ("contributions", "CONTRIBUIÇÕES", "últimos 12 meses"),
    ("streak",        "STREAK ATUAL",            "dias seguidos"),
    ("stars",         "STARS",                   "nos meus repos"),
    ("repos",         "REPOSITÓRIOS",       "públicos"),
]

QUERY = """
query($login:String!){
  user(login:$login){
    repositories(first:100, ownerAffiliations:OWNER, isFork:false){
      totalCount
      nodes{
        stargazerCount
        languages(first:10, orderBy:{field:SIZE, direction:DESC}){
          edges{ size node{ name color } }
        }
      }
    }
    contributionsCollection{
      contributionCalendar{
        totalContributions
        weeks{ contributionDays{ date contributionCount } }
      }
    }
  }
}
"""

# usado quando nao ha token: numeros plausiveis so pra validar o desenho
SAMPLE = dict(
    contributions=742, streak=7, stars=8, repos=24,
    langs=[("Python", 34.2, "#3572A5"), ("JavaScript", 22.8, "#f1e05a"),
           ("HTML", 15.1, "#e34c26"), ("Java", 14.6, "#b07219"),
           ("TypeScript", 8.3, "#3178c6")],
)


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fetch(token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {token}",
                 "Content-Type": "application/json",
                 "User-Agent": USER},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if payload.get("errors"):
        raise RuntimeError(f"GraphQL: {payload['errors']}")
    return payload["data"]["user"]


def current_streak(days):
    """Dias consecutivos com contribuicao, terminando hoje ou ontem.

    Se hoje ainda esta zerado a contagem comeca em ontem -- senao o streak
    zeraria toda madrugada. O calendario do GitHub cobre so 12 meses, entao
    uma sequencia mais longa que isso aparece truncada em 365.
    """
    counts = {d["date"]: d["contributionCount"] for d in days}
    day = date.today()
    if counts.get(day.isoformat(), 0) == 0:
        day -= timedelta(days=1)
    n = 0
    while counts.get(day.isoformat(), 0) > 0:
        n += 1
        day -= timedelta(days=1)
    return n


def summarize(user):
    repos = user["repositories"]
    sizes, colors = {}, {}
    for node in repos["nodes"]:
        for edge in node["languages"]["edges"]:
            name = edge["node"]["name"]
            sizes[name] = sizes.get(name, 0) + edge["size"]
            colors[name] = edge["node"]["color"]
    total = sum(sizes.values()) or 1
    top = sorted(sizes.items(), key=lambda kv: -kv[1])[:LANG_N]

    cal = user["contributionsCollection"]["contributionCalendar"]
    days = [d for week in cal["weeks"] for d in week["contributionDays"]]

    return dict(
        contributions=cal["totalContributions"],
        streak=current_streak(days),
        stars=sum(n["stargazerCount"] for n in repos["nodes"]),
        repos=repos["totalCount"],
        langs=[(name, size / total * 100, colors.get(name)) for name, size in top],
    )


def tile_svg(t, i, value, label, sub, tile_w):
    x = PAD + i * (tile_w + TILE_GAP)
    cx = x + tile_w // 2
    delay = 0.35 + i * 0.12
    return (
        f'<g opacity="0">'
        f'<animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="{delay:.2f}s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" values="0 10;0 0" '
        f'dur="0.5s" begin="{delay:.2f}s" fill="freeze" calcMode="spline" keyTimes="0;1" '
        f'keySplines=".3 0 .2 1"/>'
        f'<rect x="{x}" y="{TILE_Y}" width="{tile_w}" height="{TILE_H}" rx="10" '
        f'fill="{t["screen"]}" stroke="{t["frame"]}"/>'
        f'<text x="{cx}" y="{TILE_Y + 58}" text-anchor="middle" font-size="40" font-weight="700" '
        f'fill="url(#num)">{esc(value)}</text>'
        f'<text x="{cx}" y="{TILE_Y + 84}" text-anchor="middle" font-size="11" letter-spacing="2" '
        f'fill="{t["screen_fg"]}">{label}</text>'
        f'<text x="{cx}" y="{TILE_Y + 104}" text-anchor="middle" font-size="10" '
        f'fill="{t["screen_dim"]}">{sub}</text>'
        f'</g>'
    )


def lang_svg(t, i, name, pct, color):
    y = LANG_Y + i * LANG_STEP
    width = max(4, round(TRACK_W * pct / 100))
    delay = 0.9 + i * 0.1
    fill = color or t["node"]
    return (
        f'<g opacity="0">'
        f'<animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{delay:.2f}s" fill="freeze"/>'
        f'<text x="{PAD}" y="{y + 4}" font-size="13" fill="{t["text"]}">{esc(name)}</text>'
        f'<rect x="{TRACK_X}" y="{y - 5}" width="{TRACK_W}" height="9" rx="4.5" '
        f'fill="{t["track"]}"/>'
        f'<rect x="{TRACK_X}" y="{y - 5}" width="0" height="9" rx="4.5" fill="{fill}">'
        f'<animate attributeName="width" from="0" to="{width}" dur="1.1s" begin="{delay + 0.1:.2f}s" '
        f'fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".2 0 .1 1"/></rect>'
        f'<text x="{W - PAD}" y="{y + 4}" text-anchor="end" font-size="12" font-weight="600" '
        f'fill="{t["muted"]}">{pct:.1f}%</text>'
        f'</g>'
    )


def build(t, s, stamp):
    tile_w = (W - 2 * PAD - 3 * TILE_GAP) // 4
    tiles = "\n".join(tile_svg(t, i, s[key], label, sub, tile_w)
                      for i, (key, label, sub) in enumerate(TILES))
    langs = "\n".join(lang_svg(t, i, name, pct, color)
                      for i, (name, pct, color) in enumerate(s["langs"]))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace" role="img" aria-label="Estatisticas do GitHub de {USER}">
<defs>
<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
<stop offset="0" stop-color="#7C4DFF"><animate attributeName="stop-color" values="#7C4DFF;#48BFE3;#3FB950;#7C4DFF" dur="10s" repeatCount="indefinite"/></stop>
<stop offset="0.5" stop-color="#48BFE3"><animate attributeName="stop-color" values="#48BFE3;#3FB950;#7C4DFF;#48BFE3" dur="10s" repeatCount="indefinite"/></stop>
<stop offset="1" stop-color="#3FB950"><animate attributeName="stop-color" values="#3FB950;#7C4DFF;#48BFE3;#3FB950" dur="10s" repeatCount="indefinite"/></stop>
</linearGradient>
<linearGradient id="num" x1="0" y1="{TILE_Y}" x2="0" y2="{TILE_Y + 70}" gradientUnits="userSpaceOnUse">
<stop offset="0" stop-color="{t['ink'][0]}"/><stop offset="1" stop-color="{t['ink'][2]}"/>
</linearGradient>
<linearGradient id="panelGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t['panel_a']}"/><stop offset="1" stop-color="{t['panel_b']}"/></linearGradient>
<filter id="glow8" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="8"/></filter>
<filter id="txtGlow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="0.9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="winClip"><rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="18"/></clipPath>
</defs>
<rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="18" fill="{t['bg']}"/>
<g clip-path="url(#winClip)">
<rect x="2" y="2" width="{W - 4}" height="{H - 4}" fill="url(#panelGrad)"/>
<rect x="2" y="2" width="{W - 4}" height="{BAR}" fill="{t['chrome']}"/>
<line x1="2" y1="{BAR + 2}" x2="{W - 2}" y2="{BAR + 2}" stroke="{t['hair']}"/>
<circle cx="30" cy="25" r="5.5" fill="#ff5f56"/>
<circle cx="50" cy="25" r="5.5" fill="#ffbd2e"/>
<circle cx="70" cy="25" r="5.5" fill="#27c93f"/>
<text x="{W // 2}" y="29" text-anchor="middle" font-size="12" fill="{t['muted']}">{TITLE}</text>
<text x="{PAD}" y="74" font-size="10" letter-spacing="3" fill="{t['dim']}">METRICS</text>
<text x="{W - PAD}" y="74" text-anchor="end" font-size="10" fill="{t['dim']}">sync {stamp}</text>
{tiles}
<text x="{PAD}" y="238" font-size="13" letter-spacing="2" fill="{t['key']}" filter="url(#txtGlow)">LANGUAGES</text>
<line x1="{PAD + 106}" y1="234" x2="{W - PAD}" y2="234" stroke="{t['hair']}"/>
{langs}
</g>
<rect x="3" y="3" width="{W - 6}" height="{H - 6}" rx="17" fill="none" stroke="url(#accent)" stroke-width="3" opacity="0.55" filter="url(#glow8)"/>
<rect x="3" y="3" width="{W - 6}" height="{H - 6}" rx="17" fill="none" stroke="url(#accent)" stroke-width="1.6"/>
</svg>
'''


if __name__ == "__main__":
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("STATS_TOKEN")
    if token:
        stats = summarize(fetch(token))
    else:
        stats = SAMPLE
        print("AVISO: sem GITHUB_TOKEN -- desenhando com dados de exemplo", file=sys.stderr)

    stamp = date.today().isoformat()
    root = Path(__file__).resolve().parents[2]
    for name, theme in (("dark", THEMES["dark"]), ("light", THEMES["light"])):
        target = root / f"stats-{name}.svg"
        target.write_text(build(theme, stats, stamp), encoding="utf-8")
        print(f"gerado: {target.name} ({target.stat().st_size / 1024:.1f} KB)")
    print(f"  contribuicoes={stats['contributions']} streak={stats['streak']} "
          f"stars={stats['stars']} repos={stats['repos']}")

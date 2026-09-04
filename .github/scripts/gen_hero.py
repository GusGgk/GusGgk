#!/usr/bin/env python3
"""Gera hero-dark.svg e hero-light.svg: o banner animado no topo do README.

Uso:  python .github/scripts/gen_hero.py

Para mudar o conteudo, edite ROWS / TITLE / FOOTER abaixo e rode o script.
Os dois temas saem da mesma estrutura, so muda a paleta.
"""

from pathlib import Path

W, H = 1180, 610
BAR = 46                                # altura da barra de titulo
LX, LY, LW, LH = 36, 84, 400, 492       # painel esquerdo (VISUAL.MAP)
RX, RW = 470, 655                       # painel direito (SYSTEM.INFO)
CHARS = 78                              # largura da linha em caracteres monoespacados

TITLE = "gukumagai@gmail.com - % ./gustavo.sh --live"
NAME = "Gustavo Giacoia Kumagai"
FOOTER = "&#9656; Mais sobre mim e meus projetos abaixo &#8595; "

# (rotulo, valor); None abre um respiro de secao; ("--", "Titulo") vira um divisor
ROWS = [
    ("Subject",        "Gustavo Giacoia Kumagai"),
    ("Role",           "Software Engineer"),
    ("Focus",          "AI - Automation - Fullstack"),
    ("Education",      "Eng. de Software @ PUCPR"),
    ("Current",        "Tecnologia B2B @ Vivo (Telefônica Brasil)"),
    ("Previous",       "APIs, Chatbots &amp; IA @ Zenvia"),
    None,
    ("Core.Lang",      "Python, Java, TypeScript, PHP"),
    ("Core.Frontend",  "React, Next.js"),
    ("Core.Backend",   "Node.js, Laravel, Django"),
    ("Core.Data",      "MySQL, Supabase"),
    ("Core.Infra",     "Docker, Google Cloud, Vercel"),
    None,
    ("--", "Contact"),
    ("Grid.Mail",      "gukumagai@gmail.com"),
    ("Grid.LinkedIn",  "gustavo-giacoia-kumagai"),
    ("Grid.GitHub",    "@GusGgk"),
    ("Grid.Instagram", "@_gustavo.gk"),
    ("Grid.Portfolio", "https://gusgk.com.br"),
]

# grafo do painel esquerdo: colunas de nos (x, [y...])
LAYERS = [
    (110, [200, 320, 440]),
    (236, [170, 270, 370, 470]),
    (362, [260, 400]),
]
COL_LABELS = ["INPUT", "PROCESS", "IMPACT"]

# painel esquerdo: "portrait" (foto em pontinhos) ou "graph" (grafo animado)
LEFT_PANEL = "portrait"

PHOTO = ".github/assets/photo.jpg"
CROP = (573, 10, 1467, 960)    # recorte da foto original em px: (x0, y0, x1, y1)
PX, PY, PW, PH = 44, 92, 384, 408   # area do retrato dentro do painel
GRID_W = 224                        # colunas de pontinhos (linhas saem da proporcao)
BANDS = 16                          # faixas do reveal progressivo
LEVELS = 0.85, 1.2                  # (gamma, ganho) antes do dither
VIGNETTE = 1.0, 1.0, 0.55, 1.05     # (raio x, raio y, inicio, fim) do ovalo de recorte
HIGHLIGHT = 0.94, 1.4               # (limiar, forca): doma o nucleo estourado do
                                    # painel de luz que aparece atras dele na foto

THEMES = {
    "dark": dict(
        out="hero-dark.svg",
        bg="#08090F", panel_a="#0D1117", panel_b="#111827",
        chrome="#0B0E17",
        hair="rgba(255,255,255,0.10)",
        frame="rgba(72,191,227,0.35)",
        dim="#475569", muted="#94A3B8", text="#F8FAFC",
        key="#48BFE3", ldr="rgba(148,163,184,0.35)",
        chip_bg="#3D2670", chip_fg="#E9D5FF",
        node="#7C4DFF", spark="#48BFE3", edge="rgba(124,77,255,0.45)",
        ink=("#48BFE3", "#A78BFA", "#7C4DFF"),
        grid="#94A3B8", live="#F87171",
        # a "tela" do painel esquerdo e escura nos dois temas: o retrato em
        # pontinhos so funciona como luz sobre fundo escuro
        screen="#0A0E1A", screen_fg="#94A3B8", screen_dim="#475569",
        screen_hair="rgba(255,255,255,0.10)",
    ),
    "light": dict(
        out="hero-light.svg",
        bg="#FFFFFF", panel_a="#F1F5F9", panel_b="#E6EBF3",
        chrome="#E9EEF5",
        hair="rgba(15,23,42,0.10)",
        frame="rgba(8,145,178,0.55)",
        dim="#64748B", muted="#475569", text="#0F172A",
        key="#0891B2", ldr="rgba(71,85,105,0.35)",
        chip_bg="#EDE9FE", chip_fg="#5B21B6",
        node="#7C4DFF", spark="#22D3EE", edge="rgba(124,77,255,0.45)",
        ink=("#22D3EE", "#A78BFA", "#7C4DFF"),
        grid="#94A3B8", live="#DC2626",
        screen="#0D1220", screen_fg="#94A3B8", screen_dim="#64748B",
        screen_hair="rgba(255,255,255,0.10)",
    ),
}


def visible_len(s):
    """Comprimento em caracteres, ignorando entidades XML como &amp;."""
    return len(s.replace("&amp;", "&").replace("&#183;", "."))


def leader(label, value, ch="."):
    """Quantos pontinhos cabem entre o rotulo e o valor."""
    return ch * max(3, CHARS - visible_len(label) - visible_len(value) - 2)


def row_svg(t, y, label, value, delay):
    """Uma linha 'Rotulo ....... Valor', com fade + slide na entrada."""
    return (
        f'<g opacity="0">'
        f'<animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{delay:.2f}s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" values="-8 0;0 0" '
        f'dur="0.4s" begin="{delay:.2f}s" fill="freeze"/>'
        f'<text x="{RX}" y="{y}" font-size="14" textLength="{RW}" lengthAdjust="spacingAndGlyphs" xml:space="preserve">'
        f'<tspan fill="{t["key"]}">{label} </tspan>'
        f'<tspan fill="{t["ldr"]}">{leader(label, value)}</tspan>'
        f'<tspan fill="{t["text"]}" font-weight="600"> {value}</tspan>'
        f'</text></g>'
    )


def divider_svg(t, y, title, delay):
    return (
        f'<g opacity="0">'
        f'<animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{delay:.2f}s" fill="freeze"/>'
        f'<text x="{RX}" y="{y}" font-size="14" textLength="{RW}" lengthAdjust="spacingAndGlyphs" xml:space="preserve">'
        f'<tspan fill="{t["muted"]}">- {title} </tspan>'
        f'<tspan fill="{t["ldr"]}">{leader("- " + title, "", "-")}</tspan>'
        f'</text></g>'
    )


def right_panel(t):
    out = []
    # cabecalho SYSTEM.INFO + indicador LIVE piscando
    out.append(f'<text x="{RX}" y="106" font-size="13" letter-spacing="2" fill="{t["key"]}" '
               f'filter="url(#txtGlow)">SYSTEM.INFO</text>')
    out.append(f'<line x1="{RX + 106}" y1="102" x2="{RX + RW - 64}" y2="102" stroke="{t["hair"]}"/>')
    out.append(f'<text x="{RX + RW}" y="106" text-anchor="end" font-size="12" fill="{t["live"]}" '
               f'font-weight="700"><tspan>&#9679;</tspan> LIVE'
               f'<animate attributeName="opacity" values="1;0.25;1" dur="1.6s" repeatCount="indefinite"/></text>')

    # chip com o nome
    chip_w = 18 + len(NAME) * 8
    out.append(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="0.6s" fill="freeze"/>'
               f'<rect x="{RX}" y="122" width="{chip_w}" height="20" rx="4" fill="{t["chip_bg"]}"/>'
               f'<text x="{RX + 9}" y="136" font-size="14" font-weight="700" fill="{t["chip_fg"]}">{NAME}</text>'
               f'<line x1="{RX + chip_w + 10}" y1="130" x2="{RX + RW}" y2="130" stroke="{t["hair"]}"/></g>')

    # linhas: passo de 23px, com respiro extra onde ha quebra de secao
    y, delay = 162, 0.90
    for item in ROWS:
        if item is None:
            y += 8
            continue
        label, value = item
        out.append(divider_svg(t, y, value, delay) if label == "--"
                   else row_svg(t, y, label, value, delay))
        y += 23
        delay += 0.12

    # rodape com cursor piscando
    out.append(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.5s" '
               f'begin="{delay + 0.3:.2f}s" fill="freeze"/>'
               f'<text x="{RX}" y="{y + 8}" font-size="14" fill="{t["muted"]}">{FOOTER}'
               f'<tspan fill="{t["key"]}">&#9608;'
               f'<animate attributeName="fill-opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/>'
               f'</tspan></text></g>')
    return "\n".join(out)


def portrait_paths(dark):
    """Converte PHOTO num mapa de pontinhos 1-bit (dither Floyd-Steinberg).

    Devolve (cell, gh, bandas), onde cada banda e uma string de path SVG em
    coordenadas de celula -- o <g> pai aplica translate + scale.
    """
    from PIL import Image, ImageOps

    cell = PW / GRID_W
    gh = int(round(PH / cell))

    im = Image.open(PHOTO).convert("L").crop(CROP)
    im = ImageOps.autocontrast(im, cutoff=2).resize((GRID_W, gh), Image.LANCZOS)

    gamma, gain = LEVELS
    ax, ay, inner, outer = VIGNETTE
    hi_cut, hi_force = HIGHLIGHT
    px = im.load()

    # densidade de pontos: no tema escuro os pontos sao a luz; no claro, a sombra
    dens = []
    for y in range(gh):
        row = []
        for x in range(GRID_W):
            v = px[x, y] / 255.0
            if dark and v > hi_cut:
                # so para domar o nucleo estourado do painel de luz atras dele
                v = max(0.0, hi_cut - (v - hi_cut) * hi_force)
            v = v if dark else 1.0 - v
            v = min(1.0, (v ** gamma) * gain)
            # vinheta oval: o retrato se dissolve num ovalo e o fundo some nas
            # bordas -- sem isso o painel iluminado vira um bloco solido
            nx = (x / (GRID_W - 1) - 0.5) * 2 / ax
            ny = (y / (gh - 1) - 0.5) * 2 / ay
            r = (nx * nx + ny * ny) ** 0.5
            s = min(1.0, max(0.0, (r - inner) / (outer - inner)))
            row.append(v * (1.0 - s * s * (3.0 - 2.0 * s)))
        dens.append(row)

    # Floyd-Steinberg sobre a densidade
    on = [[False] * GRID_W for _ in range(gh)]
    for y in range(gh):
        for x in range(GRID_W):
            old = dens[y][x]
            new = 1.0 if old > 0.5 else 0.0
            on[y][x] = new > 0.5
            err = old - new
            for dx, dy, w in ((1, 0, 7 / 16), (-1, 1, 3 / 16), (0, 1, 5 / 16), (1, 1, 1 / 16)):
                sx, sy = x + dx, y + dy
                if 0 <= sx < GRID_W and 0 <= sy < gh:
                    dens[sy][sx] += err * w

    # run-length por linha: sequencias horizontais viram um retangulo so
    bands = ["" for _ in range(BANDS)]
    for y in range(gh):
        parts = []
        x = 0
        while x < GRID_W:
            if on[y][x]:
                n = 1
                while x + n < GRID_W and on[y][x + n]:
                    n += 1
                parts.append(f"M{x} {y}h{n}v1h-{n}z")
                x += n
            else:
                x += 1
        bands[min(BANDS - 1, y * BANDS // gh)] += "".join(parts)
    return cell, gh, bands


def portrait_panel(t, dark):
    cell, gh, bands = portrait_paths(dark)
    out = [f'<g transform="translate({PX},{PY}) scale({cell:.4f})" fill="url(#asciiGrad)" '
           f'shape-rendering="crispEdges">']
    for i, d in enumerate(bands):
        if not d:
            continue
        out.append(f'<g opacity="0"><animate attributeName="opacity" values="0;1" dur="0.7s" '
                   f'begin="{0.25 + i * 0.07:.2f}s" fill="freeze" calcMode="spline" keyTimes="0;1" '
                   f'keySplines=".4 0 .2 1"/><path d="{d}"/></g>')
    out.append('</g>')
    return "\n".join(out)


def graph_panel(t):
    """Conteudo alternativo do painel: grafo neural animado."""
    out = []

    for (x, _), name in zip(LAYERS, COL_LABELS):
        out.append(f'<text x="{x}" y="132" text-anchor="middle" font-size="9" letter-spacing="2" '
                   f'fill="{t["dim"]}">{name}</text>')

    edges = [(x1, y1, x2, y2)
             for (x1, ys1), (x2, ys2) in zip(LAYERS, LAYERS[1:])
             for y1 in ys1 for y2 in ys2]

    out.append('<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.8s" '
               'begin="0.35s" fill="freeze"/>')
    for i, (x1, y1, x2, y2) in enumerate(edges):
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{t["edge"]}" stroke-width="1"/>')
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{t["spark"]}" stroke-width="1.4" '
                   f'stroke-dasharray="4 14" opacity="0.5">'
                   f'<animate attributeName="stroke-dashoffset" values="36;0" dur="{2.4 + (i % 5) * 0.35:.2f}s" '
                   f'repeatCount="indefinite"/></line>')
    out.append('</g>')

    # pacotes de dados viajando por metade das arestas
    for i, (x1, y1, x2, y2) in enumerate(edges):
        if i % 2:
            continue
        dur = 2.6 + (i % 4) * 0.4
        begin = 1.0 + (i % 7) * 0.33
        out.append(f'<circle r="2.8" fill="{t["spark"]}">'
                   f'<animateMotion dur="{dur:.2f}s" begin="{begin:.2f}s" repeatCount="indefinite" '
                   f'path="M {x1} {y1} L {x2} {y2}"/>'
                   f'<animate attributeName="opacity" values="0;1;1;0" dur="{dur:.2f}s" begin="{begin:.2f}s" '
                   f'repeatCount="indefinite"/></circle>')

    for li, (x, ys) in enumerate(LAYERS):
        for ni, y in enumerate(ys):
            seed = li * 3 + ni
            out.append(f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.5s" '
                       f'begin="{0.25 + seed * 0.07:.2f}s" fill="freeze"/>'
                       f'<circle cx="{x}" cy="{y}" r="10" fill="none" stroke="{t["node"]}">'
                       f'<animate attributeName="r" values="10;22" dur="2.6s" begin="{seed * 0.31:.2f}s" '
                       f'repeatCount="indefinite"/>'
                       f'<animate attributeName="opacity" values="0.5;0" dur="2.6s" begin="{seed * 0.31:.2f}s" '
                       f'repeatCount="indefinite"/></circle>'
                       f'<circle cx="{x}" cy="{y}" r="8.5" fill="{t["screen"]}" stroke="{t["node"]}" '
                       f'stroke-width="2"/>'
                       f'<circle cx="{x}" cy="{y}" r="3" fill="{t["spark"]}"/></g>')
    return "\n".join(out)


def left_panel(t):
    """Painel esquerdo: moldura + conteudo (retrato ou grafo) + legenda."""
    cx = LX + LW // 2
    out = [f'<text x="{LX + 2}" y="74" font-size="10" letter-spacing="3" fill="{t["dim"]}">VISUAL.MAP</text>',
           f'<rect x="{LX}" y="{LY}" width="{LW}" height="{LH}" rx="10" fill="none" '
           f'stroke="{t["spark"]}" stroke-width="2" opacity="0.45" filter="url(#glow3)"/>',
           f'<rect x="{LX}" y="{LY}" width="{LW}" height="{LH}" rx="10" fill="{t["screen"]}" '
           f'stroke="{t["frame"]}"/>',
           '<g clip-path="url(#panelClip)">',
           f'<rect x="{LX}" y="{LY}" width="{LW}" height="{LH}" fill="url(#dotGrid)"/>']

    out.append(portrait_panel(t, True) if LEFT_PANEL == "portrait" else graph_panel(t))

    # varredura passando por cima do conteudo
    out.append(f'<rect x="{LX}" y="{LY}" width="{LW}" height="80" fill="url(#scan)">'
               f'<animate attributeName="y" values="{LY - 80};{LY + LH};{LY - 80}" dur="8s" '
               f'repeatCount="indefinite"/></rect>')

    # legenda inferior
    out.append(f'<line x1="{LX + 20}" y1="512" x2="{LX + LW - 20}" y2="512" stroke="{t["screen_hair"]}"/>')
    out.append(f'<text x="{cx}" y="536" text-anchor="middle" font-size="12" fill="{t["screen_fg"]}">'
               f'ai &#183; automation &#183; fullstack</text>')
    out.append(f'<text x="{cx}" y="558" text-anchor="middle" font-size="11" fill="{t["screen_dim"]}">'
               f'<tspan fill="{t["node"]}">[ok]</tspan> pipeline online '
               f'<tspan fill="{t["spark"]}">&#9608;'
               f'<animate attributeName="fill-opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/>'
               f'</tspan></text>')
    out.append('</g>')

    # cantos em L
    for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
        x, y = LX + dx * LW, LY + dy * LH
        sx, sy = (14 if dx == 0 else -14), (14 if dy == 0 else -14)
        out.append(f'<path d="M {x + sx} {y} L {x} {y} L {x} {y + sy}" fill="none" stroke="{t["spark"]}" '
                   f'stroke-width="2" opacity="0.8"/>')
    return "\n".join(out)


def build(t):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace" role="img" aria-label="{NAME} - gustavo.sh --live">
<defs>
<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
<stop offset="0" stop-color="#7C4DFF"><animate attributeName="stop-color" values="#7C4DFF;#48BFE3;#3FB950;#7C4DFF" dur="10s" repeatCount="indefinite"/></stop>
<stop offset="0.5" stop-color="#48BFE3"><animate attributeName="stop-color" values="#48BFE3;#3FB950;#7C4DFF;#48BFE3" dur="10s" repeatCount="indefinite"/></stop>
<stop offset="1" stop-color="#3FB950"><animate attributeName="stop-color" values="#3FB950;#7C4DFF;#48BFE3;#3FB950" dur="10s" repeatCount="indefinite"/></stop>
</linearGradient>
<linearGradient id="panelGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t['panel_a']}"/><stop offset="1" stop-color="{t['panel_b']}"/></linearGradient>
<linearGradient id="scan" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t['spark']}" stop-opacity="0"/><stop offset="0.5" stop-color="{t['spark']}" stop-opacity="0.14"/><stop offset="1" stop-color="{t['spark']}" stop-opacity="0"/></linearGradient>
<pattern id="dotGrid" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" r="0.9" fill="{t['grid']}" opacity="0.22"/></pattern>
<linearGradient id="asciiGrad" x1="0" y1="{PY}" x2="0" y2="{PY + PH}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{t['ink'][0]}"/><stop offset="0.45" stop-color="{t['ink'][1]}"/><stop offset="1" stop-color="{t['ink'][2]}"/><animateTransform attributeName="gradientTransform" type="translate" values="0 -110; 0 110; 0 -110" dur="9s" repeatCount="indefinite"/></linearGradient>
<filter id="glow8" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="8"/></filter>
<filter id="glow3" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3"/></filter>
<filter id="txtGlow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="0.9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="winClip"><rect x="2" y="2" width="{W - 4}" height="{H - 4}" rx="18"/></clipPath>
<clipPath id="panelClip"><rect x="{LX}" y="{LY}" width="{LW}" height="{LH}" rx="10"/></clipPath>
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
{left_panel(t)}
{right_panel(t)}
</g>
<rect x="3" y="3" width="{W - 6}" height="{H - 6}" rx="17" fill="none" stroke="url(#accent)" stroke-width="3" opacity="0.55" filter="url(#glow8)"/>
<rect x="3" y="3" width="{W - 6}" height="{H - 6}" rx="17" fill="none" stroke="url(#accent)" stroke-width="1.6"/>
</svg>
'''


DIV_W, DIV_H = 1180, 40     # divisor de secao usado entre os blocos do README


def build_divider():
    """Regua animada que separa as secoes -- serve nos dois temas do GitHub.

    Fundo transparente e as pontas somem no nada, entao funciona tanto sobre
    branco quanto sobre o cinza-escuro do GitHub.
    """
    cy = DIV_H // 2
    ticks = "".join(
        f'<line x1="{x}" y1="{cy - 5}" x2="{x}" y2="{cy + 5}" stroke="url(#rule)" stroke-width="1.8"/>'
        for x in range(90, DIV_W - 89, 90) if abs(x - DIV_W // 2) > 80
    )
    packets = "".join(
        f'<rect x="-3" y="{cy - 3}" width="6" height="6" rx="1.5" fill="#48BFE3">'
        f'<animateMotion dur="{5.5 + i * 1.3:.1f}s" begin="{i * 1.7:.1f}s" repeatCount="indefinite" '
        f'path="M 40 {cy} L {DIV_W - 40} {cy}"/>'
        f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.12;0.88;1" '
        f'dur="{5.5 + i * 1.3:.1f}s" begin="{i * 1.7:.1f}s" repeatCount="indefinite"/></rect>'
        for i in range(3)
    )
    mid = DIV_W // 2
    # o gradiente e em userSpaceOnUse: num <line> a caixa delimitadora tem
    # altura zero, e o padrao (objectBoundingBox) simplesmente nao renderiza
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{DIV_W}" height="{DIV_H}" viewBox="0 0 {DIV_W} {DIV_H}" role="img" aria-label="separador">
<defs>
<linearGradient id="rule" x1="0" y1="0" x2="{DIV_W}" y2="0" gradientUnits="userSpaceOnUse">
<stop offset="0" stop-color="#7C4DFF" stop-opacity="0"/>
<stop offset="0.2" stop-color="#7C4DFF" stop-opacity="0.9"><animate attributeName="stop-color" values="#7C4DFF;#48BFE3;#3FB950;#7C4DFF" dur="10s" repeatCount="indefinite"/></stop>
<stop offset="0.5" stop-color="#48BFE3" stop-opacity="1"><animate attributeName="stop-color" values="#48BFE3;#3FB950;#7C4DFF;#48BFE3" dur="10s" repeatCount="indefinite"/></stop>
<stop offset="0.8" stop-color="#3FB950" stop-opacity="0.9"><animate attributeName="stop-color" values="#3FB950;#7C4DFF;#48BFE3;#3FB950" dur="10s" repeatCount="indefinite"/></stop>
<stop offset="1" stop-color="#3FB950" stop-opacity="0"/>
</linearGradient>
<filter id="divGlow" x="-20%" y="-400%" width="140%" height="900%"><feGaussianBlur stdDeviation="3"/></filter>
</defs>
<line x1="0" y1="{cy}" x2="{DIV_W}" y2="{cy}" stroke="url(#rule)" stroke-width="4" opacity="0.45" filter="url(#divGlow)"/>
<line x1="0" y1="{cy}" x2="{mid - 60}" y2="{cy}" stroke="url(#rule)" stroke-width="2.2"/>
<line x1="{mid + 60}" y1="{cy}" x2="{DIV_W}" y2="{cy}" stroke="url(#rule)" stroke-width="2.2"/>
{ticks}
{packets}
<g transform="translate({mid} {cy})" fill="#48BFE3" stroke="#48BFE3">
<animate attributeName="fill" values="#48BFE3;#3FB950;#7C4DFF;#48BFE3" dur="10s" repeatCount="indefinite"/>
<animate attributeName="stroke" values="#48BFE3;#3FB950;#7C4DFF;#48BFE3" dur="10s" repeatCount="indefinite"/>
<path d="M -60 0 L -34 0 M 34 0 L 60 0" stroke-width="2.2"/>
<circle cx="-24" cy="0" r="2.8" stroke="none"><animate attributeName="opacity" values="0.25;1;0.25" dur="2.4s" repeatCount="indefinite"/></circle>
<circle cx="24" cy="0" r="2.8" stroke="none"><animate attributeName="opacity" values="1;0.25;1" dur="2.4s" repeatCount="indefinite"/></circle>
<path d="M 0 -9 L 9 0 L 0 9 L -9 0 Z" fill="#7C4DFF" stroke="none">
<animateTransform attributeName="transform" type="rotate" from="0" to="180" dur="6s" repeatCount="indefinite"/>
<animate attributeName="fill" values="#7C4DFF;#48BFE3;#3FB950;#7C4DFF" dur="10s" repeatCount="indefinite"/>
</path>
</g>
</svg>
'''


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    for theme in THEMES.values():
        target = root / theme["out"]
        target.write_text(build(theme), encoding="utf-8")
        print(f"gerado: {target.name} ({target.stat().st_size / 1024:.1f} KB)")

    divider = root / "divider.svg"
    divider.write_text(build_divider(), encoding="utf-8")
    print(f"gerado: {divider.name} ({divider.stat().st_size / 1024:.1f} KB)")

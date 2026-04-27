import json, os, locale
from datetime import datetime, timezone

_MESES_PT = [
    '', 'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
    'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'
]

EVENTS_JSON = os.path.join(os.path.dirname(__file__), '..', 'web', 'events.json')
OUTPUT_HTML = os.path.join(os.path.dirname(__file__), '..', 'web', 'index.html')

BADGE_CORES = {
    'Show':        '#C0392B',
    'Festa':       '#6C3483',
    'Feira':       '#1E8449',
    'Festival':    '#B7770D',
    'Teatro':      '#1A5276',
    'Esporte':     '#0E6655',
    'Corporativo': '#7F8C8D',
    'Outro':       '#95A5A6',
}

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Source+Sans+3:wght@400;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
    background: #F7F3EE;
    color: #1A1A1A;
    font-family: 'Source Sans 3', sans-serif;
    min-height: 100vh;
}

/* Banner stale */
.stale-banner {
    background: #FEF9E7;
    border-left: 4px solid #E67E22;
    color: #7D6608;
    padding: 10px 20px;
    font-size: 14px;
    font-style: italic;
    text-align: center;
}

/* Header */
header {
    padding: 32px 24px 0;
    max-width: 1200px;
    margin: 0 auto;
}
.header-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
}
.linka-logo {
    height: 80px;
    width: auto;
    object-fit: contain;
    opacity: 0.9;
}
.logo {
    font-family: 'Playfair Display', serif;
    font-size: clamp(42px, 8vw, 80px);
    font-weight: 900;
    color: #5B2D8E;
    letter-spacing: -2px;
    line-height: 1;
}
.sub {
    font-size: 13px;
    color: #888;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 6px;
}
.rule {
    height: 3px;
    background: #5B2D8E;
    margin: 16px 0 24px;
    transform-origin: left;
    animation: drawRule 0.6s ease forwards;
}
@keyframes drawRule { from { transform: scaleX(0); } to { transform: scaleX(1); } }

/* Filtros */
.filtros {
    max-width: 1200px;
    margin: 0 auto 28px;
    padding: 0 24px;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}
.filtro-btn {
    background: none;
    border: 1px solid #ccc;
    border-radius: 2px;
    padding: 6px 14px;
    font-family: 'Source Sans 3', sans-serif;
    font-size: 12px;
    letter-spacing: 1px;
    text-transform: uppercase;
    cursor: pointer;
    color: #555;
    transition: all 0.2s;
}
.filtro-btn:hover, .filtro-btn.active {
    background: #5B2D8E;
    border-color: #5B2D8E;
    color: #fff;
}

/* Grid */
.grid {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 24px 48px;
    display: grid;
    grid-template-columns: 1fr;
    gap: 24px;
}
@media (min-width: 640px) {
    .grid { grid-template-columns: repeat(2, 1fr); }
}
@media (min-width: 960px) {
    .grid { grid-template-columns: repeat(3, 1fr); }
    .grid .card:first-child {
        grid-column: span 2;
    }
}

/* Card */
.card {
    background: #fff;
    border: 1px solid #E0DAD0;
    padding: 20px;
    transition: transform 0.2s, box-shadow 0.2s;
    cursor: pointer;
    perspective: 600px;
}
.card:hover {
    transform: rotateY(3deg) translateY(-4px);
    box-shadow: -6px 8px 24px rgba(91,45,142,0.12);
}
.badge {
    display: inline-block;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #fff;
    border-radius: 2px;
    margin-bottom: 10px;
}
.card h2 {
    font-family: 'Playfair Display', serif;
    font-size: clamp(16px, 2.5vw, 22px);
    font-weight: 700;
    line-height: 1.3;
    margin-bottom: 8px;
    color: #1A1A1A;
}
.meta {
    font-size: 12px;
    color: #999;
    letter-spacing: 0.5px;
    margin-bottom: 10px;
}
.narrativa {
    font-size: 14px;
    color: #555;
    font-style: italic;
    line-height: 1.5;
    border-top: 1px solid #F0EBE3;
    padding-top: 10px;
    margin-top: 8px;
}

/* Vazio */
.vazio {
    grid-column: 1 / -1;
    text-align: center;
    padding: 60px 20px;
    color: #aaa;
    font-family: 'Playfair Display', serif;
    font-size: 20px;
}

/* Partículas */
.particles {
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}
.particle {
    position: absolute;
    font-family: 'Playfair Display', serif;
    color: #5B2D8E;
    opacity: 0.04;
    animation: fall linear infinite;
    user-select: none;
}
@keyframes fall {
    from { transform: translateY(-60px); }
    to   { transform: translateY(110vh); }
}

main, header, .filtros { position: relative; z-index: 1; }
"""

JS = """
const cards = document.querySelectorAll('.card');
const btns  = document.querySelectorAll('.filtro-btn');

btns.forEach(btn => {
    btn.addEventListener('click', () => {
        const cat = btn.dataset.cat;
        btns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        cards.forEach(card => {
            const show = cat === 'todos' || card.dataset.cat === cat;
            card.style.display = show ? '' : 'none';
        });
    });
});

// Partículas de letras
const chars = 'RADAR●▪'.split('');
const container = document.querySelector('.particles');
if (container) {
    for (let i = 0; i < 18; i++) {
        const el = document.createElement('span');
        el.className = 'particle';
        el.textContent = chars[i % chars.length];
        el.style.left = Math.random() * 100 + 'vw';
        el.style.fontSize = (14 + Math.random() * 28) + 'px';
        el.style.animationDuration = (18 + Math.random() * 24) + 's';
        el.style.animationDelay = -(Math.random() * 30) + 's';
        container.appendChild(el);
    }
}
"""

def render(eventos=None, stale=False):
    """Gera o HTML completo da interface jornal.
    Se eventos=None, lê de web/events.json.
    Se stale=True, exibe banner de aviso."""

    if eventos is None:
        try:
            with open(EVENTS_JSON, encoding='utf-8') as f:
                eventos = json.load(f)
        except FileNotFoundError:
            eventos = []

    now = datetime.now()
    hoje = f'{now.day} de {_MESES_PT[now.month]} de {now.year}'

    banner = ''
    if stale:
        banner = '<div class="stale-banner">⚠ Dados podem estar desatualizados — última atualização há mais de 48h.</div>'

    # Categorias presentes para os filtros
    cats_presentes = sorted({ev.get('categoria', 'Outro') for ev in eventos})

    filtros_html = '<button class="filtro-btn active" data-cat="todos">Todos</button>\n'
    for cat in cats_presentes:
        filtros_html += f'    <button class="filtro-btn" data-cat="{cat}">{cat}</button>\n'

    # Cards
    cards_html = ''
    if not eventos:
        cards_html = '<p class="vazio">Nenhum evento encontrado esta semana.</p>'
    else:
        for ev in eventos:
            cat   = ev.get('categoria', 'Outro')
            cor   = BADGE_CORES.get(cat, '#95A5A6')
            titulo = ev.get('titulo', '').replace('<', '&lt;').replace('>', '&gt;')
            local  = ev.get('local', '') or 'Ribeirão Preto'
            data   = ev.get('data_iso', '') or 'Data a confirmar'
            narr   = ev.get('narrativa_ia', '').replace('<', '&lt;').replace('>', '&gt;')
            url    = ev.get('url', '#')

            cards_html += f'''
    <article class="card" data-cat="{cat}" onclick="window.open('{url}','_blank')">
        <span class="badge" style="background:{cor}">{cat}</span>
        <h2>{titulo}</h2>
        <p class="meta">{data} &nbsp;·&nbsp; {local}</p>
        {'<p class="narrativa">' + narr + '</p>' if narr else ''}
    </article>'''

    html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="RADAR — Agregador inteligente de eventos de Ribeirão Preto">
    <title>RADAR — Ribeirão Preto</title>
    <style>{CSS}</style>
</head>
<body>
<div class="particles"></div>
{banner}
<header>
    <div class="header-top">
        <h1 class="logo">● RADAR</h1>
        <img src="linka.png" alt="LINKA" class="linka-logo">
    </div>
    <p class="sub">Ribeirão Preto &nbsp;·&nbsp; Edição {hoje}</p>
    <div class="rule"></div>
</header>

<nav class="filtros">
    {filtros_html}
</nav>

<main class="grid">
    {cards_html}
</main>

<script>{JS}</script>
</body>
</html>'''

    return html

def render_to_file(stale=False):
    """Lê events.json, gera index.html e salva em web/."""
    html = render(stale=stale)
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)
    n = html.count('class="card"')
    print(f'[OK] index.html gerado com {n} eventos — {OUTPUT_HTML}')

if __name__ == '__main__':
    render_to_file()

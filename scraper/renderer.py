import json, os, locale
from datetime import datetime, timezone

_MESES_PT = [
    '', 'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
    'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'
]

EVENTS_JSON = os.path.join(os.path.dirname(__file__), '..', 'web', 'events.json')
OUTPUT_HTML = os.path.join(os.path.dirname(__file__), '..', 'web', 'index.html')

RADAR_VERSION = "1.2.0"

CHANGELOG = {
    "1.2.0": {
        "titulo": "Cobertura expandida para 200km",
        "novidades": [
            "249 eventos de 11 cidades da região",
            "Franca, Araraquara, Barretos, Jaboticabal, Bebedouro, Guariba, Monte Alto, São José do Rio Preto, Campinas e Uberaba",
            "Deduplicação inteligente — sem eventos repetidos entre cidades",
            "60% das duplicatas removidas automaticamente",
        ]
    },
    "1.1.0": {
        "titulo": "Datas e expansão regional",
        "novidades": [
            "Datas dos eventos agora no formato DD/MM/YYYY",
            "Filtro por cidade adicionado na interface",
            "Logo LINKA no header",
        ]
    },
    "1.0.0": {
        "titulo": "Lançamento do RADAR MVP",
        "novidades": [
            "27 eventos de Ribeirão Preto",
            "Categorização por IA",
            "Interface estilo jornal",
        ]
    },
}

BADGE_CORES = {
    'Show':        '#D4AC0D',  # amarelo escuro
    'Festa':       '#6C3483',  # roxo escuro
    'Feira':       '#1E8449',  # verde
    'Festival':    '#B7770D',  # laranja escuro
    'Teatro':      '#1A5276',  # azul escuro
    'Esporte':     '#0E6655',  # verde-água
    'Corporativo': '#C0392B',  # vermelho
    'Curso':       '#1A6B8A',  # azul petróleo
    'Exposição':   '#884EA0',  # roxo médio
    'Religioso':   '#A04000',  # marrom-terracota
    'Turismo':     '#1D8348',  # verde floresta
    'Infantil':    '#CB4335',  # vermelho coral
    'Outro':       '#95A5A6',  # cinza claro
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
    height: 150px;
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
    opacity: 0;
    transform: translateY(-16px);
    animation: logoEntrada 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.1s forwards;
}
@keyframes logoEntrada {
    from {
        opacity: 0;
        transform: translateY(-16px) scale(0.96);
        letter-spacing: 8px;
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
        letter-spacing: -2px;
    }
}
.logo-bullet {
    display: inline-block;
    animation: bulletPulse 2s ease-in-out 0.9s infinite;
    color: #5B2D8E;
}
@keyframes bulletPulse {
    0%, 100% { transform: scale(1);   opacity: 1;   }
    50%       { transform: scale(1.3); opacity: 0.7; }
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

/* ── Filtros dropdown ── */
.filtros-wrapper {
    max-width: 1200px;
    margin: 0 auto 28px;
    padding: 0 24px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    align-items: start;
}
.filtro-grupo {
    display: flex;
    flex-direction: column;
    gap: 6px;
}
.filtro-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #aaa;
    font-family: 'Source Sans 3', sans-serif;
}
.filtro-select {
    appearance: none;
    -webkit-appearance: none;
    background: #fff url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%235B2D8E' stroke-width='2' fill='none' stroke-linecap='round'/%3E%3C/svg%3E") no-repeat right 14px center;
    border: 1.5px solid #E0DAD0;
    border-radius: 999px;
    padding: 10px 40px 10px 20px;
    font-family: 'Source Sans 3', sans-serif;
    font-size: 14px;
    color: #1A1A1A;
    cursor: pointer;
    transition: border-color 0.2s, box-shadow 0.2s;
    width: 100%;
    box-shadow: 0 2px 8px rgba(91,45,142,0.06);
}
.filtro-select:focus {
    outline: none;
    border-color: #5B2D8E;
    box-shadow: 0 0 0 3px rgba(91, 45, 142, 0.12);
}
.filtro-select:hover {
    border-color: #5B2D8E;
}
@media (max-width: 600px) {
    .filtros-wrapper { grid-template-columns: 1fr; }
}

/* ── Busca ── */
.busca-wrapper {
    max-width: 1200px;
    margin: 0 auto 20px;
    padding: 0 24px;
    display: flex;
    justify-content: center;
}

.busca-grupo {
    width: 100%;
    max-width: 520px;
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.busca-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #aaa;
    font-family: 'Source Sans 3', sans-serif;
    text-align: center;
}

.busca-input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
}

.busca-input {
    width: 100%;
    border: 1.5px solid #E0DAD0;
    border-radius: 999px;
    padding: 10px 40px 10px 20px;
    font-family: 'Source Sans 3', sans-serif;
    font-size: 14px;
    color: #1A1A1A;
    background: #fff;
    transition: border-color 0.2s, box-shadow 0.2s;
    box-shadow: 0 2px 8px rgba(91,45,142,0.06);
}

.busca-input::placeholder {
    color: #bbb;
}

.busca-input:focus {
    outline: none;
    border-color: #5B2D8E;
    box-shadow: 0 0 0 3px rgba(91, 45, 142, 0.12);
}

.busca-clear {
    position: absolute;
    right: 14px;
    background: none;
    border: none;
    cursor: pointer;
    color: #bbb;
    font-size: 18px;
    line-height: 1;
    display: none;
    padding: 4px;
    transition: color 0.2s;
}

.busca-clear:hover {
    color: #5B2D8E;
}

.busca-clear.visible {
    display: block;
}

@media (max-width: 600px) {
    .busca-grupo {
        max-width: 100%;
    }
}

.sem-resultado {
    grid-column: 1 / -1;
    text-align: center;
    padding: 60px 20px;
    font-family: 'Playfair Display', serif;
    font-size: 20px;
    color: #bbb;
    display: none;
}

.sem-resultado.visible {
    display: block;
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
    border-radius: 16px;
    padding: 20px;
    position: relative;
    cursor: pointer;
    perspective: 600px;
    opacity: 0;
    transform: translateY(24px);
    transition: opacity 0.5s ease, transform 0.5s ease,
                box-shadow 0.2s ease;
}
.card.visivel {
    opacity: 1;
    transform: translateY(0);
}
.card.visivel:hover {
    transform: translateY(-4px) !important;
    box-shadow: 0 8px 32px rgba(91, 45, 142, 0.13);
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

main, header, .filtros-wrapper, .busca-wrapper { position: relative; z-index: 1; }

/* ── Popup de novidades ── */
.popup-overlay {
    position: fixed;
    inset: 0;
    background: rgba(10, 8, 6, 0.75);
    backdrop-filter: blur(4px);
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
    animation: fadeInOverlay 0.4s ease forwards;
}
@keyframes fadeInOverlay {
    from { opacity: 0; }
    to   { opacity: 1; }
}
.popup-overlay.hidden { display: none; }

.popup-box {
    background: #F7F3EE;
    border: 1px solid #E0DAD0;
    border-top: 5px solid #5B2D8E;
    max-width: 520px;
    width: 100%;
    padding: 36px 40px;
    animation: slideUp 0.45s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    position: relative;
}
@keyframes slideUp {
    from { transform: translateY(40px); opacity: 0; }
    to   { transform: translateY(0);    opacity: 1; }
}

.popup-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
}
.popup-badge {
    background: #5B2D8E;
    color: #fff;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    padding: 4px 12px;
    border-radius: 2px;
    font-family: 'Source Sans 3', sans-serif;
}
.popup-edicao {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #aaa;
    font-family: 'Source Sans 3', sans-serif;
}
.popup-rule {
    height: 2px;
    background: #5B2D8E;
    margin: 14px 0;
    transform-origin: left;
    transform: scaleX(0);
    animation: drawRule 0.6s ease 0.3s forwards;
}
.popup-titulo {
    font-family: 'Playfair Display', serif;
    font-size: clamp(22px, 4vw, 30px);
    font-weight: 900;
    color: #1A1A1A;
    line-height: 1.2;
    margin-bottom: 8px;
}
.popup-subtitulo {
    font-size: 13px;
    color: #888;
    letter-spacing: 0.5px;
    margin-bottom: 16px;
    font-family: 'Source Sans 3', sans-serif;
}
.popup-lista {
    list-style: none;
    padding: 0;
    margin: 0 0 4px;
    display: flex;
    flex-direction: column;
    gap: 10px;
}
.popup-lista li {
    font-size: 15px;
    color: #333;
    padding-left: 20px;
    position: relative;
    line-height: 1.5;
    font-family: 'Source Sans 3', sans-serif;
}
.popup-lista li::before {
    content: '●';
    position: absolute;
    left: 0;
    color: #5B2D8E;
    font-size: 8px;
    top: 5px;
}
.popup-btn {
    display: inline-block;
    background: #5B2D8E;
    color: #fff;
    border: none;
    padding: 14px 28px;
    font-family: 'Source Sans 3', sans-serif;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    cursor: pointer;
    width: 100%;
    margin-top: 20px;
    transition: background 0.2s, transform 0.15s;
    border-radius: 2px;
}
.popup-btn:hover {
    background: #3B1A6E;
    transform: translateY(-1px);
}
.popup-checkbox-wrapper {
    margin-top: 20px;
    padding-top: 16px;
    border-top: 1px solid #E0DAD0;
}
.popup-checkbox-label {
    display: flex;
    align-items: center;
    gap: 10px;
    cursor: pointer;
    user-select: none;
}
.popup-checkbox-label input[type="checkbox"] {
    appearance: none;
    -webkit-appearance: none;
    width: 18px;
    height: 18px;
    border: 2px solid #5B2D8E;
    border-radius: 2px;
    cursor: pointer;
    flex-shrink: 0;
    position: relative;
    transition: background 0.2s;
}
.popup-checkbox-label input[type="checkbox"]:checked {
    background: #5B2D8E;
}
.popup-checkbox-label input[type="checkbox"]:checked::after {
    content: '';
    position: absolute;
    left: 3px;
    top: 0px;
    width: 5px;
    height: 10px;
    border: 2px solid #fff;
    border-top: none;
    border-left: none;
    transform: rotate(45deg);
}
.popup-checkbox-text {
    font-size: 13px;
    color: #666;
    font-family: 'Source Sans 3', sans-serif;
}
@media (max-width: 480px) {
    .popup-box { padding: 24px 20px; }
}
footer {
    position: relative;
    z-index: 1;
    text-align: center;
    padding: 32px 24px;
    margin-top: 40px;
    border-top: 1px solid #E0DAD0;
    font-size: 13px;
    color: #aaa;
    font-family: 'Source Sans 3', sans-serif;
}
footer a {
    color: #5B2D8E;
    text-decoration: none;
    border-bottom: 1px solid transparent;
    transition: border-color 0.2s;
}
footer a:hover {
    border-bottom-color: #5B2D8E;
}
.card-link-hint {
    display: inline-block;
    margin-top: 12px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #5B2D8E;
    font-family: 'Source Sans 3', sans-serif;
    opacity: 0;
    transform: translateX(-4px);
    transition: opacity 0.2s, transform 0.2s;
}
.card:hover .card-link-hint {
    opacity: 1;
    transform: translateX(0);
}
"""

JS = """
// Data da edicao — sempre atual
(function() {
    const meses = [
        'janeiro','fevereiro','março','abril','maio','junho',
        'julho','agosto','setembro','outubro','novembro','dezembro'
    ];
    const hoje = new Date();
    const el   = document.getElementById('data-edicao');
    if (el) el.textContent = hoje.getDate() + ' de ' + meses[hoje.getMonth()] + ' de ' + hoje.getFullYear();
})();

function aplicarFiltros() {
    const cat    = document.getElementById('select-cat').value;
    const cidade = document.getElementById('select-cidade').value;
    const busca  = document.getElementById('busca-input').value
                    .toLowerCase()
                    .normalize('NFD')
                    .replace(/[̀-ͯ]/g, '');

    const cards    = document.querySelectorAll('.card');
    const btnClear = document.getElementById('busca-clear');
    const semRes   = document.getElementById('sem-resultado');
    let visiveis = 0;

    if (btnClear) {
        btnClear.classList.toggle('visible', busca.length > 0);
    }

    cards.forEach(card => {
        const catOk    = cat    === 'todos' || card.dataset.cat    === cat;
        const cidadeOk = cidade === 'todas' || card.dataset.cidade === cidade;

        let buscaOk = true;
        if (busca.length > 0) {
            const texto = (card.textContent || '')
                .toLowerCase()
                .normalize('NFD')
                .replace(/[̀-ͯ]/g, '');
            buscaOk = texto.includes(busca);
        }

        const show = catOk && cidadeOk && buscaOk;
        card.style.display = show ? '' : 'none';
        if (show) visiveis++;
    });

    const label = document.getElementById('count-label');
    if (label) label.textContent = visiveis + ' evento' + (visiveis !== 1 ? 's' : '');

    if (semRes) {
        semRes.classList.toggle('visible', visiveis === 0);
    }
}

function limparBusca() {
    const input = document.getElementById('busca-input');
    if (input) {
        input.value = '';
        input.focus();
    }
    aplicarFiltros();
}

// Scroll reveal nos cards
const observador = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
        if (entry.isIntersecting) {
            setTimeout(() => {
                entry.target.classList.add('visivel');
            }, i * 60);
            observador.unobserve(entry.target);
        }
    });
}, {
    threshold: 0.08,
    rootMargin: '0px 0px -40px 0px'
});

document.querySelectorAll('.card').forEach(card => {
    observador.observe(card);
});

// Partículas
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

    # Ordenar: eventos com data primeiro (por data asc), sem data no final
    def sort_key(ev):
        d = ev.get('data_iso', '')
        if d:
            return (0, d)
        return (1, '')

    eventos = sorted(eventos, key=sort_key)

    # Limpar sufixos de cidade dos títulos
    import re as _re
    SUFIXOS_CIDADE = [
        ' - Ribeirão Preto-SP', ' - Ribeirão Preto - SP',
        ' - Ribeirão Preto', ' | Ribeirão Preto',
        ' - Franca-SP', ' - Franca - SP', ' - Franca',
        ' - Araraquara-SP', ' - Araraquara - SP', ' - Araraquara',
        ' - Barretos-SP', ' - Barretos - SP', ' - Barretos',
        ' - Campinas-SP', ' - Campinas - SP', ' - Campinas',
        ' - São José do Rio Preto-SP', ' - São José do Rio Preto',
        ' - Uberaba-MG', ' - Uberaba - MG', ' - Uberaba',
        ' - Jaboticabal-SP', ' - Jaboticabal',
        ' - Bebedouro-SP', ' - Bebedouro',
        ' - Guariba-SP', ' - Guariba',
        ' - Monte Alto-SP', ' - Monte Alto',
        '/SP', '-SP', '- SP',
    ]

    def limpar_titulo(titulo):
        for sufixo in SUFIXOS_CIDADE:
            if titulo.endswith(sufixo):
                titulo = titulo[:-len(sufixo)].strip()
        titulo = _re.sub(r'\s*[\|\/]\s*[A-Z][a-zÀ-ú\s]+$', '', titulo).strip()
        return titulo

    for ev in eventos:
        ev['titulo'] = limpar_titulo(ev.get('titulo', ''))

    banner = ''
    if stale:
        banner = '<div class="stale-banner">⚠ Dados podem estar desatualizados — última atualização há mais de 48h.</div>'

    # Options para dropdown de categorias
    cats_presentes = sorted({ev.get('categoria', 'Outro') for ev in eventos})
    cats_options_html = ''
    for cat in cats_presentes:
        n = sum(1 for ev in eventos if ev.get('categoria') == cat)
        cats_options_html += f'<option value="{cat}">{cat} ({n})</option>\n'

    # Options para dropdown de cidades
    cidades_presentes = sorted({ev.get('cidade', 'Ribeirão Preto') for ev in eventos})
    cidades_options_html = ''
    for cidade in cidades_presentes:
        n = sum(1 for ev in eventos if ev.get('cidade', 'Ribeirão Preto') == cidade)
        cidades_options_html += f'<option value="{cidade}">{cidade} ({n})</option>\n'

    # Popup de novidades
    version_data = CHANGELOG.get(RADAR_VERSION, {})
    popup_titulo = version_data.get('titulo', 'Atualizacao disponivel')
    popup_novidades = version_data.get('novidades', [])
    novidades_html = ''.join(f'<li>{item}</li>\n' for item in popup_novidades)

    popup_html = f'''<div id="radar-popup-overlay" class="popup-overlay">
    <div class="popup-box">
        <div class="popup-header">
            <span class="popup-badge">v{RADAR_VERSION}</span>
            <span class="popup-edicao">EDIÇÃO ESPECIAL</span>
        </div>
        <div class="popup-rule"></div>
        <h2 class="popup-titulo">{popup_titulo}</h2>
        <p class="popup-subtitulo">O que há de novo nesta edição:</p>
        <ul class="popup-lista">
            {novidades_html}        </ul>
        <div class="popup-rule"></div>
        <div class="popup-checkbox-wrapper">
            <label class="popup-checkbox-label">
                <input type="checkbox" id="popup-nao-mostrar">
                <span class="popup-checkbox-text">Não mostrar novamente</span>
            </label>
        </div>
        <button class="popup-btn" onclick="fecharPopup()">Continuar para o RADAR →</button>
    </div>
</div>
<script>
(function() {{
    var POPUP_KEY = 'radar_nao_mostrar_v{RADAR_VERSION}';
    window.fecharPopup = function() {{
        var checkbox = document.getElementById('popup-nao-mostrar');
        if (checkbox && checkbox.checked) {{
            localStorage.setItem(POPUP_KEY, '1');
        }}
        var overlay = document.getElementById('radar-popup-overlay');
        if (overlay) {{
            overlay.style.animation = 'fadeInOverlay 0.3s ease reverse forwards';
            setTimeout(function() {{ overlay.classList.add('hidden'); }}, 280);
        }}
    }};
    if (localStorage.getItem(POPUP_KEY)) {{
        var overlay = document.getElementById('radar-popup-overlay');
        if (overlay) overlay.classList.add('hidden');
    }}
}})();
</script>'''

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
            data_iso = ev.get('data_iso', '')
            if data_iso:
                try:
                    dt = datetime.strptime(data_iso, '%Y-%m-%d')
                    data = dt.strftime('%d/%m/%Y')
                except:
                    data = data_iso
            else:
                data = 'Data a confirmar'
            narr   = ev.get('narrativa_ia', '').replace('<', '&lt;').replace('>', '&gt;')
            url    = ev.get('url', '#')
            cidade = ev.get('cidade', 'Ribeirão Preto')

            cards_html += f'''
    <article class="card" data-cat="{cat}" data-cidade="{cidade}" onclick="window.open('{url}','_blank')">
        <span class="badge" style="background:{cor}">{cat}</span>
        <h2>{titulo}</h2>
        <p class="meta">{data} &nbsp;·&nbsp; {local}</p>
        {'<p class="narrativa">' + narr + '</p>' if narr else ''}
        <span class="card-link-hint">Ver evento →</span>
    </article>'''

    html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="RADAR — Agregador inteligente de eventos de Ribeirão Preto">
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='45' fill='%235B2D8E'/%3E%3Ctext x='50' y='67' font-size='52' text-anchor='middle' fill='white' font-family='serif'%3E●%3C/text%3E%3C/svg%3E">
    <title>RADAR — Ribeirão Preto</title>
    <style>{CSS}</style>
</head>
<body>
{popup_html}
<div class="particles"></div>
{banner}
<header>
    <div class="header-top">
        <h1 class="logo"><span class="logo-bullet">●</span> RADAR</h1>
        <img src="linka.png" alt="LINKA" class="linka-logo">
    </div>
    <p class="sub">Ribeirão Preto &nbsp;·&nbsp; Edição <span id="data-edicao"></span></p>
    <div class="rule"></div>
</header>

<div class="busca-wrapper">
    <div class="busca-grupo">
        <label class="busca-label" for="busca-input">Buscar evento</label>
        <div class="busca-input-wrapper">
            <input
                type="text"
                id="busca-input"
                class="busca-input"
                placeholder="Buscar evento ou artista..."
                oninput="aplicarFiltros()"
                autocomplete="off"
            >
            <button class="busca-clear" id="busca-clear" onclick="limparBusca()" title="Limpar">×</button>
        </div>
    </div>
</div>

<div class="filtros-wrapper">
    <div class="filtro-grupo">
        <label class="filtro-label" for="select-cat">Tipo de evento</label>
        <select class="filtro-select" id="select-cat" onchange="aplicarFiltros()">
            <option value="todos">Todos os tipos</option>
            {cats_options_html}
        </select>
    </div>
    <div class="filtro-grupo">
        <label class="filtro-label" for="select-cidade">Cidade</label>
        <select class="filtro-select" id="select-cidade" onchange="aplicarFiltros()">
            <option value="todas">Todas as cidades</option>
            {cidades_options_html}
        </select>
    </div>
</div>
<p id="count-label" style="max-width:1200px;margin:-16px auto 20px;padding:0 24px;font-size:11px;color:#aaa;font-family:'Source Sans 3',sans-serif;">{len(eventos)} eventos</p>

<main class="grid">
    {cards_html}
    <p class="sem-resultado" id="sem-resultado">Nenhum evento encontrado para essa busca.</p>
</main>

<script>{JS}</script>
<footer>
    RADAR &nbsp;·&nbsp; Ribeirão Preto e Região &nbsp;·&nbsp; 2026
    &nbsp;&nbsp;|&nbsp;&nbsp;
    Desenvolvido por <a href="https://linka.com.br" target="_blank">LINKA</a>
    &nbsp;&nbsp;|&nbsp;&nbsp;
    Dev Principal: Miguel Ribas
</footer>
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

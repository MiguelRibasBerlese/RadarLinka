import re
import requests, time, random
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from web_scraper import scrape_web_all

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
}

SYMPLA_URLS = [
    'https://www.sympla.com.br/eventos/ribeirao-preto-sp',
]

# Fallback de local quando o card não traz o campo — permite que o normalizador
# identifique a cidade correta em vez de usar o fallback 'Ribeirão Preto'.
_SLUG_PARA_LOCAL = {
    'ribeirao-preto':      'Ribeirão Preto - SP',
    'batatais':            'Batatais - SP',
    'sertaozinho':         'Sertãozinho - SP',
    'serrana':             'Serrana - SP',
    'jardinopolis':        'Jardinópolis - SP',
    'cravinhos':           'Cravinhos - SP',
    'brodowski':           'Brodowski - SP',
    'pontal':              'Pontal - SP',
    'santa-rosa-de-viterbo': 'Santa Rosa de Viterbo - SP',
    'pradopolis':          'Pradópolis - SP',
    'dumont':              'Dumont - SP',
    'serra-azul':          'Serra Azul - SP',
    'luis-antonio':        'Luís Antônio - SP',
    'guatapara':           'Guatapará - SP',
}

def scrape_sympla():
    eventos = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        for url in SYMPLA_URLS:
            cidade_slug = url.split('/')[-1].replace('-sp', '')
            local_fallback = _SLUG_PARA_LOCAL.get(cidade_slug, cidade_slug)
            try:
                page = browser.new_page()
                page.set_extra_http_headers({'User-Agent': HEADERS['User-Agent']})
                page.goto(url, wait_until='networkidle', timeout=20000)
                page.wait_for_timeout(3000)
                html = page.content()
                page.close()

                soup = BeautifulSoup(html, 'html.parser')
                cards = soup.select('a.sympla-card')

                if not cards:
                    print(f'[sympla:{cidade_slug}] 0 eventos — pulando')
                    continue

                n_adicionados = 0
                for card in cards:
                    titulo = card.get('data-name', '').strip()
                    if not titulo:
                        titulo_el = card.find(['h2', 'h3', 'h4', 'strong', 'span'])
                        titulo = titulo_el.get_text(strip=True) if titulo_el else ''

                    url_evento = card.get('href', '')
                    if url_evento and not url_evento.startswith('http'):
                        url_evento = 'https://www.sympla.com.br' + url_evento

                    local_el = card.find(class_=lambda c: c and 'local' in c.lower())
                    local = local_el.get_text(strip=True) if local_el else ''
                    if not local:
                        local = local_fallback

                    texto_card = card.get_text(' ', strip=True)
                    data_match = re.search(
                        r'(Segunda|Ter[cç]a|Quarta|Quinta|Sexta|S[aá]bado|Domingo)'
                        r',?\s+\d{1,2}\s+de\s+\w+(?:\s+[aà]s\s+\d{1,2}:\d{2})?'
                        r'|\d{1,2}\s+de\s+\w+(?:\s+a\s+\d{1,2}\s+de\s+\w+)?(?:\s+de\s+\d{4})?',
                        texto_card, re.IGNORECASE
                    )
                    data_raw = data_match.group(0).strip() if data_match else ''

                    if titulo and len(titulo) > 5 and url_evento:
                        eventos.append({'titulo': titulo, 'url': url_evento,
                                        'local': local, 'data': data_raw,
                                        'fonte': 'sympla'})
                        n_adicionados += 1

                print(f'[sympla:{cidade_slug}] {n_adicionados} eventos')
                time.sleep(random.uniform(1.0, 2.0))

            except Exception as e:
                print(f'[WARN sympla:{cidade_slug}] {e}')
                continue

        browser.close()

    print(f'[scrape_sympla] {len(eventos)} eventos no total')
    return eventos

def scrape_ingresse():
    BASE = 'https://www.ingresse.com'
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_extra_http_headers({'User-Agent': HEADERS['User-Agent']})
            page.goto(f'{BASE}/search?city=ribeirao+preto', wait_until='networkidle')
            page.wait_for_timeout(5000)
            html = page.content()
            browser.close()
        soup = BeautifulSoup(html, 'html.parser')
        eventos = []
        cards = soup.select('[class*=swipper_card]')
        for card in cards:
            titulo_el = card.select_one('[class*=swipper_title]')
            titulo = titulo_el.get_text(strip=True) if titulo_el else ''
            contents = card.select('[class*=swipper_content]')
            local = contents[0].get_text(strip=True) if len(contents) > 0 else ''
            data = contents[1].get_text(strip=True) if len(contents) > 1 else ''
            link = card.find_parent('a') or card.find('a', href=True)
            href = link.get('href', '') if link else ''
            if href and not href.startswith('http'):
                href = BASE + href
            if titulo and len(titulo) > 5:
                eventos.append({'titulo': titulo, 'url': href, 'local': local, 'data': data, 'fonte': 'ingresse'})
        time.sleep(random.uniform(1.0, 2.0))
        print(f'[scrape_ingresse playwright] {len(eventos)} eventos encontrados')
        return eventos
    except Exception as e:
        print(f'[ERRO scrape_ingresse] {e}')
        return []

def scrape_emribeirao():
    # Paths to exclude — pure news, not events
    _NAO_EVENTO = ('/politica/', '/atualidades/', '/saude/', '/economia/', '/seguranca/')
    url = 'https://emribeirao.com/agenda-cultural-em-ribeirao-preto/'
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        soup = BeautifulSoup(resp.text, 'html.parser')
        eventos = []
        # td_module_1 is the WordPress article card class on this theme
        for card in soup.select('.td_module_1'):
            t = card.find(['h3', 'h2'])
            titulo = t.get_text(strip=True)[:120] if t else ''
            a = card.find('a', href=True)
            url_evento = a['href'] if a else ''
            # Skip non-event categories by URL path
            if any(p in url_evento for p in _NAO_EVENTO):
                continue
            if titulo and len(titulo) > 5 and url_evento:
                data_raw = fetch_date_emribeirao(url_evento)
                eventos.append({'titulo': titulo, 'url': url_evento,
                                'local': 'Ribeirão Preto', 'data': data_raw,
                                'fonte': 'emribeirao'})
                time.sleep(random.uniform(1.0, 2.0))
        print(f'[scrape_emribeirao] {len(eventos)} eventos encontrados')
        return eventos
    except Exception as e:
        print(f'[ERRO scrape_emribeirao] {e}')
        return []

def scrape_shopping():
    import json
    BASE = 'https://www.ribeiraoshopping.com.br'
    url = f'{BASE}/eventos/'
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        soup = BeautifulSoup(resp.text, 'html.parser')
        eventos = []
        # Events are embedded as JSON in data-props of .event_grid divs
        for grid in soup.select('.event_grid'):
            props_raw = grid.get('data-props', '{}')
            try:
                props = json.loads(props_raw)
            except Exception:
                continue
            # Skip "past events" grids
            if props.get('view_mode') == 'past':
                continue
            for ev in props.get('events', []):
                titulo = ev.get('title', '').strip()
                path = ev.get('get_absolute_url', '')
                url_evento = BASE + path if path else ''
                data = ev.get('start_date', '') or ev.get('duration', '')
                local = ev.get('location', 'RibeirãoShopping - Ribeirão Preto')
                if titulo and len(titulo) > 5:
                    eventos.append({
                        'titulo': titulo,
                        'url': url_evento,
                        'data': data,
                        'local': local or 'RibeirãoShopping - Ribeirão Preto',
                        'fonte': 'shopping'
                    })
        print(f'[scrape_shopping] {len(eventos)} eventos encontrados')
        return eventos
    except Exception as e:
        print(f'[ERRO scrape_shopping] {e}')
        return []

def fetch_date_emribeirao(url: str) -> str:
    """Visita a página individual do EmRibeirão e extrai a data do evento."""
    if not url:
        return ''
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(resp.text, 'html.parser')
        texto = soup.get_text(' ', strip=True)

        MESES = (
            'janeiro|fevereiro|março|abril|maio|junho|'
            'julho|agosto|setembro|outubro|novembro|dezembro'
        )

        # Padrão 1 — explícito: "Data: De 27 de abril a 1º de maio de 2026"
        m = re.search(
            rf'[Dd]ata[:\s]+(?:De\s+)?(\d{{1,2}}(?:º)?)\s+de\s+({MESES})'
            rf'(?:\s+a\s+\d{{1,2}}(?:º)?\s+de\s+(?:{MESES}))?'
            rf'(?:\s+de\s+(\d{{4}}))?',
            texto, re.IGNORECASE
        )
        if m:
            dia = m.group(1).replace('º', '').strip()
            mes = m.group(2).strip()
            ano = m.group(3) or str(__import__('datetime').date.today().year)
            return f'{dia} de {mes} de {ano}'

        # Padrão 2 — "no dia 8 de julho" / "acontece em 8 de julho de 2026"
        m = re.search(
            rf'(?:no dia|em|para)\s+(\d{{1,2}}(?:º)?)\s+de\s+({MESES})'
            rf'(?:\s+de\s+(\d{{4}}))?',
            texto, re.IGNORECASE
        )
        if m:
            dia = m.group(1).replace('º', '').strip()
            mes = m.group(2).strip()
            ano = m.group(3) or str(__import__('datetime').date.today().year)
            return f'{dia} de {mes} de {ano}'

        # Padrão 3 — qualquer "DD de mês de AAAA" no texto
        m = re.search(
            rf'(\d{{1,2}}(?:º)?)\s+de\s+({MESES})\s+de\s+(\d{{4}})',
            texto, re.IGNORECASE
        )
        if m:
            dia = m.group(1).replace('º', '').strip()
            mes = m.group(2).strip()
            ano = m.group(3).strip()
            return f'{dia} de {mes} de {ano}'

        return ''
    except Exception as e:
        print(f'[WARN fetch_date_emribeirao] {url}: {e}')
        return ''


# ── EVENTOON ──────────────────────────────────────────────────
def scrape_eventoon():
    url = 'https://www.eventoon.com.br/cidade/ribeirao-preto-sp'
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_extra_http_headers({'User-Agent': HEADERS['User-Agent']})
            page.goto(url, wait_until='domcontentloaded', timeout=45000)
            page.wait_for_timeout(5000)
            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, 'html.parser')
        eventos = []

        for bloco in soup.select('.col-md-2.col-sm-3.form-group'):
            try:
                pai = bloco.parent
                textos = [t.strip() for t in pai.get_text('\n').split('\n') if t.strip()]
                if len(textos) < 4:
                    continue

                titulo = textos[3]
                local  = textos[4] if len(textos) > 4 else ''
                data   = next((t for t in textos if re.match(r'\d{2}/\d{2}/\d{4}', t)), '')

                href = next((a['href'] for a in pai.find_all('a', href=True)
                             if 'evento' in a['href']), '')
                if href and not href.startswith('http'):
                    href = 'https://www.eventoon.com.br' + href

                if titulo and len(titulo) > 3:
                    eventos.append({'titulo': titulo, 'data': data,
                                    'local': local, 'url': href, 'fonte': 'eventoon'})
            except Exception:
                continue

        print(f'[scrape_eventoon] {len(eventos)} eventos encontrados')
        return eventos
    except Exception as e:
        print(f'[ERRO scrape_eventoon] {e}')
        return []


# ── SINDTUR ───────────────────────────────────────────────────
def scrape_sindtur():
    url = 'https://observatorio.sindtur.org.br/pesquisa/eventos/calendario-de-eventos/'
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_extra_http_headers({'User-Agent': HEADERS['User-Agent']})
            page.goto(url, wait_until='networkidle', timeout=30000)
            page.wait_for_timeout(2000)
            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, 'html.parser')
        eventos = []

        for artigo in soup.select('article[class*=tribe_events], article[class*=type-tribe]'):
            try:
                titulo_el = artigo.select_one('[class*=event-title], h2, h3')
                titulo    = titulo_el.get_text(strip=True) if titulo_el else ''

                time_el  = artigo.select_one('time[datetime]')
                data_iso = time_el['datetime'][:10] if time_el else ''

                local_el = artigo.select_one('[class*=venue], [class*=local]')
                local    = local_el.get_text(strip=True) if local_el else 'Ribeirão Preto'

                href   = artigo.select_one('a[href]')
                url_ev = href['href'] if href else ''

                if titulo:
                    eventos.append({'titulo': titulo, 'data': data_iso,
                                    'data_iso': data_iso, 'local': local,
                                    'url': url_ev, 'fonte': 'sindtur'})
            except Exception:
                continue

        print(f'[scrape_sindtur] {len(eventos)} eventos encontrados')
        return eventos
    except Exception as e:
        print(f'[ERRO scrape_sindtur] {e}')
        return []


# ── SONGKICK ──────────────────────────────────────────────────
def scrape_songkick():
    url = 'https://www.songkick.com/metro-areas/97701-brazil-ribeirao-preto'
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_extra_http_headers({'User-Agent': HEADERS['User-Agent']})
            page.goto(url, wait_until='domcontentloaded', timeout=45000)
            page.wait_for_timeout(5000)
            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, 'html.parser')
        eventos = []

        for item in soup.select('.event-listings-element'):
            try:
                time_el  = item.select_one('time[datetime]')
                data_iso = time_el['datetime'][:10] if time_el else ''

                partes  = [p.strip() for p in item.get_text('|').split('|') if p.strip()]
                titulo  = partes[0] if partes else ''
                local   = partes[1] if len(partes) > 1 else 'Ribeirão Preto'

                href = item.select_one('a[href]')
                if href:
                    h = href['href']
                    url_ev = h if h.startswith('http') else 'https://www.songkick.com' + h
                else:
                    url_ev = ''

                if titulo and len(titulo) > 2:
                    eventos.append({'titulo': titulo, 'data': data_iso,
                                    'data_iso': data_iso,
                                    'local': local + ' - Ribeirão Preto',
                                    'url': url_ev, 'fonte': 'songkick'})
            except Exception:
                continue

        print(f'[scrape_songkick] {len(eventos)} eventos encontrados')
        return eventos
    except Exception as e:
        print(f'[ERRO scrape_songkick] {e}')
        return []


# ── VARAL DIVERSO ─────────────────────────────────────────────
def scrape_varal():
    url = 'https://varaldiverso.com.br/editorias/shows/agenda-de-shows-de-2025-em-ribeirao-preto/'
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_extra_http_headers({'User-Agent': HEADERS['User-Agent']})
            page.goto(url, wait_until='networkidle', timeout=30000)
            page.wait_for_timeout(2000)
            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, 'html.parser')
        eventos = []

        for bq in soup.select('blockquote'):
            try:
                texto  = bq.get_text('\n', strip=True)
                linhas = [l.strip() for l in texto.split('\n') if l.strip()]
                if not linhas:
                    continue

                titulo = linhas[0]

                data_match = re.search(r'(\d{1,2})[\/\.](\d{1,2})', texto)
                if data_match:
                    dia = data_match.group(1).zfill(2)
                    mes = data_match.group(2).zfill(2)
                    data_iso = f'2026-{mes}-{dia}'
                else:
                    data_iso = ''

                local_match = re.search(r'\bno\s+([A-ZÀ-Ú][^,\n]+)', texto)
                local = local_match.group(1).strip() if local_match else 'Ribeirão Preto'

                href = bq.select_one('a[href]')
                url_ev = href['href'] if href else ''

                if titulo and len(titulo) > 3:
                    eventos.append({'titulo': titulo, 'data': data_iso,
                                    'local': local + ' - Ribeirão Preto',
                                    'url': url_ev, 'fonte': 'varal'})
            except Exception:
                continue

        print(f'[scrape_varal] {len(eventos)} eventos encontrados')
        return eventos
    except Exception as e:
        print(f'[ERRO scrape_varal] {e}')
        return []


def scrape_all():
    todos = []
    for fn in [
        scrape_sympla,
        scrape_emribeirao,
        scrape_shopping,
        scrape_eventoon,
        scrape_sindtur,
        scrape_songkick,
        scrape_varal,
    ]:
        try:
            resultado = fn()
            todos.extend(resultado)
            print(f'[OK] {fn.__name__}: {len(resultado)} eventos')
        except Exception as e:
            print(f'[FALHA] {fn.__name__}: {e}')

    # Fonte extra: busca na web via Groq Compound
    try:
        web_eventos = scrape_web_all()
        todos.extend(web_eventos)
        print(f'[OK] scrape_web_all: {len(web_eventos)} eventos')
    except Exception as e:
        print(f'[FALHA] scrape_web_all: {e}')

    return todos

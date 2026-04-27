import re
import requests, time, random
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
}

def scrape_sympla():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_extra_http_headers({'User-Agent': HEADERS['User-Agent']})
        page.goto('https://www.sympla.com.br/eventos/ribeirao-preto-sp', wait_until='networkidle')
        page.wait_for_timeout(4000)
        html = page.content()
        browser.close()
    soup = BeautifulSoup(html, 'html.parser')
    eventos = []
    cards = soup.select('a.sympla-card')
    for card in cards:
        titulo = card.get('data-name') or ''
        if not titulo:
            h3 = card.find('h3')
            titulo = h3.get_text(strip=True) if h3 else ''
        url_evento = card.get('href', '')
        local_el = card.find('p')
        local = local_el.get_text(strip=True) if local_el else ''
        # Extrai data do texto do card via regex (classes são hashes CSS — não usar seletores)
        texto_card = card.get_text(' ', strip=True)
        data_match = re.search(
            r'(Segunda|Ter[cç]a|Quarta|Quinta|Sexta|S[aá]bado|Domingo)'
            r',?\s+\d{1,2}\s+de\s+\w+(?:\s+[aà]s\s+\d{1,2}:\d{2})?'
            r'|\d{1,2}\s+de\s+\w+(?:\s+a\s+\d{1,2}\s+de\s+\w+)?(?:\s+de\s+\d{4})?',
            texto_card, re.IGNORECASE
        )
        data_raw = data_match.group(0).strip() if data_match else ''
        if titulo and len(titulo) > 5 and url_evento:
            eventos.append({'titulo': titulo, 'url': url_evento, 'local': local,
                            'data': data_raw, 'fonte': 'sympla'})
    time.sleep(random.uniform(1.0, 2.0))
    print(f'[scrape_sympla playwright] {len(eventos)} eventos encontrados')
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


def scrape_all():
    todos = []
    for fn in [scrape_sympla, scrape_emribeirao, scrape_shopping]:
        try:
            resultado = fn()
            todos.extend(resultado)
            print(f'[OK] {fn.__name__}: {len(resultado)} eventos')
        except Exception as e:
            print(f'[FALHA] {fn.__name__}: {e}')
    return todos

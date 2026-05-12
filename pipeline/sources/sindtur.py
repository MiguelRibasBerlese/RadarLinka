import requests, time, random
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from ..settings import HEADERS


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

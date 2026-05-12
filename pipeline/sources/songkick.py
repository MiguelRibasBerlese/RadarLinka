import requests, time, random
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from ..settings import HEADERS


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

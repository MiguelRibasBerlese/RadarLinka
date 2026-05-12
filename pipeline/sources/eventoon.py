import re
import requests, time, random
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from ..settings import HEADERS


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

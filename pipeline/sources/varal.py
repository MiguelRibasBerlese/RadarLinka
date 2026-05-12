import re
import requests, time, random
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from ..settings import HEADERS


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

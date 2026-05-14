import re, time, random
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from ..settings import HEADERS

SYMPLA_URLS = [
    # Ribeirão Preto e região metropolitana
    'https://www.sympla.com.br/eventos/ribeirao-preto-sp',
    'https://www.sympla.com.br/eventos/batatais-sp',
    'https://www.sympla.com.br/eventos/sertaozinho-sp',
    'https://www.sympla.com.br/eventos/serrana-sp',
    'https://www.sympla.com.br/eventos/jardinopolis-sp',
    'https://www.sympla.com.br/eventos/cravinhos-sp',
    'https://www.sympla.com.br/eventos/brodowski-sp',
    'https://www.sympla.com.br/eventos/pontal-sp',
    'https://www.sympla.com.br/eventos/santa-rosa-de-viterbo-sp',
    'https://www.sympla.com.br/eventos/pradopolis-sp',
    'https://www.sympla.com.br/eventos/dumont-sp',
    'https://www.sympla.com.br/eventos/serra-azul-sp',
    'https://www.sympla.com.br/eventos/luis-antonio-sp',
    'https://www.sympla.com.br/eventos/guatapara-sp',
    # Até 100km
    'https://www.sympla.com.br/eventos/franca-sp',
    'https://www.sympla.com.br/eventos/araraquara-sp',
    'https://www.sympla.com.br/eventos/barretos-sp',
    'https://www.sympla.com.br/eventos/jaboticabal-sp',
    'https://www.sympla.com.br/eventos/bebedouro-sp',
    'https://www.sympla.com.br/eventos/guariba-sp',
    'https://www.sympla.com.br/eventos/monte-alto-sp',
    # 100km a 200km
    'https://www.sympla.com.br/eventos/sao-jose-do-rio-preto-sp',
    'https://www.sympla.com.br/eventos/campinas-sp',
    'https://www.sympla.com.br/eventos/uberaba-mg',
]

_SLUG_PARA_LOCAL = {
    'ribeirao-preto':         'Ribeirão Preto - SP',
    'batatais':               'Batatais - SP',
    'sertaozinho':            'Sertãozinho - SP',
    'serrana':                'Serrana - SP',
    'jardinopolis':           'Jardinópolis - SP',
    'cravinhos':              'Cravinhos - SP',
    'brodowski':              'Brodowski - SP',
    'pontal':                 'Pontal - SP',
    'santa-rosa-de-viterbo':  'Santa Rosa de Viterbo - SP',
    'pradopolis':             'Pradópolis - SP',
    'dumont':                 'Dumont - SP',
    'serra-azul':             'Serra Azul - SP',
    'luis-antonio':           'Luís Antônio - SP',
    'guatapara':              'Guatapará - SP',
    'franca':                 'Franca - SP',
    'araraquara':             'Araraquara - SP',
    'barretos':               'Barretos - SP',
    'jaboticabal':            'Jaboticabal - SP',
    'bebedouro':              'Bebedouro - SP',
    'guariba':                'Guariba - SP',
    'monte-alto':             'Monte Alto - SP',
    'sao-jose-do-rio-preto':  'São José do Rio Preto - SP',
    'campinas':               'Campinas - SP',
    'uberaba':                'Uberaba - MG',
}


def scrape_sympla():
    eventos = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        for url in SYMPLA_URLS:
            cidade_slug = url.split('/')[-1].replace('-sp', '').replace('-mg', '')
            local_fallback = _SLUG_PARA_LOCAL.get(cidade_slug, cidade_slug)
            try:
                page = browser.new_page()
                page.set_extra_http_headers({'User-Agent': HEADERS['User-Agent']})
                page.goto(url, wait_until='networkidle', timeout=35000)
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
                        cidade_nome = local_fallback.split(' - ')[0].strip()
                        eventos.append({'titulo': titulo, 'url': url_evento,
                                        'local': local, 'data': data_raw,
                                        'cidade': cidade_nome, 'fonte': 'sympla'})
                        n_adicionados += 1

                print(f'[sympla:{cidade_slug}] {n_adicionados} eventos')
                time.sleep(random.uniform(3.0, 5.0))

            except Exception as e:
                print(f'[WARN sympla:{cidade_slug}] {e}')
                continue

        browser.close()

    print(f'[scrape_sympla] {len(eventos)} eventos no total')
    return eventos

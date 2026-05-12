import re
import requests, time, random
from bs4 import BeautifulSoup
from ..settings import HEADERS


def fetch_date_emribeirao(url: str) -> str:
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


def scrape_emribeirao():
    _NAO_EVENTO = ('/politica/', '/atualidades/', '/saude/', '/economia/', '/seguranca/')
    url = 'https://emribeirao.com/agenda-cultural-em-ribeirao-preto/'
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        soup = BeautifulSoup(resp.text, 'html.parser')
        eventos = []
        for card in soup.select('.td_module_1'):
            t = card.find(['h3', 'h2'])
            titulo = t.get_text(strip=True)[:120] if t else ''
            a = card.find('a', href=True)
            url_evento = a['href'] if a else ''
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

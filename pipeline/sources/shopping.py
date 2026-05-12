import json
import requests, time, random
from bs4 import BeautifulSoup
from ..settings import HEADERS


def scrape_shopping():
    BASE = 'https://www.ribeiraoshopping.com.br'
    url = f'{BASE}/eventos/'
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        soup = BeautifulSoup(resp.text, 'html.parser')
        eventos = []
        for grid in soup.select('.event_grid'):
            props_raw = grid.get('data-props', '{}')
            try:
                props = json.loads(props_raw)
            except Exception:
                continue
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

import requests, time, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from config import SEARCHAPI_KEY

BUSCAS = [
    'eventos Ribeirão Preto',
    'shows Ribeirão Preto',
    'festas Ribeirão Preto',
    'teatro Ribeirão Preto',
]

BASE_URL = 'https://www.searchapi.io/api/v1/search'

def log(msg, emoji=''):
    print(f'{emoji}  {msg}', flush=True)

def barra(atual, total, largura=30):
    preenchido = int(largura * atual / total)
    b = '█' * preenchido + '░' * (largura - preenchido)
    pct = int(100 * atual / total)
    print(f'\r  [{b}] {pct}% ({atual}/{total})', end='', flush=True)
    if atual == total:
        print(flush=True)

def buscar_serp(termo: str) -> list:
    try:
        params = {
            'engine':  'google_events',
            'q':       termo,
            'api_key': SEARCHAPI_KEY,
            'hl':      'pt',
            'gl':      'br',
        }
        resp = requests.get(BASE_URL, params=params, timeout=30)
        data = resp.json()

        if resp.status_code != 200:
            log(f'Erro HTTP {resp.status_code}: {data.get("error", "?")}', '❌')
            return []

        eventos = []
        for ev in data.get('events', []):
            titulo = ev.get('title', '')

            # Data: {'day': '14', 'month': 'jun.'} ou string em duration
            date_info = ev.get('date', {})
            if isinstance(date_info, dict):
                dia = date_info.get('day', '')
                mes = date_info.get('month', '').rstrip('.')
                data_ev = f'{dia} de {mes}' if dia and mes else ev.get('duration', '')
            else:
                data_ev = str(date_info)

            # Local: campo 'location' tem o nome do venue; 'address' tem endereço
            local = ev.get('location', '') or ev.get('address', '') or 'Ribeirão Preto'

            url = ev.get('link', '')

            if titulo:
                eventos.append({
                    'titulo':          titulo,
                    'data':            data_ev,
                    'local':           local + ' - Ribeirão Preto',
                    'url':             url,
                    'descricao_bruta': ev.get('description', ''),
                    'fonte':           'searchapi',
                })
        return eventos

    except Exception as e:
        log(f'Erro na busca "{termo}": {e}', '❌')
        return []

def scrape_serp_all() -> list:
    log('Iniciando busca Google Events via SearchAPI.io...', '🔍')
    log(f'Total de buscas: {len(BUSCAS)} (de 100 disponíveis/mês)', 'ℹ️')
    print(flush=True)

    todos  = []
    vistos = set()

    for i, termo in enumerate(BUSCAS, 1):
        log(f'Busca {i}/{len(BUSCAS)}: "{termo}"', '🔎')
        barra(0, 1)
        eventos = buscar_serp(termo)
        barra(1, 1)

        novos = 0
        for ev in eventos:
            chave = ev['titulo'].lower().strip()[:50]
            if chave not in vistos:
                vistos.add(chave)
                todos.append(ev)
                novos += 1

        log(f'  → {len(eventos)} encontrados · {novos} novos · {len(eventos) - novos} duplicatas', '✅')

        if i < len(BUSCAS):
            log('  Aguardando 2s...', '⏳')
            time.sleep(2)
        print(flush=True)

    log(f'SearchAPI concluída: {len(todos)} eventos únicos', '🎯')
    return todos

if __name__ == '__main__':
    eventos = scrape_serp_all()
    print(f'\nEventos encontrados ({len(eventos)}):')
    for ev in eventos:
        print(f"  [{ev.get('data', '?')}] {ev.get('titulo', '')[:60]}")
        print(f"  Local: {ev.get('local', '')[:50]}")
        print(f"  URL: {ev.get('url', '')[:60]}")
        print()

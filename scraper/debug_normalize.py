import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, 'scraper')

from event_scraper import scrape_all
from event_normalizer import normalize

print('=== Coletando eventos (sem Groq) ===\n')
brutos = scrape_all()
normalizados = [normalize(e, e['fonte']) for e in brutos]
normalizados = [e for e in normalizados if e is not None]

# Conta por fonte
from collections import defaultdict
com_data   = defaultdict(list)
sem_data   = defaultdict(list)

for e in normalizados:
    if e['data_iso']:
        com_data[e['fonte']].append(e)
    else:
        sem_data[e['fonte']].append(e)

fontes = ['sympla', 'emribeirao', 'shopping']
total_com = sum(len(v) for v in com_data.values())
total_sem = sum(len(v) for v in sem_data.values())

print(f'Total normalizados : {len(normalizados)}')
print(f'Com data_iso       : {total_com}')
print(f'Sem data_iso       : {total_sem}')
print()

# Exemplos com data
print('=== 1 exemplo com data_iso por fonte ===')
for fonte in fontes:
    if com_data[fonte]:
        e = com_data[fonte][0]
        print(f'[{fonte}] {e["titulo"][:60]}')
        print(f'         data_iso={e["data_iso"]}  local={e["local"][:50]}')
    else:
        print(f'[{fonte}] — nenhum evento com data_iso preenchida')
print()

# Fontes sem data — mostra campo 'data' bruto dos eventos originais
print('=== Dados brutos de fontes com 0 datas ===')
brutos_por_fonte = defaultdict(list)
for e in brutos:
    brutos_por_fonte[e['fonte']].append(e)

for fonte in fontes:
    if not com_data[fonte] and brutos_por_fonte[fonte]:
        print(f'\n--- {fonte.upper()}: campo "data" dos primeiros 3 brutos ---')
        for e in brutos_por_fonte[fonte][:3]:
            print(f'  titulo : {e.get("titulo","")[:60]}')
            print(f'  data   : {repr(e.get("data",""))}')
            print()

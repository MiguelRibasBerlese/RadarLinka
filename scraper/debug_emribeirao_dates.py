import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, 'scraper')

from event_scraper import scrape_emribeirao
from event_normalizer import normalize

eventos = scrape_emribeirao()
normalizados = [normalize(e, 'emribeirao') for e in eventos]
normalizados = [e for e in normalizados if e]

com_data = [e for e in normalizados if e['data_iso']]
sem_data = [e for e in normalizados if not e['data_iso']]

print(f'Com data_iso: {len(com_data)}')
print(f'Sem data_iso: {len(sem_data)}')

print('\nCom data:')
for e in com_data:
    print(f'  [{e["data_iso"]}] {e["titulo"][:50]}')

print('\nSem data (primeiros 3):')
for e in sem_data[:3]:
    print(f'  [sem data] {e["titulo"][:50]}')
    print(f'  URL: {e["url"]}')

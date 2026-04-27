import sys
sys.path.insert(0, 'scraper')
from event_scraper import scrape_all
from event_normalizer import normalize

brutos = scrape_all()
normalizados = [normalize(e, e['fonte']) for e in brutos]
normalizados = [e for e in normalizados if e is not None]
print(f'Brutos: {len(brutos)} -> Normalizados (filtrados): {len(normalizados)}')
for e in normalizados[:3]:
    print(e)

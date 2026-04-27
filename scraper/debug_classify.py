import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scraper'))
from event_scraper import scrape_all
from event_normalizer import normalize
from ai_classifier import classify

brutos = scrape_all()
normalizados = [normalize(e, e['fonte']) for e in brutos]
normalizados = [e for e in normalizados if e is not None]
print(f'\n{len(normalizados)} eventos para classificar...\n')

for ev in normalizados:
    resultado = classify(ev)
    ev.update(resultado)
    print(f'[{ev["categoria"]:12}] {ev["titulo"][:60]}')
    if ev["narrativa_ia"]:
        print(f'               -> {ev["narrativa_ia"][:80]}')

print(f'\nConcluido: {len(normalizados)} eventos classificados.')

categorias = {}
for ev in normalizados:
    cat = ev["categoria"]
    categorias[cat] = categorias.get(cat, 0) + 1
print('\nDistribuicao por categoria:')
for cat, n in sorted(categorias.items(), key=lambda x: -x[1]):
    print(f'  {cat}: {n}')

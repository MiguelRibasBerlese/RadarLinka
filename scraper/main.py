import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from event_scraper import scrape_all
from event_normalizer import normalize
from ai_classifier import classify

OUTPUT_JSON = os.path.join(os.path.dirname(__file__), '..', 'web', 'events.json')

def run():
    print('[1/3] Coletando eventos...')
    brutos = scrape_all()
    print(f'      {len(brutos)} eventos brutos coletados')

    print('[2/3] Normalizando e filtrando...')
    normalizados = [normalize(e, e['fonte']) for e in brutos]
    normalizados = [e for e in normalizados if e is not None]
    print(f'      {len(normalizados)} eventos validos apos filtro geografico')

    print(f'[3/3] Classificando com IA (~{len(normalizados) * 2}s)...')
    classificados = []
    for i, ev in enumerate(normalizados, 1):
        resultado = classify(ev)
        ev.update(resultado)
        classificados.append(ev)
        print(f'      [{i:02d}/{len(normalizados)}] [{ev["categoria"]:12}] {ev["titulo"][:50]}')

    # Salva JSON local (fallback para renderer enquanto Sheets nao esta configurado)
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(classificados, f, ensure_ascii=False, indent=2)
    print(f'\n[OK] {len(classificados)} eventos salvos em web/events.json')

    # Distribuicao por categoria
    cats = {}
    for ev in classificados:
        cats[ev['categoria']] = cats.get(ev['categoria'], 0) + 1
    print('\nDistribuicao:')
    for cat, n in sorted(cats.items(), key=lambda x: -x[1]):
        print(f'  {cat}: {n}')

    return classificados

if __name__ == '__main__':
    run()

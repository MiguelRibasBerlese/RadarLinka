import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from web_scraper import buscar_eventos_web

for cidade in ['Ribeirão Preto', 'Campinas']:
    eventos = buscar_eventos_web(cidade)
    for ev in eventos:
        print(f"  [{ev.get('data_iso','?')}] {ev.get('titulo','')[:60]}")
        print(f"  URL: {ev.get('url','')[:60]}")
        print()

import json, sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
from ai_classifier import classify

EVENTS_JSON = os.path.join(os.path.dirname(__file__), '..', 'web', 'events.json')

with open(EVENTS_JSON, encoding='utf-8') as f:
    eventos = json.load(f)

print(f'Reclassificando {len(eventos)} eventos com novo prompt...')
print(f'Tempo estimado: ~{len(eventos) * 5 // 60}min {len(eventos) * 5 % 60}s\n')

for i, ev in enumerate(eventos, 1):
    resultado = classify(ev)
    ev['categoria']   = resultado['categoria']
    ev['narrativa_ia'] = resultado['narrativa_ia']
    print(f'[{i:03d}/{len(eventos)}] [{ev["categoria"]:12}] {ev["titulo"][:55]}')

with open(EVENTS_JSON, 'w', encoding='utf-8') as f:
    json.dump(eventos, f, ensure_ascii=False, indent=2)

# Distribuição final
cats = {}
for ev in eventos:
    cats[ev['categoria']] = cats.get(ev['categoria'], 0) + 1
print('\n=== Distribuição final ===')
for cat, n in sorted(cats.items(), key=lambda x: -x[1]):
    print(f'  {cat}: {n}')
print(f'\n✅ {len(eventos)} eventos salvos em events.json')

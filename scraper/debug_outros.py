import json

with open('C:/Radar/web/events.json', encoding='utf-8') as f:
    eventos = json.load(f)

outros = [e for e in eventos if e.get('categoria') == 'Outro']
print(f'Total "Outro": {len(outros)}\n')

for e in outros:
    print(f'Título:    {e["titulo"][:80]}')
    print(f'Local:     {e["local"][:60]}')
    print(f'Narrativa: {e["narrativa_ia"][:80]}')
    print('---')

import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from ai_classifier import classificar_por_regras

with open('../web/events.json', encoding='utf-8') as f:
    eventos = json.load(f)

por_regra  = {}
por_groq   = []

for ev in eventos:
    cat = classificar_por_regras(ev.get('titulo', ''), ev.get('descricao_bruta', ''))
    if cat:
        por_regra[cat] = por_regra.get(cat, 0) + 1
    else:
        por_groq.append(ev.get('titulo', '?'))

total     = len(eventos)
n_regra   = sum(por_regra.values())
n_groq    = len(por_groq)
pct_regra = int(100 * n_regra / total) if total else 0

print(f'Total de eventos : {total}')
print(f'Por regras       : {n_regra} ({pct_regra}%)')
print(f'Precisam do Groq : {n_groq} ({100 - pct_regra}%)')
print(f'Economia de tokens: ~{pct_regra}%')
print()
print('Distribuição por categoria (regras):')
for cat, n in sorted(por_regra.items(), key=lambda x: -x[1]):
    print(f'  {cat:<14} {"#" * n} ({n})')
print()
print('Eventos que vao para o Groq:')
for t in por_groq:
    print(f'  - {t}')

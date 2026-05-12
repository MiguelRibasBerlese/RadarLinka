import json, sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
from event_scraper import scrape_all
from event_normalizer import normalize
from ai_classifier import classify

OUTPUT_JSON = os.path.join(os.path.dirname(__file__), '..', 'web', 'events.json')

def barra_progresso(atual, total, largura=40, prefixo=''):
    preenchido = int(largura * atual / total)
    b = '█' * preenchido + '░' * (largura - preenchido)
    pct = int(100 * atual / total)
    print(f'\r  {prefixo} [{b}] {pct}% ({atual}/{total})',
          end='', flush=True)
    if atual == total:
        print(flush=True)

def separador(titulo=''):
    linha = '═' * 52
    if titulo:
        print(f'\n  ╔{linha}╗', flush=True)
        print(f'  ║  {titulo:<50}║', flush=True)
        print(f'  ╚{linha}╝', flush=True)
    else:
        print(f'  {"─"*52}', flush=True)

def run():
    inicio = time.time()
    separador('● RADAR — Pipeline Completo')

    # ── COLETA ──────────────────────────────────────────
    separador('ETAPA 1/3 — Coleta de Eventos')
    brutos = scrape_all()
    print(f'\n  📦 Total bruto coletado: {len(brutos)} eventos', flush=True)

    # ── NORMALIZAÇÃO ────────────────────────────────────
    separador('ETAPA 2/3 — Normalização e Filtro Geográfico')
    print(f'  Processando {len(brutos)} eventos...', flush=True)

    normalizados = []
    descartados  = 0
    for i, ev in enumerate(brutos, 1):
        r = normalize(ev, ev.get('fonte', ''))
        if r:
            normalizados.append(r)
        else:
            descartados += 1
        barra_progresso(i, len(brutos), prefixo='Normalizando')

    # Deduplicação por URL/título
    vistos = set()
    unicos = []
    for ev in normalizados:
        chave = ev.get('url', '') or ev.get('titulo', '')
        if chave not in vistos:
            vistos.add(chave)
            unicos.append(ev)
    dupes = len(normalizados) - len(unicos)
    normalizados = unicos

    print(f'\n  ✅ {len(normalizados)} eventos válidos', flush=True)
    print(f'  🗑️  {descartados} descartados (fora da região ou sem dados)', flush=True)
    if dupes:
        print(f'  🔁 {dupes} duplicatas removidas', flush=True)

    # ── CLASSIFICAÇÃO IA ────────────────────────────────
    separador('ETAPA 3/3 — Classificação por IA (Groq)')
    total = len(normalizados)
    tempo_est = total * 5
    print(f'  {total} eventos para classificar', flush=True)
    print(f'  ⏱️  Tempo estimado: ~{tempo_est//60}min {tempo_est%60}s', flush=True)
    print(flush=True)

    classificados = []
    contagem_cats = {}
    inicio_ia = time.time()

    for i, ev in enumerate(normalizados, 1):
        resultado = classify(ev)
        ev.update(resultado)
        classificados.append(ev)

        cat = ev['categoria']
        contagem_cats[cat] = contagem_cats.get(cat, 0) + 1

        decorrido = time.time() - inicio_ia
        eta = int((decorrido / i) * (total - i)) if i > 0 else 0
        eta_str = f'{eta//60}m{eta%60:02d}s' if eta >= 60 else f'{eta}s'

        print(f'  [{i:03d}/{total}] [{cat:<12}] {ev["titulo"][:45]}  (ETA: ~{eta_str})',
              flush=True)

    # ── SALVAR ──────────────────────────────────────────
    separador('Salvando Resultados')
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(classificados, f, ensure_ascii=False, indent=2)
    print(f'  💾 {len(classificados)} eventos salvos em web/events.json', flush=True)

    # ── RESUMO FINAL ────────────────────────────────────
    total_tempo = int(time.time() - inicio)
    separador('Resumo Final')
    print(f'  ✅ Pipeline concluído em {total_tempo//60}m{total_tempo%60:02d}s\n', flush=True)
    print(f'  Distribuição por categoria:', flush=True)
    for cat, n in sorted(contagem_cats.items(), key=lambda x: -x[1]):
        barra_cat = '█' * n
        print(f'  {cat:<14} {barra_cat} ({n})', flush=True)
    print(flush=True)

    return classificados

if __name__ == '__main__':
    run()

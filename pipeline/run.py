import time, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def _com_retry(fn, tentativas=2, pausa=6):
    for i in range(tentativas + 1):
        try:
            return fn()
        except Exception as e:
            if i == tentativas:
                raise
            print(f'  ⚠️  Tentativa {i + 1} falhou ({e}). Retentando em {pausa}s...', flush=True)
            time.sleep(pausa)

from pipeline.sources import (
    scrape_sympla, scrape_eventoon, scrape_sindtur,
    scrape_songkick, scrape_varal, scrape_emribeirao,
    scrape_shopping, scrape_searchapi_all,
)
from pipeline.processors import normalize, classify
from pipeline.storage import save_events

FONTES = [
    scrape_sympla, scrape_emribeirao, scrape_shopping,
    scrape_eventoon, scrape_sindtur, scrape_songkick,
    scrape_varal,
]


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
    brutos = []
    total_fontes = len(FONTES) + 1  # +1 SearchAPI

    for i, fn in enumerate(FONTES, 1):
        nome = fn.__name__.replace('scrape_', '')
        print(f'  [{i}/{total_fontes}] {nome}...', flush=True)
        try:
            resultado = _com_retry(fn)
            brutos.extend(resultado)
            print(f'  ✅ {len(resultado)} eventos\n', flush=True)
        except Exception as e:
            print(f'  ❌ Falha após retentativas: {e}\n', flush=True)

    print(f'  [{total_fontes}/{total_fontes}] SearchAPI (Google Events)...', flush=True)
    try:
        serp = _com_retry(scrape_searchapi_all)
        brutos.extend(serp)
        print(f'  ✅ {len(serp)} eventos do Google\n', flush=True)
    except Exception as e:
        print(f'  ❌ SearchAPI falhou após retentativas: {e}\n', flush=True)

    print(f'  📦 Total bruto: {len(brutos)} eventos', flush=True)

    # ── NORMALIZAÇÃO ────────────────────────────────────
    separador('ETAPA 2/3 — Normalização e Filtro')
    normalizados = []
    for i, ev in enumerate(brutos):
        r = normalize(ev, ev.get('fonte', ''))
        if r:
            normalizados.append(r)
        barra_progresso(i+1, len(brutos), prefixo='Normalizando')
    print(f'\n  ✅ {len(normalizados)} eventos válidos', flush=True)

    # ── DEDUPLICAÇÃO ────────────────────────────────────
    separador('Deduplicacao')
    vistos_url    = set()
    vistos_titulo = set()
    unicos = []
    for ev in normalizados:
        url    = (ev.get('url') or '').strip().lower()
        titulo = ''.join(c for c in ev.get('titulo', '').lower() if c.isalnum())[:60]
        chave  = url if url else titulo
        if not chave:
            continue
        if chave in vistos_url:
            continue
        vistos_url.add(chave)
        if titulo in vistos_titulo:
            continue
        vistos_titulo.add(titulo)
        unicos.append(ev)
    removidos = len(normalizados) - len(unicos)
    print(f'  {len(unicos)} unicos · {removidos} duplicatas removidas', flush=True)
    normalizados = unicos

    # ── CLASSIFICAÇÃO ────────────────────────────────────
    separador('ETAPA 3/3 — Classificação por IA')
    total = len(normalizados)
    tempo_est = total * 2
    print(f'  {total} eventos · ETA ~{tempo_est//60}m{tempo_est%60}s', flush=True)
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
        barra_progresso(i, total, prefixo='Classificando')
        print(f'  [{i:03d}/{total}] [{cat:<12}] {ev["titulo"][:45]}',
              flush=True)

    # ── SALVAR ──────────────────────────────────────────
    separador('Salvando')
    save_events(classificados)

    # ── RESUMO ──────────────────────────────────────────
    total_tempo = int(time.time() - inicio)
    separador('Resumo Final')
    print(f'  ✅ {len(classificados)} eventos em '
          f'{total_tempo//60}m{total_tempo%60:02d}s\n', flush=True)
    for cat, n in sorted(contagem_cats.items(), key=lambda x: -x[1]):
        print(f'  {cat:<14} {"█"*n} ({n})', flush=True)
    print(flush=True)

    return classificados


if __name__ == '__main__':
    run()

import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scraper'))

EVENTOS_MOCK = [
    {
        "titulo": "Show de Rock",
        "data_iso": "2026-05-10",
        "local": "Ribeirao Preto",
        "url": "http://x.com/1",
        "fonte": "sympla",
        "descricao_bruta": "",
        "categoria": "Show",
        "narrativa_ia": "Grande show de rock no coracao de Ribeirao Preto."
    },
    {
        "titulo": "Feira de Artesanato",
        "data_iso": "",
        "local": "Centro de Ribeirao Preto",
        "url": "http://x.com/2",
        "fonte": "shopping",
        "descricao_bruta": "",
        "categoria": "Feira",
        "narrativa_ia": "Artesaos locais expõem no centro da cidade."
    }
]

def test_renderer_gera_html_valido():
    from renderer import render
    html = render(eventos=EVENTOS_MOCK, stale=False)
    assert '<!DOCTYPE html>' in html
    assert 'RADAR' in html
    assert 'Show de Rock' in html
    assert 'Feira de Artesanato' in html

def test_renderer_exibe_banner_quando_stale():
    from renderer import render
    html = render(eventos=EVENTOS_MOCK, stale=True)
    assert 'stale' in html.lower() or 'desatualizad' in html.lower()

def test_renderer_badge_cor_correta():
    from renderer import render
    html = render(eventos=EVENTOS_MOCK, stale=False)
    assert '#C0392B' in html  # cor do badge Show

def test_renderer_sem_eventos_nao_quebra():
    from renderer import render
    html = render(eventos=[], stale=False)
    assert '<!DOCTYPE html>' in html
    assert 'RADAR' in html

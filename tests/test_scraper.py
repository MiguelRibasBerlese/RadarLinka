import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scraper'))
from event_scraper import scrape_sympla, scrape_emribeirao, scrape_shopping, scrape_all

def test_scrape_sympla_returns_list():
    result = scrape_sympla()
    assert isinstance(result, list), 'Deve retornar uma lista'
    assert len(result) > 0, 'Lista não pode estar vazia'
    primeiro = result[0]
    assert 'titulo' in primeiro or 'nome' in primeiro, 'Evento deve ter titulo'

def test_scrape_emribeirao_returns_list():
    result = scrape_emribeirao()
    assert isinstance(result, list), 'Deve retornar uma lista'
    print(f'[emribeirao] {len(result)} eventos')

def test_scrape_shopping_returns_list():
    result = scrape_shopping()
    assert isinstance(result, list), 'Deve retornar uma lista'
    print(f'[shopping] {len(result)} eventos')

def test_scrape_all_combines_sources():
    result = scrape_all()
    assert isinstance(result, list)
    assert len(result) > 0, 'scrape_all deve retornar ao menos 1 evento'
    fontes = {e['fonte'] for e in result}
    assert len(fontes) >= 2, f'scrape_all deve combinar ao menos 2 fontes, got: {fontes}'
    print(f'[scrape_all] {len(result)} eventos de fontes: {fontes}')

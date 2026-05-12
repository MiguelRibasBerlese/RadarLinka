import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from pipeline.sources import scrape_sympla, scrape_emribeirao, scrape_shopping

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

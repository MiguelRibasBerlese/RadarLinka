import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scraper'))
from event_normalizer import normalize

def test_normalize_retorna_schema_completo():
    ev = {'titulo': 'Show de Rock', 'data': '2026-05-10',
          'url': 'http://x.com/1', 'local': 'Ribeirão Preto'}
    r = normalize(ev, 'sympla')
    for campo in ['titulo', 'data_iso', 'local', 'url', 'fonte', 'descricao_bruta']:
        assert campo in r, f'Campo {campo} ausente'

def test_normalize_campo_ausente_vira_string_vazia():
    ev = {'titulo': 'Feira', 'url': 'http://x.com/2', 'local': 'Ribeirão Preto'}
    r = normalize(ev, 'sympla')
    assert r['descricao_bruta'] == ''

def test_normalize_descarta_evento_passado():
    ev = {'titulo': 'Evento Antigo', 'data': '2020-01-01',
          'url': 'http://x.com/3', 'local': 'Ribeirão Preto'}
    r = normalize(ev, 'sympla')
    assert r is None, 'Evento passado deve retornar None'

def test_normalize_descarta_evento_fora_de_rp_ingresse():
    ev = {'titulo': 'Show em SP', 'url': 'http://x.com/4',
          'local': 'Parque do Ibirapuera', 'data': '2026-06-01'}
    r = normalize(ev, 'ingresse')
    assert r is None, 'Evento fora de RP do Ingresse deve ser descartado'

def test_normalize_aceita_evento_de_rp_ingresse():
    ev = {'titulo': 'Festa em RP', 'url': 'http://x.com/5',
          'local': 'Ribeirão Preto - SP', 'data': '2026-06-15'}
    r = normalize(ev, 'ingresse')
    assert r is not None, 'Evento de RP deve ser aceito'

def test_normalize_descarta_ingresse_sem_local():
    ev = {'titulo': 'Evento sem local', 'url': 'http://x.com/6', 'data': '2026-07-01'}
    r = normalize(ev, 'ingresse')
    assert r is None, 'Evento do Ingresse sem local deve ser descartado'

def test_normalize_data_formato_ptbr():
    ev = {'titulo': 'Feira', 'data': '23 de maio de 2026',
          'url': 'http://x.com/7', 'local': 'Ribeirão Preto'}
    r = normalize(ev, 'ingresse')
    assert r is not None
    assert r['data_iso'] == '2026-05-23'

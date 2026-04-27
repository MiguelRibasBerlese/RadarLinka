import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scraper'))
from unittest.mock import patch, MagicMock
from ai_classifier import classify

CATEGORIAS = ['Show','Festa','Feira','Festival','Teatro','Esporte','Corporativo','Outro']

def test_classify_retorna_categoria_valida():
    mock_resp = MagicMock()
    mock_resp.choices[0].message.content = '{"categoria": "Show", "narrativa": "Evento incrivel em Ribeirao Preto."}'
    with patch('ai_classifier.client.chat.completions.create', return_value=mock_resp):
        ev = {'titulo':'Show de Rock','data_iso':'2026-05-10','local':'Ribeirao Preto','descricao_bruta':''}
        r = classify(ev)
        assert r['categoria'] in CATEGORIAS
        assert isinstance(r['narrativa_ia'], str)
        assert len(r['narrativa_ia']) > 0

def test_classify_categoria_fora_do_conjunto_vira_outro():
    mock_resp = MagicMock()
    mock_resp.choices[0].message.content = '{"categoria": "Balada", "narrativa": "Teste."}'
    with patch('ai_classifier.client.chat.completions.create', return_value=mock_resp):
        ev = {'titulo':'X','data_iso':'','local':'','descricao_bruta':''}
        r = classify(ev)
        assert r['categoria'] == 'Outro'

def test_classify_erro_api_retorna_outro():
    with patch('ai_classifier.client.chat.completions.create', side_effect=Exception('timeout')):
        ev = {'titulo':'X','data_iso':'','local':'','descricao_bruta':''}
        r = classify(ev)
        assert r['categoria'] == 'Outro'
        assert r['narrativa_ia'] == ''

def test_classify_json_malformado_retorna_outro():
    mock_resp = MagicMock()
    mock_resp.choices[0].message.content = 'texto livre sem json'
    with patch('ai_classifier.client.chat.completions.create', return_value=mock_resp):
        ev = {'titulo':'X','data_iso':'','local':'','descricao_bruta':''}
        r = classify(ev)
        assert r['categoria'] == 'Outro'

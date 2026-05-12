import sys, os, json, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

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


def test_save_events_cria_json_valido(tmp_path, monkeypatch):
    from pipeline import storage
    target = str(tmp_path / "events.json")
    monkeypatch.setattr(storage.data_store, 'EVENTS_JSON', target)
    storage.save_events(EVENTOS_MOCK)
    assert os.path.exists(target)
    with open(target, encoding='utf-8') as f:
        data = json.load(f)
    assert len(data) == 2
    assert data[0]['titulo'] == 'Show de Rock'


def test_load_events_retorna_lista_vazia_sem_arquivo(tmp_path, monkeypatch):
    from pipeline import storage
    target = str(tmp_path / "nao_existe.json")
    monkeypatch.setattr(storage.data_store, 'EVENTS_JSON', target)
    result = storage.load_events()
    assert result == []


def test_save_load_roundtrip(tmp_path, monkeypatch):
    from pipeline import storage
    target = str(tmp_path / "events.json")
    monkeypatch.setattr(storage.data_store, 'EVENTS_JSON', target)
    storage.save_events(EVENTOS_MOCK)
    result = storage.load_events()
    assert len(result) == len(EVENTOS_MOCK)
    assert result[1]['categoria'] == 'Feira'

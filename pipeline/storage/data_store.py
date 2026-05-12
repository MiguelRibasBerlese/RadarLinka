import json, os

EVENTS_JSON = os.path.join(
    os.path.dirname(__file__), '..', '..', 'public', 'data', 'events.json'
)


def save_events(eventos: list):
    os.makedirs(os.path.dirname(EVENTS_JSON), exist_ok=True)
    with open(EVENTS_JSON, 'w', encoding='utf-8') as f:
        json.dump(eventos, f, ensure_ascii=False, indent=2)
    print(f'[OK] {len(eventos)} eventos salvos', flush=True)


def load_events() -> list:
    try:
        with open(EVENTS_JSON, encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

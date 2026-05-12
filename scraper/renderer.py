import json, os
from datetime import datetime

EVENTS_JSON = os.path.join(os.path.dirname(__file__), '..', 'web', 'events.json')

def save_events(eventos: list) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(EVENTS_JSON)), exist_ok=True)
    with open(EVENTS_JSON, 'w', encoding='utf-8') as f:
        json.dump(eventos, f, ensure_ascii=False, indent=2)
    print(f'  💾 {len(eventos)} eventos salvos em web/events.json', flush=True)

def check_health() -> dict:
    try:
        with open(EVENTS_JSON, encoding='utf-8') as f:
            eventos = json.load(f)
        mtime = os.path.getmtime(EVENTS_JSON)
        age_h = (datetime.now().timestamp() - mtime) / 3600
        return {'count': len(eventos), 'age_hours': round(age_h, 1), 'stale': age_h > 48}
    except FileNotFoundError:
        return {'count': 0, 'age_hours': None, 'stale': True}

if __name__ == '__main__':
    info = check_health()
    print(f"events.json: {info['count']} eventos, {info['age_hours']}h atrás, stale={info['stale']}")

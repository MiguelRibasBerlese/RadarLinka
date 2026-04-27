from bs4 import BeautifulSoup
import json, re

for fonte in ['sympla', 'emribeirao', 'shopping']:
    path = f'C:/Radar/debug_detail_{fonte}.html'
    try:
        with open(path, encoding='utf-8') as f:
            html = f.read()
        soup = BeautifulSoup(html, 'html.parser')

        print(f'\n=== {fonte.upper()} ===')

        # JSON-LD
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if isinstance(data, list): data = data[0]
                if 'startDate' in data:
                    print(f'  JSON-LD startDate: {data["startDate"]}')
                if 'startDate' in str(data):
                    print(f'  JSON-LD contém startDate')
            except: pass

        # Tags <time>
        times = soup.find_all('time')
        for t in times[:3]:
            print(f'  <time>: datetime={t.get("datetime")} texto={t.get_text(strip=True)[:40]}')

        # Classes com data
        for cls in ['date', 'data', 'when', 'schedule', 'datetime', 'start']:
            els = soup.find_all(class_=re.compile(cls, re.I))
            for el in els[:2]:
                print(f'  .{cls}: {el.get_text(strip=True)[:60]}')

        # Meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('property','') + meta.get('name','')
            if any(x in name.lower() for x in ['date','time','event']):
                print(f'  <meta {name}>: {meta.get("content","")[:60]}')

    except FileNotFoundError:
        print(f'  [SKIP] arquivo nao encontrado')

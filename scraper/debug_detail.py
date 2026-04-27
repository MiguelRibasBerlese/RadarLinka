from playwright.sync_api import sync_playwright
import json, os

with open('C:/Radar/web/events.json', encoding='utf-8') as f:
    eventos = json.load(f)

urls = {
    'sympla':     next((e['url'] for e in eventos if e['fonte']=='sympla'), None),
    'emribeirao': next((e['url'] for e in eventos if e['fonte']=='emribeirao'), None),
    'shopping':   next((e['url'] for e in eventos if e['fonte']=='shopping'), None),
}

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    for fonte, url in urls.items():
        if not url:
            print(f'[SKIP] {fonte} sem URL')
            continue
        page = browser.new_page()
        page.goto(url, wait_until='networkidle', timeout=30000)
        page.wait_for_timeout(2000)
        html = page.content()
        path = f'C:/Radar/debug_detail_{fonte}.html'
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'[OK] {fonte}: {len(html)} bytes salvos em {path}')
        page.close()
    browser.close()

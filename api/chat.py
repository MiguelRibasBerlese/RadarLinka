import json, os
from datetime import date
from http.server import BaseHTTPRequestHandler
from groq import Groq

client = Groq(api_key=os.environ.get('GROQ_API_KEY'))

EVENTS_PATH = os.path.join(os.path.dirname(__file__), '..', 'web', 'events.json')
MAX_EVENTS  = 80

def load_events():
    try:
        with open(EVENTS_PATH, encoding='utf-8') as f:
            events = json.load(f)

        hoje = date.today().isoformat()
        futuros = [e for e in events if e.get('data_iso', '') >= hoje]
        futuros.sort(key=lambda e: e.get('data_iso', ''))

        resumo = []
        for e in futuros[:MAX_EVENTS]:
            url = e.get('url', '')
            linha = (
                f"- {e.get('titulo','')} | "
                f"{e.get('categoria','')} | "
                f"{e.get('data_iso','')} | "
                f"{e.get('local','').split('-')[0].strip()} | "
                f"{e.get('cidade','Ribeirão Preto')}"
                + (f" | URL: {url}" if url else "")
            )
            resumo.append(linha)
        return '\n'.join(resumo) or 'Nenhum evento futuro encontrado.'
    except:
        return 'Nenhum evento disponível no momento.'

SYSTEM_PROMPT = """Você é o RADAR Assistant — assistente de eventos
culturais de Ribeirão Preto e região (até 200km).

Você conhece a agenda completa desta semana. Quando o usuário
perguntar sobre eventos, responda com base na lista abaixo.

Regras:
- Seja direto e amigável
- Máximo 3-4 eventos por resposta (os mais relevantes)
- Para cada evento mencione: nome, data, cidade e categoria
- SEMPRE inclua o link do evento no formato exato: [Ver ingresso](URL)
- Se o evento não tiver URL, não inclua link
- Se não encontrar eventos para o critério, diga honestamente
- Responda sempre em português brasileiro
- Não invente eventos que não estão na lista

Formato de resposta exemplo:
🎵 **Show de Rock** — 23/05 · Ribeirão Preto
Noite de rock no Vat Rock Bar.
[Ver ingresso](https://sympla.com.br/evento)

Repita esse formato para cada evento encontrado.

EVENTOS DISPONÍVEIS:
{eventos}"""

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        try:
            length   = int(self.headers.get('Content-Length', 0))
            body     = json.loads(self.rfile.read(length))
            messages = body.get('messages', [])
            eventos  = load_events()

            response = client.chat.completions.create(
                model='llama-3.3-70b-versatile',
                messages=[
                    {'role': 'system', 'content': SYSTEM_PROMPT.format(eventos=eventos)},
                    *messages
                ],
                max_tokens=400,
                temperature=0.5,
            )

            reply = response.choices[0].message.content

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'reply': reply}).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def log_message(self, format, *args):
        pass

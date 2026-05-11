import json, os
from http.server import BaseHTTPRequestHandler
from groq import Groq

client = Groq(api_key=os.environ.get('GROQ_API_KEY'))

EVENTS_PATH = os.path.join(os.path.dirname(__file__), '..', 'web', 'events.json')

def load_events():
    try:
        with open(EVENTS_PATH, encoding='utf-8') as f:
            events = json.load(f)
        resumo = []
        for e in events:
            resumo.append(
                f"- {e.get('titulo','')} | {e.get('categoria','')} | "
                f"{e.get('data_iso','Data a confirmar')} | "
                f"{e.get('local','').split('-')[0].strip()} | "
                f"{e.get('cidade','Ribeirão Preto')}"
            )
        return '\n'.join(resumo)
    except:
        return 'Nenhum evento disponível no momento.'

SYSTEM_PROMPT = """Você é o RADAR Assistant — assistente de eventos culturais
de Ribeirão Preto e região (até 200km).

Você conhece a agenda completa desta semana. Quando o usuário perguntar
sobre eventos, responda com base na lista abaixo.

Regras:
- Seja direto e amigável
- Máximo 3-4 eventos por resposta (os mais relevantes)
- Mencione: nome, data, cidade e categoria
- Se não encontrar eventos para o critério, diga honestamente
- Responda sempre em português brasileiro
- Não invente eventos que não estão na lista

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

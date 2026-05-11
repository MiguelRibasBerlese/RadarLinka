import json, time, re
from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

CIDADES = [
    'Ribeirão Preto', 'Franca', 'Araraquara', 'Barretos',
    'Campinas', 'São José do Rio Preto', 'Uberaba',
    'Jaboticabal', 'Bebedouro', 'Serrana', 'Brodowski',
]

PROMPT_BUSCA = """Busque eventos culturais, shows, festas, festivais,
teatro, esporte e outros eventos que acontecerão em {cidade} nos
próximos 30 dias.

Retorne SOMENTE um JSON com esta estrutura, sem preamble:
{{
  "eventos": [
    {{
      "titulo": "Nome do evento",
      "data_iso": "YYYY-MM-DD ou vazio se não souber",
      "local": "Local do evento em {cidade}",
      "url": "URL do evento ou página de ingresso",
      "descricao_bruta": "Descrição curta do evento"
    }}
  ]
}}

Retorne no máximo 5 eventos por cidade.
Só eventos futuros. Só eventos reais com fonte verificável.
Se não encontrar eventos, retorne {{"eventos": []}}"""

def buscar_eventos_web(cidade: str, tentativa: int = 1) -> list:
    try:
        resp = client.chat.completions.create(
            model='compound-beta-mini',
            messages=[{
                'role': 'user',
                'content': PROMPT_BUSCA.format(cidade=cidade)
            }],
            max_tokens=1000,
            temperature=0.2,
        )
        content = resp.choices[0].message.content.strip()

        # Remove markdown se presente
        if '```' in content:
            content = content.split('```')[1]
            if content.startswith('json'):
                content = content[4:]

        data = json.loads(content)
        eventos = data.get('eventos', [])

        for ev in eventos:
            ev['fonte'] = 'web'
            ev['cidade_busca'] = cidade

        print(f'[web:{cidade}] {len(eventos)} eventos encontrados')
        time.sleep(30)  # intervalo generoso para respeitar TPM
        return eventos

    except Exception as e:
        err = str(e)
        # Rate limit — extrai tempo de espera e tenta novamente
        if '429' in err and tentativa <= 3:
            match = re.search(r'try again in ([\d.]+)s', err)
            wait = float(match.group(1)) + 5 if match else 35
            print(f'[web:{cidade}] rate limit, aguardando {wait:.0f}s (tentativa {tentativa}/3)...')
            time.sleep(wait)
            return buscar_eventos_web(cidade, tentativa + 1)
        print(f'[ERRO web:{cidade}] {e}')
        return []

def scrape_web_all() -> list:
    todos = []
    for cidade in CIDADES:
        eventos = buscar_eventos_web(cidade)
        todos.extend(eventos)
    print(f'[web TOTAL] {len(todos)} eventos da web')
    return todos

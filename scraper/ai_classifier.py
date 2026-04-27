import json, time
from groq import Groq
from config import GROQ_API_KEY, CATEGORIAS

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = (
    'Voce e um editor de jornal local de Ribeirao Preto, SP. '
    'Dado um evento, retorne SOMENTE um JSON com dois campos: '
    '"categoria" (exatamente uma de: Show, Festa, Feira, Festival, Teatro, Esporte, Corporativo, Outro) '
    'e "narrativa" (1-2 frases em portugues brasileiro, tom jornalistico, maximo 30 palavras, '
    'mencione Ribeirao Preto se relevante). '
    'Sem preamble, sem markdown, sem explicacao — apenas o JSON puro.'
)

def classify(evento: dict) -> dict:
    prompt = (
        f'Titulo: {evento.get("titulo", "")} | '
        f'Data: {evento.get("data_iso", "") or "nao informada"} | '
        f'Local: {evento.get("local", "") or "Ribeirao Preto"} | '
        f'Descricao: {evento.get("descricao_bruta", "") or "sem descricao"}'
    )
    try:
        resp = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user',   'content': prompt}
            ],
            temperature=0.3,
            max_tokens=120,
        )
        raw = resp.choices[0].message.content.strip()
        # Remove markdown se a IA ignorar a instrução
        if raw.startswith('```'):
            raw = raw.split('```')[1]
            if raw.startswith('json'):
                raw = raw[4:]
        data = json.loads(raw)
        categoria = data.get('categoria', 'Outro')
        if categoria not in CATEGORIAS:
            categoria = 'Outro'
        narrativa = str(data.get('narrativa', '')).strip()[:200]
        time.sleep(2)
        return {'categoria': categoria, 'narrativa_ia': narrativa}
    except json.JSONDecodeError:
        print(f'[WARN classify] JSON malformado para: {evento.get("titulo","?")}')
        return {'categoria': 'Outro', 'narrativa_ia': ''}
    except Exception as e:
        print(f'[ERRO classify] {e}')
        return {'categoria': 'Outro', 'narrativa_ia': ''}

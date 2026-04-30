import json, time
from groq import Groq
from config import GROQ_API_KEY, CATEGORIAS

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = (
    'Voce e um editor de jornal local do interior de Sao Paulo. '
    'Dado um evento, retorne SOMENTE um JSON com dois campos: '
    '"categoria" e "narrativa". '
    'Sem preamble, sem markdown, sem explicacao — apenas o JSON puro. '
    '\n\n'
    'CATEGORIAS VALIDAS (escolha exatamente uma):\n'
    '- Show: shows musicais, bandas, cantores, concertos, apresentacoes ao vivo\n'
    '- Festa: baladas, bailes, festas tematicas, carnaval, noites de festa\n'
    '- Feira: feiras de artesanato, feiras gastronomicas, feiras agropecuarias\n'
    '- Festival: festivais com multiplas atracoes, festivais culturais, rodeos\n'
    '- Teatro: pecas teatrais, musicais, opera, danca, espetaculos cênicos\n'
    '- Esporte: corridas, campeonatos, torneios, maratonas, eventos esportivos\n'
    '- Corporativo: congressos, palestras, summit, networking, jornadas academicas\n'
    '- Curso: workshops, cursos, oficinas, capacitacoes, aulas, treinamentos\n'
    '- Exposição: museus, exposicoes de arte, mostras, galerias, experiencias imersivas\n'
    '- Religioso: cultos, retiros espirituais, conferencias religiosas, acampamentos evangelicos\n'
    '- Turismo: passeios, experiencias turisticas, parques, ecoturismo, visitas guiadas\n'
    '- Infantil: eventos kids, parques infantis, espetaculos para criancas e familias\n'
    '- Outro: apenas quando nenhuma das categorias acima se aplica\n'
    '\n'
    'CAMPO narrativa: 1-2 frases em portugues brasileiro, '
    'tom jornalistico de colunista local, maximo 30 palavras. '
    'Mencione a cidade se relevante. '
    'NUNCA use "Outro" na narrativa — descreva o evento.'
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

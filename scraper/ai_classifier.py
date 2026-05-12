import json, time, unicodedata
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

# ── Classificação por regras (zero tokens) ──────────────────
REGRAS = {
    'Show': [
        'show', 'banda', 'cantor', 'cantora', 'concerto', 'ao vivo',
        'turne', 'apresentacao', 'musical',
        'sinfonica', 'orquestra', 'jazz', 'rock', 'samba',
        'pagode', 'forro', 'sertanejo', 'funk', 'rap', 'hip hop',
        'metal', 'pop', 'mpb', 'blues', 'reggae', 'stand-up', 'standup',
        'comedy', 'comedia', 'humorista', 'pianista', 'violonista',
        'cantor', 'tribute', 'cover', 'acustico', '- goa',
        'numanice', 'ribeirao comedy', 'ribeira comedy',
    ],
    'Festa': [
        'balada', 'festa', 'baile', 'noite', 'party', 'dj', 'club',
        'boate', 'carnaval', 'bloco', 'open bar', 'rave', 'trap',
        'house', 'eletronico', 'flashback', 'carnadoze', 'kiki ball',
        'ball da', 'arraial', 'arraia', 'arraia',
    ],
    'Feira': [
        'feira', 'mercado', 'artesanato', 'gastronomia', 'gastronomico',
        'agricola', 'agropecuaria', 'feirinha',
    ],
    'Festival': [
        'festival', 'rodeio', 'rodeo', 'joao rock', 'tardezinha',
        'lollapalooza', 'tomorrowland', 'bacon day', 'open air',
    ],
    'Teatro': [
        'teatro', 'theatro', 'peca', 'espetaculo', 'opera', 'danca', 'ballet',
        'bale', 'monologo', 'dramaturgia', 'sessao de freud',
        'montagem escolar', 'fabrica de chocolate',
    ],
    'Esporte': [
        'corrida', 'maratona', 'triathlon', 'ciclismo', 'futebol',
        'campeonato', 'torneio', 'esporte', 'esportivo', 'corrida de rua',
        '5k', '10k', 'natacao', 'atletismo', 'crossfit',
    ],
    'Corporativo': [
        'congresso', 'summit', 'conferencia', 'palestra',
        'seminario', 'jornada academica', 'simposio', 'forum',
        'networking', 'hackathon', 'inovacao', 'jornada de',
        'enfermagem', 'veterinaria', 'odontologia', 'clinica medica',
        'clinica cirurgica', 'e-commerce', 'ecommerce', 'experience',
        'intervencao', 'psicoses', 'pamv',
    ],
    'Curso': [
        'curso', 'capacitacao', 'treinamento', 'oficina',
        'formacao', 'certificacao', 'imersao', 'mentoria',
        'masterclass', 'bootcamp',
    ],
    'Exposicao': [
        'exposicao', 'museu', 'galeria', 'mostra',
        'instalacao', 'fotografia', 'imersiva', 'imersivo',
        'interativa', 'interativo',
    ],
    'Religioso': [
        'culto', 'retiro', 'acampamento', 'evangelico', 'catolico',
        'missa', 'louvor', 'adoracao', 'pregacao', 'adore', 'aviva',
        'pastor', 'igreja', 'reino de deus', 'monja', 'zen',
    ],
    'Turismo': [
        'passeio', 'tour', 'turismo', 'ecoturismo',
        'trilha', 'excursao', 'parque', 'natureza', 'helicoptero',
        'city tour',
    ],
    'Infantil': [
        'kids', 'infantil', 'crianca', 'familia', 'circo', 'magico',
        'mundo encantado', 'princesa', 'super heroi', 'patrulha',
        'peppa', 'frozen', 'disney', 'fantastica fabrica',
    ],
}

# Mapeamento de nomes normalizados de volta para nomes corretos
_NOME_CORRETO = {
    'Exposicao': 'Exposição',
}

def _normalizar(texto: str) -> str:
    t = unicodedata.normalize('NFKD', texto.lower())
    return ''.join(c for c in t if not unicodedata.combining(c))

def classificar_por_regras(titulo: str, descricao: str = '') -> str:
    """Tenta classificar por palavras-chave. Retorna categoria ou None."""
    texto = _normalizar(titulo + ' ' + descricao)
    for categoria, palavras in REGRAS.items():
        for palavra in palavras:
            if _normalizar(palavra) in texto:
                return _NOME_CORRETO.get(categoria, categoria)
    return None

def classify(evento: dict) -> dict:
    titulo    = evento.get('titulo', '')
    descricao = evento.get('descricao_bruta', '')

    # ── Tenta classificar por regras primeiro (zero tokens) ──
    categoria_regra = classificar_por_regras(titulo, descricao)
    if categoria_regra:
        narrativa = f'{titulo} em {evento.get("local", "Ribeirão Preto").split("-")[0].strip()}.'
        return {'categoria': categoria_regra, 'narrativa_ia': narrativa}

    # ── Só chama Groq se regras não conseguiram classificar ──
    prompt = (
        f'Titulo: {titulo} | '
        f'Data: {evento.get("data_iso", "") or "nao informada"} | '
        f'Local: {evento.get("local", "") or "Ribeirao Preto"} | '
        f'Descricao: {descricao or "sem descricao"}'
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
        if raw.startswith('```'):
            raw = raw.split('```')[1]
            if raw.startswith('json'):
                raw = raw[4:]
        data      = json.loads(raw)
        categoria = data.get('categoria', 'Outro')
        if categoria not in CATEGORIAS:
            categoria = 'Outro'
        narrativa = str(data.get('narrativa', '')).strip()[:200]
        time.sleep(2)
        return {'categoria': categoria, 'narrativa_ia': narrativa}
    except json.JSONDecodeError:
        print(f'[WARN classify] JSON malformado para: {titulo!r}')
        return {'categoria': 'Outro', 'narrativa_ia': ''}
    except Exception as e:
        print(f'[ERRO classify] {e}')
        return {'categoria': 'Outro', 'narrativa_ia': ''}

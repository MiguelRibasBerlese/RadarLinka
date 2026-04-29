from dateutil import parser as dateparser
from datetime import date
import re

CIDADES_REGIAO = [
    'ribeirão preto', 'ribeirao preto', 'ribeirão-preto',
    'brodowski',
    'batatais',
    'serrana',
    'jardinópolis', 'jardinopolis',
    'cravinhos',
    'sertãozinho', 'sertaozinho',
    'guatapará', 'guatapara',
    'dumont',
    'serra azul',
    'pradópolis', 'pradopolis',
    'pontal',
    'luís antônio', 'luis antonio',
    'santa rosa de viterbo',
]

_NOMES_CORRETOS = [
    'Ribeirão Preto', 'Ribeirão Preto', 'Ribeirão Preto',
    'Brodowski',
    'Batatais',
    'Serrana',
    'Jardinópolis', 'Jardinópolis',
    'Cravinhos',
    'Sertãozinho', 'Sertãozinho',
    'Guatapará', 'Guatapará',
    'Dumont',
    'Serra Azul',
    'Pradópolis', 'Pradópolis',
    'Pontal',
    'Luís Antônio', 'Luís Antônio',
    'Santa Rosa de Viterbo',
]

_MESES_PT = {
    'janeiro': 'january',  'jan': 'january',
    'fevereiro': 'february', 'fev': 'february',
    'março': 'march',      'mar': 'march',
    'abril': 'april',      'abr': 'april',
    'maio': 'may',         'mai': 'may',
    'junho': 'june',       'jun': 'june',
    'julho': 'july',       'jul': 'july',
    'agosto': 'august',    'ago': 'august',
    'setembro': 'september', 'set': 'september',
    'outubro': 'october',  'out': 'october',
    'novembro': 'november', 'nov': 'november',
    'dezembro': 'december', 'dez': 'december',
}

def _traduz_data_pt(data_str: str) -> str:
    s = data_str.lower()
    # Remove prefixo de dia da semana: "Sábado, " / "Terça, " etc.
    s = re.sub(r'^(segunda|ter[cç]a|quarta|quinta|sexta|s[aá]bado|domingo)[,\s]+', '', s)
    # Substitui "às HH:MM" por "HH:MM" para o dateparser
    s = s.replace('às ', '')
    for pt, en in _MESES_PT.items():
        s = re.sub(rf'\b{pt}\b', en, s)
    s = re.sub(r'\bde\b', '', s)
    return s.strip()

def _e_da_regiao(local: str) -> bool:
    local_lower = local.lower().strip()
    return any(cidade in local_lower for cidade in CIDADES_REGIAO)

def _extrair_cidade(local: str) -> str:
    """Extrai o nome da cidade do campo local."""
    local_lower = local.lower().strip()
    for idx, cidade in enumerate(CIDADES_REGIAO):
        if cidade in local_lower:
            return _NOMES_CORRETOS[idx]
    return 'Ribeirão Preto'  # fallback

def normalize(evento_bruto: dict, fonte: str):
    titulo = (evento_bruto.get('titulo') or evento_bruto.get('nome') or '').strip()
    if not titulo:
        return None

    local = (evento_bruto.get('local') or evento_bruto.get('venue') or '').strip()

    # Filtro geográfico — Ingresse retorna eventos nacionais
    if fonte == 'ingresse':
        if not local or not _e_da_regiao(local):
            return None

    # Filtro geográfico leve para Sympla (segurança)
    if fonte == 'sympla' and local and not _e_da_regiao(local):
        return None

    data_str = evento_bruto.get('data') or evento_bruto.get('date') or ''
    data_iso = ''
    if data_str:
        try:
            candidato = _traduz_data_pt(str(data_str))
            dt = dateparser.parse(candidato, dayfirst=True)
            if dt and dt.date() < date.today():
                return None  # descarta eventos passados
            data_iso = dt.strftime('%Y-%m-%d') if dt else ''
        except Exception:
            data_iso = ''

    return {
        'titulo':          titulo,
        'data_iso':        data_iso,
        'local':           local,
        'cidade':          _extrair_cidade(local),
        'url':             (evento_bruto.get('url') or '').strip(),
        'fonte':           fonte,
        'descricao_bruta': (evento_bruto.get('descricao') or
                            evento_bruto.get('description') or '').strip(),
    }

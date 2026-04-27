from dateutil import parser as dateparser
from datetime import date
import re

TERMOS_RP = ['ribeirão preto', 'ribeirao preto', ', rp', '- rp', '(rp)']

_MESES_PT = {
    'janeiro': 'january', 'fevereiro': 'february', 'março': 'march',
    'abril': 'april', 'maio': 'may', 'junho': 'june',
    'julho': 'july', 'agosto': 'august', 'setembro': 'september',
    'outubro': 'october', 'novembro': 'november', 'dezembro': 'december',
}

def _traduz_data_pt(data_str: str) -> str:
    s = data_str.lower()
    for pt, en in _MESES_PT.items():
        s = s.replace(pt, en)
    s = re.sub(r'\bde\b', '', s)
    return s.strip()

def _e_de_rp(local: str) -> bool:
    local_lower = local.lower().strip()
    return any(t in local_lower for t in TERMOS_RP)

def normalize(evento_bruto: dict, fonte: str):
    titulo = (evento_bruto.get('titulo') or evento_bruto.get('nome') or '').strip()
    if not titulo:
        return None

    local = (evento_bruto.get('local') or evento_bruto.get('venue') or '').strip()

    # Filtro geográfico — Ingresse retorna eventos nacionais
    if fonte == 'ingresse':
        if not local or not _e_de_rp(local):
            return None

    # Filtro geográfico leve para Sympla (segurança)
    if fonte == 'sympla' and local and not _e_de_rp(local):
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
        'url':             (evento_bruto.get('url') or '').strip(),
        'fonte':           fonte,
        'descricao_bruta': (evento_bruto.get('descricao') or
                            evento_bruto.get('description') or '').strip(),
    }

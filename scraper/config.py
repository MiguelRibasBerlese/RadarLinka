from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY    = os.getenv('GROQ_API_KEY')
SHEETS_CSV_URL  = os.getenv('SHEETS_CSV_URL')
SHEETS_META_URL = os.getenv('SHEETS_META_URL')
SEARCHAPI_KEY   = os.getenv('SEARCHAPI_KEY')

CATEGORIAS = [
    'Show',        # shows musicais, bandas, cantores, concertos
    'Festa',       # baladas, bailes, festas temáticas, carnaval
    'Feira',       # feiras de artesanato, gastronômicas, agronegócio
    'Festival',    # festivais multi-atrações, festivais culturais
    'Teatro',      # peças teatrais, musicais, ópera, dança
    'Esporte',     # corridas, campeonatos, torneios, eventos esportivos
    'Corporativo', # congressos, palestras, summit, networking profissional
    'Curso',       # workshops, cursos, oficinas, capacitações, aulas
    'Exposição',   # museus, exposições, mostras de arte, galerias
    'Religioso',   # cultos, retiros, conferências religiosas, acampamentos
    'Turismo',     # passeios, experiências, parques, ecoturismo
    'Infantil',    # eventos kids, parques infantis, espetáculos para crianças
    'Outro',       # quando nenhuma categoria anterior se aplica claramente
]

FONTES = [
    {
        'nome': 'sympla',
        'url': 'https://www.sympla.com.br/eventos/ribeirao-preto-sp',
        'seletor': 'a.sympla-card'
    },
    {
        'nome': 'emribeirao',
        'url': 'https://emribeirao.com/agenda-cultural-em-ribeirao-preto/',
        'seletor': 'article, [class*=card], [class*=event]'
    },
    {
        'nome': 'shopping',
        'url': 'https://www.ribeiraoshopping.com.br/eventos/',
        'seletor': 'article, [class*=event], [class*=card]'
    },
]

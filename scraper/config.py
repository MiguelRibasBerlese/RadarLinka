from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY    = os.getenv('GROQ_API_KEY')
SHEETS_CSV_URL  = os.getenv('SHEETS_CSV_URL')
SHEETS_META_URL = os.getenv('SHEETS_META_URL')

CATEGORIAS = ['Show', 'Festa', 'Feira', 'Festival', 'Teatro', 'Esporte', 'Corporativo', 'Outro']

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

from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY   = os.getenv('GROQ_API_KEY')
SEARCHAPI_KEY  = os.getenv('SEARCHAPI_KEY')
SHEETS_CSV_URL = os.getenv('SHEETS_CSV_URL')
SHEETS_META_URL = os.getenv('SHEETS_META_URL')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

CATEGORIAS = [
    'Show', 'Festa', 'Feira', 'Festival', 'Teatro', 'Esporte',
    'Corporativo', 'Curso', 'Exposição', 'Religioso', 'Turismo',
    'Infantil', 'Outro',
]

CIDADES_REGIAO = [
    'ribeirão preto', 'ribeirao preto', 'ribeirão-preto',
    'brodowski', 'batatais', 'serrana', 'jardinópolis', 'jardinopolis',
    'cravinhos', 'sertãozinho', 'sertaozinho', 'guatapará', 'guatapara',
    'dumont', 'serra azul', 'pradópolis', 'pradopolis', 'pontal',
    'luís antônio', 'luis antonio', 'santa rosa de viterbo',
    'franca', 'araraquara', 'barretos', 'jaboticabal', 'bebedouro',
    'guariba', 'monte alto', 'são josé do rio preto', 'sao jose do rio preto',
    'campinas', 'uberaba',
]

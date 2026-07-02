"""
Configurações e dados estáticos do projeto.
"""

# Dicionário mapeando UF para DDDs (fonte única de verdade)
UF_PARA_DDDS = {
    'SP': ['11', '12', '13', '14', '15', '16', '17', '18', '19'],
    'RJ': ['21', '22', '24'],
    'ES': ['27', '28'],
    'MG': ['31', '32', '33', '34', '35', '37', '38'],
    'PR': ['41', '42', '43', '44', '45', '46', '47', '48', '49'],
    'RS': ['51', '53', '54', '55'],
    'DF': ['61'],
    'GO': ['62', '64'],
    'TO': ['63'],
    'MT': ['65', '66'],
    'MS': ['67'],
    'AC': ['68'],
    'RO': ['69'],
    'BA': ['71', '73', '74', '75', '77'],
    'SE': ['79'],
    'PE': ['81', '87'],
    'AL': ['82'],
    'PB': ['83'],
    'RN': ['84'],
    'CE': ['85', '88'],
    'PI': ['86', '89'],
    'PA': ['91', '93', '94'],
    'AM': ['92', '97'],
    'RR': ['95'],
    'AP': ['96'],
    'MA': ['98', '99']
}

# Gera lista de DDDs válidos a partir do dicionário
DDD_VALIDOS = sorted(set([ddd for ddds in UF_PARA_DDDS.values() for ddd in ddds]))

# Nome do arquivo do banco de dados
DB_NAME = "telefones_ddd.db"

# URLs da API
API_BASE_URL = "https://brasilapi.com.br/api"
API_DDD_ENDPOINT = f"{API_BASE_URL}/ddd/v1/{{ddd}}"

# Tarifas para cálculo de custo (bônus)
TARIFAS = {
    'mesmo_ddd_fixo_fixo': 0.00,
    'mesmo_ddd_fixo_movel': 0.50,
    'ddd_diferente_fixo_fixo': 1.00,
    'ddd_diferente_fixo_movel': 1.50,
    'ddd_diferente_movel_movel': 2.00
}
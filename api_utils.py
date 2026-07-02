"""
Módulo para integração com APIs externas.
"""
import requests
from config import API_DDD_ENDPOINT


def consultar_ddd_api(ddd):
    """
    Consulta a BrasilAPI para obter estado e cidades de um DDD.
    Retorna um dicionário com 'estado' e 'cidades', ou None se der erro.
    """
    url = API_DDD_ENDPOINT.format(ddd=ddd)
    
    try:
        resposta = requests.get(url, timeout=5)
        
        if resposta.status_code == 200:
            dados = resposta.json()
            return {
                'estado': dados.get('state', ''),
                'cidades': dados.get('cities', [])
            }
        else:
            return None
            
    except requests.exceptions.RequestException:
        return None
"""
Módulo com funções utilitárias para manipulação de telefones.
"""
import phonenumbers
import random
from phonenumbers import number_type, PhoneNumberType
from phonenumbers import geocoder
from config import DDD_VALIDOS, UF_PARA_DDDS


def validar_ddd(ddd):
    """
    Verifica se um DDD é válido no Brasil.
    """
    return ddd in DDD_VALIDOS


def obter_uf_por_ddd(ddd):
    """
    Retorna a UF de um DDD, ou None se não encontrado.
    """
    for uf, ddds in UF_PARA_DDDS.items():
        if ddd in ddds:
            return uf
    return None


def obter_ddds_por_uf(uf):
    """
    Retorna lista de DDDs para uma UF, ou None se UF inválida.
    """
    uf = uf.upper()
    return UF_PARA_DDDS.get(uf)


def listar_ufs_disponiveis():
    """
    Retorna uma lista com todas as UFs disponíveis.
    """
    return sorted(UF_PARA_DDDS.keys())


def validar_formatar_numero(numero_input):
    """
    Valida e formata um número de telefone.
    Retorna um dicionário com os dados, ou None se o número for inválido.
    """
    try:
        numero_obj = phonenumbers.parse(numero_input, "BR")
        
        if not phonenumbers.is_valid_number(numero_obj):
            return None

        # Formata nos padrões nacional e internacional
        nacional = phonenumbers.format_number(
            numero_obj, 
            phonenumbers.PhoneNumberFormat.NATIONAL
        )
        internacional = phonenumbers.format_number(
            numero_obj, 
            phonenumbers.PhoneNumberFormat.INTERNATIONAL
        )

        # Descobre o tipo
        tipo_num = number_type(numero_obj)
        if tipo_num == PhoneNumberType.MOBILE:
            tipo = "Celular"
        elif tipo_num == PhoneNumberType.FIXED_LINE:
            tipo = "Fixo"
        else:
            tipo = "Outro"

        # Extrai o DDD
        num_nacional_str = str(numero_obj.national_number)
        ddd = num_nacional_str[:2] if len(num_nacional_str) >= 2 else ""

        # Descobre o país
        pais = geocoder.country_name_for_number(numero_obj, "pt_BR")
        if not pais:
            pais = "Brasil"
     
        return {
            'nacional': nacional,
            'internacional': internacional,
            'tipo': tipo,
            'ddd': ddd,
            'pais': pais,
            'valido': True
        }
        
    except phonenumbers.NumberParseException:
        return None


def gerar_numero_ficticio(ddd, tipo='aleatorio'):
    """
    Gera um número fictício válido para um DDD específico.
    tipo: 'celular', 'fixo' ou 'aleatorio'
    """
    if tipo == 'aleatorio':
        tipo = random.choice(['celular', 'fixo'])
    
    # Gera número base de 8 dígitos
    numero_base = f"{random.randint(10000000, 99999999)}"
    
    if tipo == 'celular':
        numero_formatado = f"9{numero_base}"
    else:  # fixo
        primeiro_digito = random.choice(['2', '3', '4', '5'])
        numero_formatado = f"{primeiro_digito}{numero_base[1:]}"
    
    numero_completo = f"{ddd}{numero_formatado}"
    
    return {
        'completo': numero_completo,
        'formatado': f"({ddd}) {numero_formatado[:4]}-{numero_formatado[4:]}",
        'ddd': ddd,
        'tipo': tipo,
        'uf': obter_uf_por_ddd(ddd)
    }


def gerar_multiples_numeros(ddd, quantidade, tipo='aleatorio'):
    """
    Gera múltiplos números fictícios para um DDD.
    """
    return [gerar_numero_ficticio(ddd, tipo) for _ in range(quantidade)]


def comparar_numeros(num1, num2):
    """
    Compara dois números e verifica se são equivalentes.
    Retorna um dicionário com o resultado da comparação.
    """
    try:
        obj1 = phonenumbers.parse(num1, "BR")
        obj2 = phonenumbers.parse(num2, "BR")
        
        # Normaliza para formato internacional sem símbolos
        normal1 = phonenumbers.format_number(
            obj1, 
            phonenumbers.PhoneNumberFormat.E164
        )
        normal2 = phonenumbers.format_number(
            obj2, 
            phonenumbers.PhoneNumberFormat.E164
        )
        
        return {
            'equivalente': normal1 == normal2,
            'normalizado1': normal1,
            'normalizado2': normal2
        }
    except:
        return None


def calcular_custo_ligacao(origem, destino):
    """
    Calcula o custo simulado de uma ligação entre dois números.
    Retorna o valor do custo em reais.
    """
    try:
        obj_origem = phonenumbers.parse(origem, "BR")
        obj_destino = phonenumbers.parse(destino, "BR")
        
        # Extrai DDDs
        ddd_origem = str(obj_origem.national_number)[:2]
        ddd_destino = str(obj_destino.national_number)[:2]
        
        # Determina tipos
        tipo_origem = number_type(obj_origem)
        tipo_destino = number_type(obj_destino)
        
        origem_movel = tipo_origem == PhoneNumberType.MOBILE
        destino_movel = tipo_destino == PhoneNumberType.MOBILE
        
        # Calcula custo baseado nas regras
        if ddd_origem == ddd_destino:
            if not origem_movel and not destino_movel:
                return 0.00  # Fixo-fixo mesmo DDD = gratuito
            else:
                return 0.50  # Qualquer ligação com móvel mesmo DDD
        else:
            if not origem_movel and not destino_movel:
                return 1.00  # Fixo-fixo DDD diferente
            elif origem_movel and destino_movel:
                return 2.00  # Móvel-móvel DDD diferente
            else:
                return 1.50  # Fixo-móvel ou móvel-fixo DDD diferente
                
    except:
        return None
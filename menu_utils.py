"""
Módulo com os handlers (manipuladores) de cada opção do menu.
"""
from database import (
    salvar_telefone,
    salvar_consulta_ddd,
    listar_telefones
)
from telefone_utils import (
    validar_formatar_numero,
    validar_ddd,
    obter_uf_por_ddd,
    obter_ddds_por_uf,
    listar_ufs_disponiveis,
    gerar_multiples_numeros,
    comparar_numeros as comparar_numeros_telefones
)
from api_utils import consultar_ddd_api
from ui_utils import (
    exibir_mensagem,
    exibir_tabela_telefone,
    exibir_tabela_ddd,
    exibir_tabela_numeros_gerados,
    exibir_tabela_historico,
    exibir_painel,
    input_numero,
    input_ddd,
    input_uf,
    input_quantidade,
    input_tipo_numero,
    input_sim_nao,
    input_text
)


def validar_numero(conexao):
    """
    Handler para opção 1: Validar e formatar número.
    """
    exibir_mensagem("\n--- VALIDAR NÚMERO ---", "info")
    
    numero = input_numero()
    dados = validar_formatar_numero(numero)
    
    if dados is None:
        exibir_mensagem("Número inválido!", "erro")
        return
    
    # Valida DDD
    ddd_valido = validar_ddd(dados['ddd'])
    uf = obter_uf_por_ddd(dados['ddd']) if ddd_valido else None
    
    if not ddd_valido:
        exibir_mensagem(f"ATENÇÃO: DDD {dados['ddd']} não está na lista de DDDs válidos!", "aviso")
    
    # Exibe dados
    exibir_tabela_telefone(dados)
    if uf:
        exibir_mensagem(f"UF: {uf}", "info")
    
    # Salva no banco
    id_reg = salvar_telefone(conexao, dados, True, 0)
    exibir_mensagem(f"✓ Salvo com ID {id_reg}", "sucesso")


def consultar_ddd(conexao):
    """
    Handler para opção 2: Consultar DDD.
    """
    exibir_mensagem("\n--- CONSULTAR DDD ---", "info")
    
    ddd = input_ddd()
    
    if not ddd.isdigit() or len(ddd) != 2:
        exibir_mensagem("DDD deve ter 2 dígitos numéricos.", "erro")
        return
    
    if not validar_ddd(ddd):
        exibir_mensagem(f"DDD {ddd} não está na lista de DDDs válidos do Brasil.", "erro")
        return
    
    uf = obter_uf_por_ddd(ddd)
    if uf:
        exibir_mensagem(f"DDD {ddd} pertence a UF {uf}", "info")
    
    dados_api = consultar_ddd_api(ddd)
    if dados_api is None:
        exibir_mensagem(f"Erro ao consultar DDD {ddd} na API.", "erro")
        return
    
    exibir_tabela_ddd(ddd, dados_api['estado'], dados_api['cidades'], uf)
    
    id_reg = salvar_consulta_ddd(conexao, ddd, dados_api['estado'], dados_api['cidades'])
    exibir_mensagem(f"✓ Consulta salva com ID {id_reg}", "sucesso")


def gerar_numeros(conexao):
    """
    Handler para opção 3: Gerar números válidos por região.
    """
    exibir_mensagem("\n--- GERAR NÚMEROS VÁLIDOS POR REGIÃO ---", "info")
    
    ufs_disponiveis = listar_ufs_disponiveis()
    exibir_mensagem(f"UFs disponíveis: {', '.join(ufs_disponiveis)}", "info")
    
    opcao = input_text("Deseja gerar por UF ou DDD?  digite UF ou DDD:").strip()
    
    ddds = []
    uf_info = None
    
    if opcao.lower() == "uf":
        uf = input_uf()
        ddds = obter_ddds_por_uf(uf)
        
        if ddds is None:
            exibir_mensagem(f"UF {uf} não encontrada.", "erro")
            return
        
        exibir_mensagem(f"Encontrados {len(ddds)} DDDs para UF {uf}: {', '.join(ddds)}", "sucesso")
        uf_info = uf
        
    elif opcao.lower() == "ddd":
        ddd = input_ddd()
        
        if not ddd.isdigit() or len(ddd) != 2:
            exibir_mensagem("DDD deve ter 2 dígitos numéricos.", "erro")
            return
        
        if not validar_ddd(ddd):
            exibir_mensagem(f"DDD {ddd} não é válido.", "erro")
            return
        
        ddds = [ddd]
        uf_info = obter_uf_por_ddd(ddd)
    elif opcao.isalpha() and len(opcao) == 2:
        uf = opcao.upper()
        ddds = obter_ddds_por_uf(uf)
        
        if ddds is None:
            exibir_mensagem(f"UF {uf} não encontrada.", "erro")
            return
        
        exibir_mensagem(f"Encontrados {len(ddds)} DDDs para UF {uf}: {', '.join(ddds)}", "sucesso")
        uf_info = uf
    elif opcao.isdigit() and len(opcao) == 2:
        ddd = opcao
        
        if not validar_ddd(ddd):
            exibir_mensagem(f"DDD {ddd} não é válido.", "erro")
            return
        
        ddds = [ddd]
        uf_info = obter_uf_por_ddd(ddd)
    else:
        exibir_mensagem("Opção inválida. Use 'uf', 'ddd', UF de 2 letras ou DDD de 2 dígitos.", "erro")
        return
    
    tipo = input_tipo_numero()
    quantidade = input_quantidade()
    
    if quantidade <= 0:
        exibir_mensagem("Quantidade deve ser maior que zero.", "erro")
        return
    
    # Gera os números
    numeros_gerados = []
    
    if len(ddds) > 1:
        distribuir = input_sim_nao(f"Distribuir {quantidade} números entre os {len(ddds)} DDDs? (s/n)")
        
        if distribuir == "s":
            numeros_por_ddd = quantidade // len(ddds)
            resto = quantidade % len(ddds)
            
            for i, ddd in enumerate(ddds):
                qtd = numeros_por_ddd + (1 if i < resto else 0)
                if qtd > 0:
                    numeros = gerar_multiples_numeros(ddd, qtd, tipo)
                    numeros_gerados.extend(numeros)
        else:
            ddd_escolhido = input_text(f"Escolha um DDD entre {', '.join(ddds)}").strip()
            if ddd_escolhido in ddds:
                numeros_gerados = gerar_multiples_numeros(ddd_escolhido, quantidade, tipo)
            else:
                exibir_mensagem("DDD inválido.", "erro")
                return
    else:
        numeros_gerados = gerar_multiples_numeros(ddds[0], quantidade, tipo)
    
    if not numeros_gerados:
        exibir_mensagem("Nenhum número gerado.", "erro")
        return
    
    exibir_mensagem(f"✓ {len(numeros_gerados)} números gerados com sucesso!", "sucesso")
    exibir_tabela_numeros_gerados(numeros_gerados)
    
    # Salva no banco
    exibir_mensagem("Salvando números no banco de dados...", "info")
    salvos = 0
    
    for num in numeros_gerados:
        dados_telefone = {
            'nacional': num['formatado'],
            'internacional': f"+55 {num['formatado']}",
            'tipo': num['tipo'].capitalize(),
            'ddd': num['ddd'],
            'pais': "Brasil"
        }
        
        # Valida com phonenumbers
        try:
            import phonenumbers
            numero_obj = phonenumbers.parse(num['completo'], "BR")
            valido = phonenumbers.is_valid_number(numero_obj)
            salvar_telefone(conexao, dados_telefone, valido, 1)
            salvos += 1
        except:
            salvar_telefone(conexao, dados_telefone, False, 1)
            salvos += 1
    
    exibir_mensagem(f"✓ {salvos} números salvos no banco de dados.", "sucesso")
    


def buscar_historico(conexao):
    """
    Handler para opção 4: Buscar histórico.
    """
    exibir_mensagem("\n--- BUSCAR HISTÓRICO ---", "info")
    exibir_mensagem("Use os filtros abaixo para refinar os resultados.", "info")

    opcao = input_text("Filtrar por (nenhum/tipo/ficticio/estado):").strip().lower()
    filtro = {}

    if opcao == "tipo":
        tipo = input_text("Tipo (Celular/Fixo/Outro):").strip().capitalize()
        if tipo not in ["Celular", "Fixo", "Outro"]:
            exibir_mensagem("Tipo inválido. Use Celular, Fixo ou Outro.", "erro")
            return
        filtro['tipo'] = tipo

    elif opcao == "ficticio":
        resposta = input_sim_nao("Mostrar apenas números fictícios? (s/n):")
        if resposta not in ["s", "n"]:
            exibir_mensagem("Resposta inválida. Use s ou n.", "erro")
            return
        filtro['ficticio'] = 1 if resposta == "s" else 0

    elif opcao == "estado":
        uf = input_uf()
        ddds = obter_ddds_por_uf(uf)
        if ddds is None:
            exibir_mensagem(f"UF {uf} não encontrada.", "erro")
            return
        filtro['ddd_list'] = ddds

    elif opcao != "nenhum":
        exibir_mensagem("Opção de filtro inválida.", "erro")
        return

    registros = listar_telefones(conexao, filtro)

    if not registros:
        exibir_mensagem("Nenhum registro encontrado.", "aviso")
        return

    ufs = [obter_uf_por_ddd(registro[4]) or "N/A" for registro in registros]
    exibir_tabela_historico(registros, ufs)


def comparar_numeros():
    """
    Handler para opção 5: Comparar dois números.
    """
    exibir_mensagem("\n--- COMPARAR NÚMEROS ---", "info")

    primeiro_numero = input_numero("Digite o primeiro número")
    segundo_numero = input_numero("Digite o segundo número")

    resultado = comparar_numeros_telefones(primeiro_numero, segundo_numero)

    if resultado is None:
        exibir_mensagem("Pelo menos um dos números não é válido.", "erro")
        return

    equivalente = "SIM" if resultado['equivalente'] else "NÃO"
    exibir_mensagem(f"Equivalentes: {equivalente}", "info")
    exibir_mensagem(f"Normalizado 1: {resultado['normalizado1']}", "info")
    exibir_mensagem(f"Normalizado 2: {resultado['normalizado2']}", "info")
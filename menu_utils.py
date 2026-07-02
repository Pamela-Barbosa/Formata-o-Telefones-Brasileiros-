"""
Módulo com os handlers (manipuladores) de cada opção do menu.
"""
import sys
from datetime import datetime
from database import (
    salvar_telefone,
    salvar_consulta_ddd,
    verificar_bloqueio,
    adicionar_bloqueio
)
from telefone_utils import (
    validar_formatar_numero,
    validar_ddd,
    obter_uf_por_ddd,
    obter_ddds_por_uf,
    listar_ufs_disponiveis,
    gerar_multiples_numeros
)
from api_utils import consultar_ddd_api
from ui_utils import (
    exibir_mensagem,
    exibir_tabela_telefone,
    exibir_tabela_ddd,
    exibir_tabela_numeros_gerados,
    exibir_painel,
    input_numero,
    input_ddd,
    input_uf,
    input_quantidade,
    input_tipo_numero,
    input_sim_nao
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
    
    # Verifica bloqueio
    bloqueado = verificar_bloqueio(conexao, dados['nacional'])
    if bloqueado:
        exibir_mensagem(f"⚠️ ATENÇÃO: Este número está BLOQUEADO! Motivo: {bloqueado[2]}", "aviso")
    
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
    
    opcao = input("Deseja gerar por UF ou DDD? (uf/ddd): ")
    
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
        
    else:  # ddd
        ddd = input_ddd()
        
        if not ddd.isdigit() or len(ddd) != 2:
            exibir_mensagem("DDD deve ter 2 dígitos numéricos.", "erro")
            return
        
        if not validar_ddd(ddd):
            exibir_mensagem(f"DDD {ddd} não é válido.", "erro")
            return
        
        ddds = [ddd]
        uf_info = obter_uf_por_ddd(ddd)
    
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
            ddd_escolhido = input(f"Escolha um DDD entre {', '.join(ddds)}")
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
    
    # Exportar vCard
    exportar = input_sim_nao("\nDeseja exportar como arquivo vCard (.vcf)? (s/n)")
    if exportar == "s":
        nome_arquivo = f"contatos_{uf_info if uf_info else 'ddd'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.vcf"
        
        try:
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                for i, num in enumerate(numeros_gerados, 1):
                    f.write("BEGIN:VCARD\n")
                    f.write("VERSION:3.0\n")
                    f.write(f"FN:Contato {i}\n")
                    f.write(f"TEL;TYPE=CELL:{num['formatado']}\n")
                    f.write("END:VCARD\n")
            
            exibir_mensagem(f"✓ vCard exportado: {nome_arquivo}", "sucesso")
        except Exception as e:
            exibir_mensagem(f"Erro ao exportar vCard: {e}", "erro")


def buscar_historico():
    """
    Handler para opção 4: Buscar histórico (EM DESENVOLVIMENTO).
    """
    exibir_mensagem("\n--- BUSCAR HISTÓRICO ---", "info")
    exibir_mensagem("⚠️ Funcionalidade em desenvolvimento...", "aviso")
    exibir_painel(
        "📋 Em breve você poderá:\n"
        "• Listar todos os números consultados\n"
        "• Filtrar por tipo (fixo/móvel/fictício)\n"
        "• Filtrar por estado\n"
        "• Ver todas as colunas relevantes",
        titulo="🔨 EM CONSTRUÇÃO",
        cor="yellow"
    )


def comparar_numeros():
    """
    Handler para opção 5: Comparar dois números (EM DESENVOLVIMENTO).
    """
    exibir_mensagem("\n--- COMPARAR NÚMEROS ---", "info")
    exibir_mensagem("⚠️ Funcionalidade em desenvolvimento...", "aviso")
    exibir_painel(
        "🔍 Em breve você poderá:\n"
        "• Comparar dois números em formatos diferentes\n"
        "• Extrair representação canônica de cada um\n"
        "• Verificar se são equivalentes\n"
        "• Calcular custo de ligação simulado",
        titulo="🔨 EM CONSTRUÇÃO",
        cor="yellow"
    )


def gerenciar_bloqueio():
    """
    Handler para opção 6: Gerenciar lista de bloqueio (EM DESENVOLVIMENTO).
    """
    exibir_mensagem("\n--- GERENCIAR LISTA DE BLOQUEIO ---", "info")
    exibir_mensagem("⚠️ Funcionalidade em desenvolvimento...", "aviso")
    exibir_painel(
        "🚫 Em breve você poderá:\n"
        "• Adicionar números à lista de bloqueio\n"
        "• Remover números da lista\n"
        "• Listar todos os bloqueios\n"
        "• Receber alertas ao consultar números bloqueados",
        titulo="🔨 EM CONSTRUÇÃO",
        cor="yellow"
    )
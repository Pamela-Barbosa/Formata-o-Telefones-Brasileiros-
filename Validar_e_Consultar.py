# Bibliotecas
import sqlite3
import phonenumbers
import requests

# Importa funções específicas 
from phonenumbers import number_type, PhoneNumberType
from phonenumbers import geocoder
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, IntPrompt

# Conecta ao arquivo do banco de dados 
conexao = sqlite3.connect("telefones_ddd.db")

# Cria um cursor para executar comandos 
cursor = conexao.cursor()

#criar tabelas

def criar_tabelas():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS telefones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,   
        numero_nacional TEXT,                   
        numero_internacional TEXT,              
        tipo TEXT,                              
        ddd TEXT,                               
        pais TEXT,                              
        valido TEXT                             
    )
    """)
    
    # Tabela para guardar consultas de DDD 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ddd_consultas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ddd TEXT,                            
        estado TEXT,                            
        cidades TEXT                           
    )
    """)
    
    # Confirma as alterações no banco
    conexao.commit()

def salvar_telefone(dados, valido):
    """
    Insere um telefone validado na tabela 'telefones'.
    Retorna o ID do registro inserido.
    """
    cursor.execute("""
    INSERT INTO telefones 
    (numero_nacional, numero_internacional, tipo, ddd, pais, valido)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        dados['nacional'],          
        dados['internacional'],    
        dados['tipo'],             
        dados['ddd'],              
        dados['pais'],              
        "Sim" if valido else "Nao"  
    ))
    
    conexao.commit()                
    return cursor.lastrowid        

#Salvar o ddd

def salvar_ddd(ddd, estado, cidades):
    """
    Insere uma consulta de DDD na tabela 'ddd_consultas'.
    Retorna o ID do registro inserido.
    """
    cidades_str = ", ".join(cidades) if cidades else ""
    
    cursor.execute("""
    INSERT INTO ddd_consultas (ddd, estado, cidades)
    VALUES (?, ?, ?)
    """, (ddd, estado, cidades_str))
    
    conexao.commit()
    return cursor.lastrowid

#consultar_ddd_api

def consultar_ddd_api(ddd):
    """
    Consulta a BrasilAPI para obter estado e cidades de um DDD.
    Retorna um dicionário com 'estado' e 'cidades', ou None se der erro.
    """
    url = f"https://brasilapi.com.br/api/ddd/v1/{ddd}"
    
    # Faz a requisição HTTP, com timeout de 5 segundos
    resposta = requests.get(url, timeout=5)
    
    if resposta.status_code == 200:
        dados = resposta.json() 
        estado = dados.get('state', '')     
        cidades = dados.get('cities', [])   
        return {'estado': estado, 'cidades': cidades}
    else:
        print(f"DDD {ddd} nao encontrado ou erro na API.")
        return None

# validar formatar numero

def validar_formatar_numero(numero_input):
    """
    Valida e formata um número de telefone.
    Retorna um dicionário com os dados, ou None se o número for inválido.
    """
    numero_obj = phonenumbers.parse(numero_input, "BR")
   
    if not phonenumbers.is_valid_number(numero_obj):
        print("Numero invalido (nao existe na numeracao real).")
        return None

    # Formata nos padrões nacional e internacional
    nacional = phonenumbers.format_number(numero_obj, phonenumbers.PhoneNumberFormat.NATIONAL)
    internacional = phonenumbers.format_number(numero_obj, phonenumbers.PhoneNumberFormat.INTERNATIONAL)

    # Descobre o tipo: Celular, Fixo 
    tipo_num = number_type(numero_obj)
    if tipo_num == PhoneNumberType.MOBILE:
        tipo = "Celular"
    elif tipo_num == PhoneNumberType.FIXED_LINE:
        tipo = "Fixo"
   
    # Extrai o DDD: pega os dois primeiros dígitos do número nacional
    # Ex: 11999999999 -> "11"
    num_nacional_str = str(numero_obj.national_number)
    if len(num_nacional_str) >= 2:
        ddd = num_nacional_str[:2]
    else:
        ddd = "" 

    # Descobre o país usando o geocoder
    pais = geocoder.country_name_for_number(numero_obj, "pt_BR")
    if not pais:
        pais = "Brasil"  
 
    return {
        'nacional': nacional,
        'internacional': internacional,
        'tipo': tipo,
        'ddd': ddd,
        'pais': pais
    }

# Cria um objeto Console para exibir textos coloridos e tabelas
console = Console()

#menu

def menu():
    """Exibe o menu e retorna a opção escolhida (0, 1 ou 2)."""
    console.print("SISTEMA DE TELEFONE E DDD")
    console.print("[1] Validar e formatar numero")
    console.print("[2] Consultar DDD (cidades/estado)")
    console.print("[0] Sair")
    return IntPrompt.ask("\nEscolha uma opcao", choices=["0", "1", "2"])

#main 

def main():
    """Loop principal do programa."""
    
    criar_tabelas()

    # Loop infinito que só termina quando o usuário escolher 0
    while True:
        opcao = menu()

        # --- Opção 0: Sair ---
        if opcao == 0:
            console.print("[bold red]Encerrando... Ate logo![/]")
            break

        # --- Opção 1: Validar número ---
        elif opcao == 1:
            console.print("\n[bold yellow]--- VALIDAR NUMERO ---[/]")
            # Pede o número ao usuário
            numero = Prompt.ask("Digite o numero (ex: 11999999999 ou +5511999999999)")

            # Chama a função de validação
            dados = validar_formatar_numero(numero)
            if dados is None:
                continue  

            # Cria uma tabela para exibir os dados com rich
            table = Table(title="Dados do Telefone")
            table.add_column("Campo")
            table.add_column("Valor")
            table.add_row("Nacional", dados['nacional'])
            table.add_row("Internacional", dados['internacional'])
            table.add_row("Tipo", dados['tipo'])
            table.add_row("DDD", dados['ddd'])
            table.add_row("Pais", dados['pais'])
            console.print(table)

            # Salva no banco (sempre válido, pois passou na validação)
            id_reg = salvar_telefone(dados, True)
            console.print(f"[green]Salvo com ID {id_reg}[/]")

        # --- Opção 2: Consultar DDD ---
        elif opcao == 2:
            console.print("\n[bold yellow]--- CONSULTAR DDD ---[/]")
            ddd = Prompt.ask("Digite o DDD (2 digitos)", default="11")

            # Valida se são exatamente 2 dígitos numéricos
            if not ddd.isdigit() or len(ddd) != 2:
                console.print("[red]DDD deve ter 2 digitos numericos.[/]")
                continue

            # Verifica se o DDD existe usando a biblioteca phonenumbers (opcional)
            teste = phonenumbers.parse(f"{ddd}999999999", "BR")
            if not phonenumbers.is_valid_number(teste):
                console.print(f"[yellow]Aviso: DDD {ddd} nao e comum segundo phonenumbers, mas vamos consultar mesmo assim.[/]")

            # Chama a função que consulta a API
            dados_api = consultar_ddd_api(ddd)
            if dados_api is None:
                continue

            # Exibe os resultados em tabela
            table = Table(title=f"DDD {ddd}")
            table.add_column("Estado")
            table.add_column("Cidades")
            cidades_str = ", ".join(dados_api['cidades']) if dados_api['cidades'] else "Nenhuma cidade listada"
            table.add_row(dados_api['estado'], cidades_str)
            console.print(table)

            # Salva a consulta no banco
            id_reg = salvar_ddd(ddd, dados_api['estado'], dados_api['cidades'])
            console.print(f"[green]Consulta salva com ID {id_reg}[/]")

        # Pausa para o usuário ver o resultado antes de voltar ao menu
            Prompt.ask("\nPressione Enter para continuar...", default="")
    # Fecha a conexão com o banco de dados (boa prática)
    conexao.close()

# Entrada do programa

if __name__ == "__main__":
    main()
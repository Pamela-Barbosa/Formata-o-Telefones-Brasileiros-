"""
Módulo com funções de interface usando a biblioteca Rich.
"""
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel


console = Console()


def exibir_tabela_telefone(dados):
    """
    Exibe os dados de um telefone em uma tabela Rich.
    """
    table = Table(title="Dados do Telefone")
    table.add_column("Campo", style="cyan")
    table.add_column("Valor", style="green")
    
    table.add_row("Nacional", dados.get('nacional', 'N/A'))
    table.add_row("Internacional", dados.get('internacional', 'N/A'))
    table.add_row("Tipo", dados.get('tipo', 'N/A'))
    table.add_row("DDD", dados.get('ddd', 'N/A'))
    table.add_row("País", dados.get('pais', 'N/A'))
    
    console.print(table)


def exibir_tabela_numeros_gerados(numeros):
    """
    Exibe uma lista de números gerados em tabela.
    """
    table = Table(title="Números Gerados")
    table.add_column("#", style="cyan", width=3)
    table.add_column("UF", style="magenta")
    table.add_column("DDD", style="yellow")
    table.add_column("Tipo", style="green")
    table.add_column("Número", style="white")
    table.add_column("Formatado", style="blue")
    
    for i, num in enumerate(numeros, 1):
        table.add_row(
            str(i),
            num.get('uf', '?'),
            num['ddd'],
            num['tipo'].capitalize(),
            num['completo'],
            num['formatado']
        )
    
    console.print(table)


def exibir_tabela_ddd(ddd, estado, cidades, uf=None):
    """
    Exibe informações de um DDD em tabela.
    """
    titulo = f"DDD {ddd}"
    if uf:
        titulo += f" - {uf}"
    
    table = Table(title=titulo)
    table.add_column("Estado", style="cyan")
    table.add_column("Cidades", style="green")
    
    # Limita a exibição de cidades
    if len(cidades) > 10:
        cidades_str = ", ".join(cidades[:10]) + f"\n... e mais {len(cidades)-10} cidades"
    else:
        cidades_str = ", ".join(cidades) if cidades else "Nenhuma cidade listada"
    
    table.add_row(estado, cidades_str)
    console.print(table)


def exibir_menu():
    """
    Exibe o menu principal e retorna a opção escolhida.
    """
    console.print("\n[bold cyan]" + "="*50)
    console.print("[bold cyan]SISTEMA DE TELEFONE E DDD")
    console.print("[bold cyan]" + "="*50)
    
    menu_items = [
        ("1", "Validar e formatar número"),
        ("2", "Consultar DDD (cidades/estado)"),
        ("3", "Gerar números válidos por região"),
        ("4", "Buscar histórico"),
        ("5", "Comparar dois números"),
        ("6", "Gerenciar lista de bloqueio"),
        ("0", "Sair")
    ]
    
    for num, desc in menu_items:
        console.print(f"[{num}] {desc}")
    
    return IntPrompt.ask("\nEscolha uma opção", choices=["0", "1", "2", "3", "4", "5", "6"])


def exibir_mensagem(mensagem, tipo="info"):
    """
    Exibe mensagens formatadas com cores.
    """
    cores = {
        "info": "blue",
        "sucesso": "green",
        "erro": "red",
        "aviso": "yellow"
    }
    
    cor = cores.get(tipo, "white")
    console.print(f"[{cor}]{mensagem}[/]")


def exibir_painel(texto, titulo="", cor="blue"):
    """
    Exibe um painel com texto formatado.
    """
    panel = Panel(texto, title=titulo, border_style=cor)
    console.print(panel)


def input_numero(mensagem="Digite o número de telefone"):
    """
    Solicita um número de telefone ao usuário.
    """
    return Prompt.ask(mensagem)


def input_ddd():
    """
    Solicita um DDD ao usuário.
    """
    return Prompt.ask("Digite o DDD (2 dígitos)", default="11")


def input_quantidade():
    """
    Solicita a quantidade de números a gerar.
    """
    return IntPrompt.ask("Quantos números gerar?", default=5)


def input_uf():
    """
    Solicita uma UF ao usuário.
    """
    return Prompt.ask("Digite a UF (ex: SP, RJ, MG)").upper()


def input_tipo_numero():
    """
    Solicita o tipo de número para geração.
    """
    return Prompt.ask(
        "Tipo de número? (celular, fixo ou aleatório)",
        choices=["celular", "fixo", "aleatorio"]
    )


def input_sim_nao(mensagem):
    """
    Solicita uma resposta sim/não ao usuário.
    """
    return Prompt.ask(mensagem, choices=["s", "n"])
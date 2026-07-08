"""
Ponto de entrada principal da aplicação.
Apenas monta o menu e chama os menus.
"""
import sys
from database import criar_banco
from ui_utils import exibir_menu, exibir_mensagem
from menu_utils import (
    validar_numero,
    consultar_ddd,
    gerar_numeros,
    buscar_historico,
    comparar_numeros
)


def main():
    """
    Função principal da aplicação.
    Gerencia o loop do menu e chama os menus correspondentes.
    """
    try:
        # Inicializa o banco de dados (mantém histórico entre execuções)
        conexao = criar_banco()
        exibir_mensagem("Sistema iniciado com sucesso!", "sucesso")
        
        while True:
            opcao = exibir_menu()
            
            # Opção 0: Sair
            if opcao == 0:
                exibir_mensagem("Encerrando... Até logo!", "info")
                break
            
            # Opção 1: Validar e formatar número
            elif opcao == 1:
                validar_numero(conexao)
            
            # Opção 2: Consultar DDD
            elif opcao == 2:
                consultar_ddd(conexao)
            
            # Opção 3: Gerar números válidos por região
            elif opcao == 3:
                gerar_numeros(conexao)
            
            # Opção 4: Buscar histórico
            elif opcao == 4:
                buscar_historico(conexao)
            
            # Opção 5: Comparar dois números
            elif opcao == 5:
                comparar_numeros()
            
            # Opção inválida
            else:
                exibir_mensagem("Opção inválida!", "erro")
            
            input("\nPressione Enter para continuar...")
        
        # Fecha a conexão com o banco
        conexao.close()
        
    except KeyboardInterrupt:
        exibir_mensagem("\nPrograma interrompido pelo usuário.", "aviso")
        sys.exit(0)
    except Exception as e:
        exibir_mensagem(f"Erro inesperado: {e}", "erro")
        sys.exit(1)


if __name__ == "__main__":
    main()
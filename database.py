"""
Módulo de gerenciamento do banco de dados SQLite.
"""
import sqlite3
import os
from config import DB_NAME


def criar_conexao():
    """
    Cria e retorna uma conexão com o banco de dados SQLite.
    """
    return sqlite3.connect(DB_NAME)


def criar_tabelas(conexao):
    """
    Cria todas as tabelas necessárias no banco de dados.
    """
    cursor = conexao.cursor()
    
    # Tabela de telefones
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS telefones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_nacional TEXT,
        numero_internacional TEXT,
        tipo TEXT,
        ddd TEXT,
        pais TEXT,
        valido TEXT,
        ficticio INTEGER DEFAULT 0,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Tabela de consultas de DDD
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ddd_consultas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ddd TEXT,
        estado TEXT,
        cidades TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conexao.commit()


def recriar_banco():
    """
    Remove o banco de dados existente e cria um novo.
    """
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
    
    conexao = criar_conexao()
    criar_tabelas(conexao)
    conexao.close()
    return criar_conexao()


def salvar_telefone(conexao, dados, valido, ficticio=0):
    """
    Insere um telefone no banco de dados.
    Retorna o ID do registro inserido.
    """
    cursor = conexao.cursor()
    cursor.execute("""
    INSERT INTO telefones 
    (numero_nacional, numero_internacional, tipo, ddd, pais, valido, ficticio)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        dados['nacional'],
        dados['internacional'],
        dados['tipo'],
        dados['ddd'],
        dados['pais'],
        "Sim" if valido else "Nao",
        ficticio
    ))
    conexao.commit()
    return cursor.lastrowid


def criar_banco():
    """
    Inicializa o banco de dados, criando as tabelas caso não existam.
    """
    conexao = criar_conexao()
    criar_tabelas(conexao)
    return conexao


def salvar_consulta_ddd(conexao, ddd, estado, cidades):
    """
    Insere uma consulta de DDD no banco de dados.
    """
    cursor = conexao.cursor()
    cidades_str = ", ".join(cidades) if cidades else ""
    
    cursor.execute("""
    INSERT INTO ddd_consultas (ddd, estado, cidades)
    VALUES (?, ?, ?)
    """, (ddd, estado, cidades_str))
    
    conexao.commit()
    return cursor.lastrowid


def listar_telefones(conexao, filtro=None):
    """
    Lista todos os telefones do banco, com filtros opcionais.
    """
    cursor = conexao.cursor()
    query = "SELECT * FROM telefones"
    params = []
    clauses = []
    
    if filtro:
        if filtro.get('tipo'):
            clauses.append("tipo = ?")
            params.append(filtro['tipo'])
        if filtro.get('ficticio') is not None:
            clauses.append("ficticio = ?")
            params.append(filtro['ficticio'])
        if filtro.get('ddd_list'):
            ddd_list = filtro['ddd_list']
            placeholders = ", ".join("?" for _ in ddd_list)
            clauses.append(f"ddd IN ({placeholders})")
            params.extend(ddd_list)
    
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    
    query += " ORDER BY timestamp DESC"
    cursor.execute(query, params)
    return cursor.fetchall()


def buscar_telefone_por_numero(conexao, numero):
    """
    Busca um telefone pelo número formatado.
    """
    cursor = conexao.cursor()
    cursor.execute("""
    SELECT * FROM telefones 
    WHERE numero_nacional = ? OR numero_internacional = ?
    """, (numero, numero))
    return cursor.fetchone()
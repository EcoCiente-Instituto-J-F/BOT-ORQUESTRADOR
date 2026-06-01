import psycopg2
import logging

def connection(host:str,port:str,database:str,user:str,password:str) -> psycopg2.extensions.connection:
    """Estabelece conexão com o banco de dados baseado no prefixo do .yaml"""
    try:
        conexao = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        return conexao
    except Exception as e:
        logging.critical(f"Erro ao conectar ao banco: {e}",exc_info=True)
        return None


import logging
from pathlib import Path
import yaml
import os
from psycopg2 import extras

from utils.load_config import connection

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    logging.info("Iniciando a execução do BOT-ORQUESTRADOR")

    yaml_file = Path(__file__).parent.parent / "config"/"config.yaml"
    if not os.path.exists(yaml_file):
        logging.critical(f"Arquivo de configuração '{yaml_file}' não encontrado.")
        return

    try:
        with open(yaml_file, "r") as f:
            config = yaml.safe_load(f)
            config_destino = config['BancoDestino']
            config_origem = config['BancoOrigem']
    except Exception as e:
        logging.critical(f"Erro ao ler o arquivo YAML: {e}", exc_info=True)
        return

    logging.info("Conectando ao banco de dados de origem...")
    conn_origem = connection(
        host=config_origem["host"],
        port=config_origem["port"],
        database=config_origem["database"],
        user=config_origem["user"],
        password=config_origem["password"]
    )

    logging.info("Conectando ao banco de dados de destino...")
    conn_destino = connection(
        host=config_destino["host"],
        port=config_destino["port"],
        database=config_destino["database"],
        user=config_destino["user"],
        password=config_destino["password"]
    )

    # Validar se ambas as conexões foram estabelecidas com sucesso
    if not conn_origem or not conn_destino:
        logging.error("Falha ao estabelecer conexão com os bancos. O processo foi abortado.")
        return

    # Usando DictCursor para facilitar a leitura das colunas pelos nomes no mapeamento
    cursor_origem = conn_origem.cursor(cursor_factory=extras.DictCursor)
    cursor_destino = conn_destino.cursor()

    try:
        # 4. Extração dos dados do banco legado
        logging.info("Buscando dados na origem...")
        cursor_origem.execute("SELECT id, nome_cliente, email_cliente, data_cadastro FROM tabela_antiga;")
        registros = cursor_origem.fetchall()
        logging.info(f"{len(registros)} registros encontrados para processamento.")

        # 5. Processamento e carga no banco normalizado (Garantindo a integridade solicitada)
        sucessos = 0
        falhas = 0

        for registro in registros:
            try:
                # Exemplo de higienização rápida dos dados antes de salvar
                id_origem = registro["id"]
                nome = registro["nome_cliente"].strip() if registro["nome_cliente"] else None
                email = registro["email_cliente"].lower().strip() if registro["email_cliente"] else None
                data = registro["data_cadastro"]

                # Query adaptada ao novo banco normalizado
                query_insert = """
                    INSERT INTO clientes (id_externo, nome, email, criado_em) 
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (email) DO NOTHING;
                """
                cursor_destino.execute(query_insert, (id_origem, nome, email, data))
                sucessos += 1

            except Exception as erro_registro:
                # Tratando falhas individuais na carga para não derrubar o robô inteiro
                falhas += 1
                logging.warning(f"Falha ao processar o registro ID {registro.get('id')}: {erro_registro}")
                conn_destino.rollback()  # Desfaz apenas a transação da linha atual corrompida
                continue

        # Confirma as alterações bem-sucedidas no banco final
        conn_destino.commit()
        logging.info(f"Processo concluído! Sucessos: {sucessos} | Falhas puladas: {falhas}")

    except Exception as e:
        logging.error(f"Erro geral durante a orquestração do pipeline de dados: {e}", exc_info=True)
        conn_destino.rollback()

    finally:
        # Fechamento seguro de todos os ponteiros e conexões abertas
        cursor_origem.close()
        cursor_destino.close()
        conn_origem.close()
        conn_destino.close()
        logging.info("Conexões com os bancos de dados encerradas de forma segura.")

if __name__ == "__main__":
    main()
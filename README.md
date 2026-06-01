# Projeto Interdisciplinar - Automação e Integração de Dados (RPA)

Este projeto consiste em um robô de **RPA (Robotic Process Automation)** desenvolvido em Python para realizar a comunicação, migração e consistência de dados entre bases de dados independentes (banco legado/1º ano e banco normalizado/2º ano) em ambiente PostgreSQL.

---

## 🛠️ Configuração do Ambiente

O projeto utiliza um arquivo de configuração centralizado (`config.yaml`) e variáveis de ambiente para garantir a segurança das credenciais e a portabilidade do sistema.

### 1. Modelo do arquivo `config.yaml`

Crie um arquivo chamado `config.yaml` na raiz do projeto e configure as credenciais seguindo o modelo abaixo:

```yaml
database_origem:
  host: "localhost"
  port: "6767"
  database: "my_database_origem"
  user: "my_user"
  password: "my_password"

database_destino:
  host: "localhost"
  port: "6767"
  database: "my_database_destino"
  user: "my_user"
  password: "my_password"

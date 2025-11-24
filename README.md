# Bank Agent System

Sistema multi-agente de atendimento bancário desenvolvido com IA Generativa.

## Sobre o projeto

Este projeto implementa um sistema de atendimento bancário automatizado utilizando múltiplos agentes especializados baseados em IA Generativa. O sistema oferece uma interface conversacional natural para realizar operações bancárias através de uma aplicação web construída com Streamlit.

## Agentes disponíveis

O sistema conta com quatro agentes especializados:

- **Agente de triagem**: responsável pela autenticação inicial dos clientes através de CPF e data de nascimento. Direciona o cliente para o agente adequado conforme sua necessidade.

- **Agente de crédito**: gerencia consultas de limite de crédito e processa solicitações de aumento de limite. Analisa automaticamente o score do cliente para aprovar ou rejeitar pedidos.

- **Agente de entrevista de crédito**: conduz entrevistas estruturadas para recalcular o score de crédito dos clientes. Coleta informações sobre renda, situação empregatícia, número de dependentes e status de dívidas.

- **Agente de câmbio**: fornece cotações de moedas em tempo real utilizando a API ExchangeRate. Suporta consultas de conversão entre diferentes moedas estrangeiras e o Real Brasileiro.

## Requisitos

- Python 3.10 ou superior
- Chave de API do Google Generative AI (Gemini)
- Conexão com internet para consulta de cotações de câmbio

## Instalação

### Configuração manual

1. Clone o repositório:

```bash
git clone <repository-url>
cd bank_agent
```

2. Crie um ambiente virtual:

```bash
python3 -m venv bank_venv
source bank_venv/bin/activate   # Linux/macOS
# ou
bank_venv\Scripts\activate      # Windows
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:

```bash
cp .env.example .env
```

Edite o arquivo `.env` e adicione sua chave de API:

```
GOOGLE_API_KEY=sua-chave-aqui
```

### Configuração automatizada

Execute o script de setup:

```bash
chmod +x setup.sh
./setup.sh
```

## Execução

Ative o ambiente virtual (se não estiver ativo):

```bash
source bank_venv/bin/activate   # Linux/macOS
# ou
bank_venv\Scripts\activate      # Windows
```

Execute a aplicação:

```bash
streamlit run src/ui/app.py
```

A aplicação estará disponível em `http://localhost:8501`

## Uso do sistema

### Autenticação

1. Ao iniciar, o sistema solicitará seu CPF
2. Em seguida, informe sua data de nascimento no formato DD/MM/AAAA
3. Após autenticação bem-sucedida, você terá acesso aos serviços

### Consulta de limite de crédito

Para consultar seu limite atual:
- "Qual é meu limite?"
- "Consultar limite"
- "Quanto tenho de crédito disponível?"

### Solicitação de aumento de limite

Para solicitar aumento:
- "Gostaria de aumentar meu limite"
- "Quero solicitar aumento de limite"
- "Aumentar limite para R$ 10000"

O sistema analisará automaticamente seu score de crédito e informará se a solicitação foi aprovada ou rejeitada.

### Entrevista para recálculo de score

Se sua solicitação for rejeitada por score insuficiente:
- O agente oferecerá realizar uma entrevista de crédito
- Responda às perguntas sobre renda, emprego, dependentes e dívidas
- Seu score será recalculado automaticamente

### Consulta de câmbio

Para consultar cotações:
- "Qual a cotação do dólar?"
- "Quanto está o euro?"
- "Converter USD para BRL"
- "Câmbio de libras"

## Estrutura do projeto

```
bank_agent/
├── src/
│   ├── agents/
│   │   ├── base_agent.py                   # Classe base para agentes
│   │   ├── triagem.py                      # Agente de triagem/autenticação
│   │   ├── credito.py                      # Agente de crédito
│   │   ├── entrevista_credito.py           # Agente de entrevista
│   │   └── cambio.py                       # Agente de câmbio
│   ├── data/
│   │   ├── clientes.csv                    # Base de clientes
│   │   ├── score_limite.csv                # Relação score/limite
│   │   └── solicitacoes_aumento_limite.csv # Histórico de solicitações
│   ├── ui/
│   │   └── app.py                          # Interface Streamlit
│   ├── config.py                           # Configurações do sistema
│   └── utils.py                            # Funções auxiliares
├── requirements.txt
├── setup.sh
└── README.md
```

## Dependências Principais

- `streamlit`: interface web interativa
- `google-generativeai`: integração com Gemini API
- `pandas`: manipulação de dados
- `requests`: requisições HTTP para API de câmbio
- `python-dotenv`: gerenciamento de variáveis de ambiente

## Problemas comuns

### Erro ao iniciar: API key not found

Se você receber um erro relacionado à chave de API ao executar a aplicação:

1. Verifique se o arquivo `.env` existe na raiz do projeto
2. Certifique-se de que a variável `GOOGLE_API_KEY` está definida no arquivo `.env`
3. Se o problema persistir, defina a variável no terminal:

```bash
export GOOGLE_API_KEY=sua-chave-aqui
```

Para Windows:
```cmd
set GOOGLE_API_KEY=sua-chave-aqui
```

### Streamlit não reconhecido

Se o comando `streamlit` não for encontrado:
- Verifique se o ambiente virtual está ativado
- Reinstale as dependências: `pip install -r requirements.txt`

## Configurações

O arquivo `src/config.py` contém parâmetros configuráveis:

- `MAX_AUTHENTICATION_ATTEMPTS`: Número máximo de tentativas de autenticação (padrão: 3)
- `DEFAULT_MODEL`: Modelo do Gemini utilizado (padrão: "gemini-1.5-flash")
- Pesos para cálculo de score de crédito
- Moedas suportadas para consulta de câmbio

## Dados de teste

O sistema inclui dados de teste em formato CSV. Para adicionar novos clientes ou modificar informações:

1. **clientes.csv**: Cadastro de clientes (CPF, nome, data de nascimento, score, limite)
2. **score_limite.csv**: Tabela de correlação entre score de crédito e limite máximo
3. **solicitacoes_aumento_limite.csv**: Registro de solicitações de aumento de limite

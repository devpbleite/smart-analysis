# Painel InSight - Gestão de Estoque Inteligente com IA

Um painel administrativo para consulta e análise de estoque. O usuário digita perguntas utilizando linguagem natural (como "quantos produtos vencem amanhã?") e o sistema converte a pergunta em uma busca no banco de dados, retornando a resposta em texto diretamente na tela do chat.

## Instalação e Execução

O projeto é dividido em duas partes: o **Backend** (onde rodam as regras de negócio e a inteligência artificial) e o **Frontend** (a interface visual de chat na web construída com React).

### 1. Configurando o Ambiente

Primeiro, entre na pasta do backend e crie seu arquivo `.env`. Dentro dele, preencha a sua chave de acesso da API (`GROQ_API_KEY`).

Certifique-se de instalar as bibliotecas do Python necessárias para o backend:
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # No Windows
pip install -r requirements.txt
```

### 2. Preparando os Dados (DuckDB)

Ainda dentro da pasta `backend`, caso seja sua primeira vez, precisamos criar o banco de dados e alimentá-lo com dados fictícios:
```bash
python scripts/setup_duckdb.py
python scripts/seed_duckdb.py
```

### 3. Rodando o Backend (API)

Ainda no mesmo terminal, dentro de `backend`, com o ambiente virtual (venv) ativado, inicie o motor Python:
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```
A API ficará disponível servindo de ponte de comunicação do sistema.

### 4. Rodando o Frontend (Telas)

Abra um segundo terminal, entre na pasta do front e inicie o servidor com o Node.js:
```bash
cd frontend
npm install
npm run dev
```
Acesse o link gerado no terminal para abrir o painel.

## Acesso Temporário

Para acessar o sistema de testes na tela inicial, utilize a seguinte credencial fornecida no código:
- **Credencial de Acesso**: admin
- **Chave de Segurança**: admin

## Como Funciona

- **Interface simples:** O painel conta com um modelo limpo de conversa e uma barra lateral (menu) contendo algumas perguntas de negócios prontas para clique rápido.
- **Consultas transparentes:** O código traduz o texto livre que o usuário envia para comandos de manipulação de dados em SQL. O usuário nunca precisa saber programar para ler o estoque.
- **Validação:** Lógicas embutidas ajudam a identificar produtos que estão perto da data de descarte ou gerenciar valores atrelados a cada produto no portfólio.

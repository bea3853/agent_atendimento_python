# Agente Chatbot

Chatbot de conversação geral construído em **Python + Streamlit**, usando a
**OpenRouter** (modelos gratuitos) como provedor de LLM. Memória apenas de
sessão — o histórico não é salvo em banco de dados nem em arquivo.

## Stack

- **Python 3.11+**
- **Streamlit** — interface de chat
- **OpenRouter** (`:free`) — API do modelo de linguagem
- **GitHub** — versionamento
- **Render** — hospedagem/deploy

## Estrutura do projeto

```
agente-chatbot/
├── app.py                 # interface Streamlit (camada de UI)
├── openrouter_client.py   # chamada à API da OpenRouter (camada de serviço)
├── config.py              # leitura de variáveis de ambiente
├── requirements.txt
├── .env.example
├── .gitignore
└── render.yaml             # blueprint para deploy automatizado no Render
```

A separação entre `app.py` (UI) e `openrouter_client.py` (chamada à API) é
proposital: a lógica de comunicação com o modelo pode ser testada e reutilizada
sem depender do Streamlit.

## Rodando localmente

1. Clone o repositório e entre na pasta:
   ```bash
   git clone https://github.com/SEU-USUARIO/agente-chatbot.git
   cd agente-chatbot
   ```
2. Crie um ambiente virtual e instale as dependências:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Copie `.env.example` para `.env` e preencha sua chave da OpenRouter:
   ```bash
   cp .env.example .env
   ```
   Obtenha uma chave gratuita em https://openrouter.ai/keys (não exige cartão de crédito).
4. Rode o app:
   ```bash
   streamlit run app.py
   ```

## Subindo para o GitHub

```bash
git init
git add .
git commit -m "Chatbot inicial com Streamlit + OpenRouter"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/agente-chatbot.git
git push -u origin main
```

⚠️ O `.gitignore` já exclui o `.env` — confirme que ele nunca aparece em
`git status` antes de dar push. Só o `.env.example` (sem valores reais) deve ir para o repositório.

## Deploy no Render

**Opção A — Blueprint (recomendado, usa o `render.yaml` já incluso):**
1. No painel do Render, clique em **New +** → **Blueprint**.
2. Selecione o repositório `agente-chatbot` no GitHub.
3. O Render vai detectar o `render.yaml` automaticamente.
4. Quando pedir a variável `OPENROUTER_API_KEY`, cole sua chave (ela foi
   marcada como `sync: false` no blueprint justamente para não ser commitada).

**Opção B — Manual:**
1. **New +** → **Web Service** → conecte o repositório.
2. Runtime: `Python 3`.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
5. Em **Environment**, adicione `OPENROUTER_API_KEY` com sua chave.
6. Plano: **Free** é suficiente para prototipagem.

## Sobre o modelo gratuito da OpenRouter

Este projeto usa `meta-llama/llama-3.3-70b-instruct:free` por padrão — um dos
modelos gratuitos mais estáveis da OpenRouter atualmente. **A lista de modelos
`:free` muda com frequência** (modelos são adicionados e removidos sem aviso
prévio). Se receber erro de modelo indisponível:

1. Verifique a lista atual em https://openrouter.ai/models (filtre por preço zero).
2. Troque a variável de ambiente `OPENROUTER_MODEL` para outro ID `:free`.
3. Alternativa simples: use `openrouter/free`, o auto-router da própria
   OpenRouter, que escolhe um modelo gratuito disponível automaticamente.

O plano gratuito tem limite de requisições por minuto/dia (varia por modelo) —
o app já trata o erro 429 (rate limit) e 401 (chave inválida) com mensagens
claras para o usuário, sem vazar detalhes internos.

## Segurança

- A chave da API nunca é hardcoded — vem sempre de variável de ambiente.
- Erros da API externa são tratados e logados; o usuário final só vê mensagens
  genéricas e seguras, nunca stack traces ou corpo de resposta cru.
- Entrada do usuário é validada (limite de tamanho) antes de ser enviada ao modelo.
- O histórico enviado ao modelo é truncado para não crescer indefinidamente.

## Limitações desta versão (por design)

- Sem memória entre sessões (nenhuma conversa é persistida).
- Sem autenticação de usuário — qualquer pessoa com a URL pode usar o chat.
  Se for expor publicamente, considere adicionar autenticação antes do deploy.

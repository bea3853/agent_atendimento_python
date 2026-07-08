"""
Configurações da aplicação.

Todas as configurações sensíveis (API keys) vêm de variáveis de ambiente,
nunca hardcoded no código-fonte. Localmente, use um arquivo `.env`
(veja `.env.example`); no Render, defina as variáveis em
Environment > Environment Variables no painel do serviço.
"""

import os

from dotenv import load_dotenv

load_dotenv()  # não faz nada em produção se o .env não existir — as env vars do Render prevalecem


class ConfigError(Exception):
    """Erro de configuração ausente ou inválida."""


def _get_required(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ConfigError(
            f"Variável de ambiente obrigatória '{name}' não foi definida. "
            f"Configure-a no arquivo .env (local) ou nas Environment Variables do Render."
        )
    return value


# Chave da API da OpenRouter — obrigatória, nunca deve ter um valor default no código.
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

# Modelo gratuito usado por padrão. A lista de modelos ":free" da OpenRouter muda com
# frequência — confira a disponibilidade atual em https://openrouter.ai/models antes
# de ir para produção, e ajuste via variável de ambiente se necessário.
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "openrouter/free")

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Cabeçalhos opcionais recomendados pela OpenRouter para identificar a aplicação
# (ajudam a evitar throttling agressivo e aparecem nos rankings públicos deles).
APP_TITLE = os.environ.get("APP_TITLE", "Agente Chatbot")
APP_URL = os.environ.get("APP_URL", "https://github.com/")

# Limite de caracteres por mensagem do usuário — validação simples de entrada
# para evitar prompts absurdamente longos consumindo o rate limit do plano free.
MAX_MESSAGE_LENGTH = int(os.environ.get("MAX_MESSAGE_LENGTH", "4000"))

# Quantidade máxima de mensagens anteriores mantidas no histórico da sessão,
# para não estourar o contexto do modelo em conversas muito longas.
MAX_HISTORY_MESSAGES = int(os.environ.get("MAX_HISTORY_MESSAGES", "20"))

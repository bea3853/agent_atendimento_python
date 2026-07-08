"""
Cliente para a API da OpenRouter.

Mantido separado da camada de UI (Streamlit) de propósito: assim a lógica de
chamada ao modelo pode ser testada isoladamente e reutilizada fora do app,
sem depender de `st.session_state` ou de qualquer coisa do Streamlit.
"""

from __future__ import annotations

import logging

import requests

import config

logger = logging.getLogger(__name__)

# Timeout de rede explícito — nunca deixar uma requisição travada indefinidamente
# esperando resposta de uma API externa.
REQUEST_TIMEOUT_SECONDS = 60


class OpenRouterError(Exception):
    """Erro ao chamar a API da OpenRouter — mensagem já é segura para exibir ao usuário."""


def send_chat_message(messages: list[dict[str, str]]) -> str:
    """
    Envia o histórico de mensagens para o modelo configurado na OpenRouter e
    retorna o texto da resposta.

    `messages` segue o formato padrão OpenAI-compatible:
    [{"role": "system"|"user"|"assistant", "content": "..."}]

    Levanta `OpenRouterError` com uma mensagem segura para o usuário em caso de
    falha — os detalhes técnicos (status code, corpo da resposta) só vão para o
    log, nunca para a tela.
    """
    if not config.OPENROUTER_API_KEY:
        raise OpenRouterError(
            "A chave da API da OpenRouter não está configurada. "
            "Defina a variável de ambiente OPENROUTER_API_KEY."
        )

    headers = {
        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        # Recomendado pela OpenRouter para identificar a origem das chamadas.
        "HTTP-Referer": config.APP_URL,
        "X-Title": config.APP_TITLE,
    }

    payload = {
        "model": config.OPENROUTER_MODEL,
        "messages": messages,
    }

    try:
        response = requests.post(
            f"{config.OPENROUTER_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.exceptions.Timeout as exc:
        logger.warning("Timeout ao chamar a OpenRouter: %s", exc)
        raise OpenRouterError(
            "O modelo demorou demais para responder. Tente novamente em instantes."
        ) from exc
    except requests.exceptions.RequestException as exc:
        logger.warning("Erro de rede ao chamar a OpenRouter: %s", exc)
        raise OpenRouterError(
            "Não foi possível conectar à OpenRouter agora. Verifique sua conexão e tente novamente."
        ) from exc

    if response.status_code == 401:
        logger.warning("OpenRouter retornou 401 — chave inválida ou expirada.")
        raise OpenRouterError("Chave da API inválida ou expirada. Verifique OPENROUTER_API_KEY.")

    if response.status_code == 429:
        logger.warning("OpenRouter retornou 429 — rate limit do plano free atingido.")
        raise OpenRouterError(
            "Limite de requisições do plano gratuito foi atingido. Aguarde um pouco e tente novamente."
        )

    if not response.ok:
        # Nunca repassar o corpo cru da resposta ao usuário — pode conter detalhes internos.
        logger.error("OpenRouter retornou status %s: %s", response.status_code, response.text[:500])
        raise OpenRouterError("O serviço de IA retornou um erro inesperado. Tente novamente mais tarde.")

    try:
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, ValueError) as exc:
        logger.error("Resposta da OpenRouter em formato inesperado: %s", response.text[:500])
        raise OpenRouterError("Resposta inesperada do serviço de IA. Tente novamente.") from exc

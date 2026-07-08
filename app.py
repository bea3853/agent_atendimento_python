"""
Chatbot de conversação geral — interface Streamlit.

Memória apenas de sessão: o histórico vive em `st.session_state` e é perdido
quando a aba é fechada ou o app reinicia. Não há persistência em banco/arquivo
por design (conforme decidido para esta versão do agente).
"""

import streamlit as st

import config
from openrouter_client import OpenRouterError, send_chat_message

SYSTEM_PROMPT = (
    "Você é um assistente de conversação prestativo, claro e objetivo. "
    "Responda em português do Brasil, salvo se o usuário escrever em outro idioma."
)

st.set_page_config(page_title=config.APP_TITLE, page_icon="💬")
st.title(config.APP_TITLE)
st.caption(f"Modelo: `{config.OPENROUTER_MODEL}` via OpenRouter (plano gratuito)")

# --- Estado da sessão -------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# --- Barra lateral -----------------------------------------------------------

with st.sidebar:
    st.subheader("Sobre")
    st.write(
        "Chatbot de conversação geral, sem memória entre sessões. "
        "Cada nova aba/execução começa uma conversa do zero."
    )
    if st.button("Limpar conversa"):
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.rerun()

    if not config.OPENROUTER_API_KEY:
        st.error(
            "OPENROUTER_API_KEY não configurada. "
            "Defina a variável de ambiente antes de usar o chat."
        )

# --- Histórico exibido (sem a mensagem de sistema) --------------------------

for message in st.session_state.messages:
    if message["role"] == "system":
        continue
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Entrada do usuário ------------------------------------------------------

user_input = st.chat_input("Digite sua mensagem...")

if user_input:
    # Validação de entrada: tamanho máximo, para não estourar o rate limit
    # do plano gratuito com prompts excessivamente longos.
    if len(user_input) > config.MAX_MESSAGE_LENGTH:
        st.warning(
            f"Mensagem muito longa ({len(user_input)} caracteres). "
            f"O limite é de {config.MAX_MESSAGE_LENGTH} caracteres — resuma e tente novamente."
        )
    else:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Trunca o histórico enviado ao modelo para não estourar o contexto
        # em conversas muito longas — mantém a mensagem de sistema + últimas N.
        system_message = st.session_state.messages[0]
        recent_messages = st.session_state.messages[1:][-config.MAX_HISTORY_MESSAGES :]
        history_to_send = [system_message, *recent_messages]

        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                try:
                    reply = send_chat_message(history_to_send)
                except OpenRouterError as exc:
                    reply = f"⚠️ {exc}"
            st.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})

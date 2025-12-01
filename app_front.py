import streamlit as st
import asyncio
from pathlib import Path
from openai import OpenAI
from agents import Agent, Runner
from agents.model_settings import ModelSettings
from agents.mcp import MCPServerStreamableHttp

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Safe-Buyer-AI",
    page_icon="⚖️",
    layout="centered"
)

client = OpenAI()

# --- Lógica do Backend ---

async def processar_queixa_agente(queixa_usuario: str):
    """
    Função assíncrona que conecta ao servidor MCP, envia a queixa
    e retorna a resposta processada.
    """
    
    # 1) Criar o MCP server client (HTTP)
    # Mantemos as mesmas configurações do seu script CLI
    mcp_server = MCPServerStreamableHttp(
        name="e-consumidor",
        params={
            "url": "http://127.0.0.1:8000/mcp",
            "timeout": 60,
            "sse_read_timeout": 60*5
        },
        cache_tools_list=True,
        client_session_timeout_seconds=60,
    )

    try:
        # 2) Conectar ao servidor MCP
        await mcp_server.connect()

        # 3) Criar o agente
        JudgeAgent = Agent(
            name="Consultor automatico",
            instructions=(
                "Você é o agente julgador de casos. "
                "Quando receber uma queixa de consumidor, primeiro verifique se é realmente "
                "uma queixa relacionada ao Código de Defesa do Consumidor. "
                "Se for uma queixa válida, use a tool `processar_queixa` passando a queixa completa, "
                "e devolva ao usuário exatamente o que foi recebido como retorno. "
                "Formate a saída em Markdown para melhor leitura."
            ),
            mcp_servers=[mcp_server],
            model_settings=ModelSettings(
                tool_choice="auto",
            ),
        )

        # 4) Rodar o runner
        result = await Runner.run(JudgeAgent, queixa_usuario)
        return result.final_output

    except Exception as e:
        return f"Ocorreu um erro ao processar sua solicitação: {str(e)}"
    
    finally:
        # 5) Limpar conexão
        await mcp_server.cleanup()


# --- Interface do Streamlit ---

st.title("⚖️ Safe-Buyer-AI")
st.markdown("### Assistente Jurídico para Consumidores (via MCP)")
st.caption("Descreva seu problema abaixo para receber uma análise baseada no Código de Defesa do Consumidor.")

# Inicializa o histórico do chat na sessão se não existir
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe as mensagens anteriores do chat a cada recarregamento da página
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Captura a entrada do usuário
if prompt := st.chat_input("Relate o problema aqui..."):
    
    # 1. Adiciona e exibe mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Processa a resposta do Agente
    with st.chat_message("assistant"):
        with st.spinner("Consultando o servidor MCP e analisando o caso..."):
            try:
                resposta_final = asyncio.run(processar_queixa_agente(prompt))
                st.markdown(resposta_final)
                
                # 3. Adiciona resposta ao histórico
                st.session_state.messages.append({"role": "assistant", "content": resposta_final})
            except Exception as e:
                st.error(f"Erro de conexão ou execução: {e}")

with st.sidebar:
    st.header("Sobre")
    st.info(
        "Este assistente utiliza um servidor MCP (Model Context Protocol) "
        "para processar queixas e buscar referências no CDC."
    )
    if st.button("Limpar Conversa"):
        st.session_state.messages = []
        st.rerun()
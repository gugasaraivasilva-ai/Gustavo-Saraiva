import streamlit as st
import asyncio
import threading
from agno.agent import Agent
from agno.tools.mcp import MCPTools
from agno.models.openai import OpenAIChat

st.title("📚 Assistente de Documentação")

pergunta = st.text_input("Digite sua dúvida:")

if st.button("Perguntar") and pergunta:
    with st.spinner("Buscando na documentação..."):

        async def rodar():
            async with MCPTools(
                url="https://docs.solucao360.app/~gitbook/mcp",
                transport="streamable-http"
            ) as mcp_tools:
                agent = Agent(
                    name="Doc Assistant",
                    model=OpenAIChat(id="gpt-4o"),
                    instructions="""
                    Você responde perguntas com base na documentação.
                    Sempre use a ferramenta disponível para buscar a resposta.
                    Não invente informações.
                    Faça um passo a passo de como ajudar o usuário.
                    Sempre envie o link da documentação.
                    Caso não encontre a resposta, sugira contato com o suporte.
                    """,
                    tools=[mcp_tools]
                )
                res = await agent.arun(pergunta)
                return res.content

        resultado = {"resposta": None, "erro": None}

        def executar():
            try:
                resultado["resposta"] = asyncio.run(rodar())
            except Exception as e:
                resultado["erro"] = str(e)

        thread = threading.Thread(target=executar)
        thread.start()
        thread.join()

        if resultado["erro"]:
            st.error(f"Erro: {resultado['erro']}")
        else:
            st.markdown(resultado["resposta"])
import asyncio
from agno.agent import Agent
from agno.tools.mcp import MCPTools
from agno.models.openai import OpenAIChat  

async def main():
    pergunta = input ("Digite a sua dúvida: ")

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
            Faça um passo a passo de como ajudar o usuário a resolver o problema, usando a documentação como base.
            Não se esqueça de sempre enviar o link da documentação para o usuário, para que ele possa consultar mais detalhes.
            Caso a resposta não esteja na documentação, diga que não sabe a resposta e sugira entrar em contato com o suporte.
            Seja sempre o mais claro e objetivo possível, para que o usuário consiga resolver o problema com as informações fornecidas.
            """,
            tools=[mcp_tools]
        )
        res = await agent.arun(pergunta)
    print (res.content)
    

asyncio.run(main())

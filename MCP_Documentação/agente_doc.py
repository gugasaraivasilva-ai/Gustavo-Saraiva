import sqlite3
import asyncio
import numpy as np
from agno.agent import Agent
from agno.tools.mcp import MCPTools
from agno.models.openai import OpenAIChat
from sentence_transformers import SentenceTransformer

# --- Banco de dados ---
conn = sqlite3.connect("memoria.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS historico (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pergunta TEXT,
        resposta TEXT
    )
""")
conn.commit()

# --- Cache em memória ---
cache = {}

def buscar_cache(pergunta):
    return cache.get(pergunta)

def salvar_cache(pergunta, resposta):
    cache[pergunta] = resposta

# --- Memória semântica ---
model = SentenceTransformer('all-MiniLM-L6-v2')
memoria = []

def salvar_memoria(pergunta, resposta):
    embedding = model.encode(pergunta)
    memoria.append((pergunta, resposta, embedding))

def buscar_memoria(pergunta, limite=1):  # ✅ fora de salvar_memoria
    if not memoria:
        return None
    embedding_query = model.encode(pergunta)

    def similaridade(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    resultados = sorted(
        memoria,
        key=lambda item: similaridade(embedding_query, item[2]),
        reverse=True
    )
    return resultados[:limite]

# --- Persistência ---
def salvar_interacao(pergunta, resposta):
    cursor.execute(
        "INSERT INTO historico (pergunta, resposta) VALUES (?, ?)",
        (pergunta, resposta)
    )
    conn.commit()

# --- Agente principal ---
async def main():
    pergunta = input("Digite a sua dúvida: ")

    # Verificar cache antes de chamar o agente
    resposta_cache = buscar_cache(pergunta)
    if resposta_cache:
        print("⚡ Cache usado")
        print(resposta_cache)
        return

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
            Se for feita uma pergunta fora do escopo da documentação, informe que não pode ajudar.
            """,
            tools=[mcp_tools]
        )

        # Adicionar contexto da memória semântica, se houver
        contexto = ""
        memoria_relacionada = buscar_memoria(pergunta)
        if memoria_relacionada:
            contexto = f"\n\nContexto de interação anterior: {memoria_relacionada[0][1]}"

        res = await agent.arun(pergunta + contexto)
        resposta = res.content

    print(resposta)

    # Salvar nas três camadas
    salvar_cache(pergunta, resposta)
    salvar_interacao(pergunta, resposta)
    salvar_memoria(pergunta, resposta)

asyncio.run(main())
conn.close()  # ✅ fechar conexão ao finalizar
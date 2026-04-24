"""
Configura e retorna a instância do LLM (Large Language Model).
Atualmente usa Groq com LLaMA-3.3-70b (free tier).

Para trocar de provedor, basta modificar este arquivo —
o resto do projeto não precisa mudar.
"""

from langchain_groq import ChatGroq
from config.settings import settings


def get_llm() -> ChatGroq:
    """
    Cria e retorna o LLM configurado.

    temperature=0 garante respostas determinísticas e baseadas
    nos dados — sem "criatividade" que poderia inventar números.
    """
    return ChatGroq(
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        api_key=settings.groq_api_key,
    )

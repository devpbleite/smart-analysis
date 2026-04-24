"""
Fábrica do agente LangChain SQL.

Recebe o LLM e o banco por injeção de dependência,
facilitando testes e futura troca de componentes.
"""

from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq

from agent.prompts import SYSTEM_PROMPT
from config.settings import settings


def build_agent(llm: ChatGroq, db: SQLDatabase):
    """
    Cria e retorna o agente SQL configurado.
    """
    return create_sql_agent(
        llm=llm,
        db=db,
        agent_type="openai-tools",
        extra_tools=[],
        prefix=SYSTEM_PROMPT,
        verbose=settings.agent_verbose,
        max_iterations=settings.agent_max_iterations,
        handle_parsing_errors=True,
    )

"""
Ponto único de configuração da aplicação.
Carrega variáveis do .env e valida antes de qualquer módulo usar.
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    database_url: str
    groq_api_key: str
    llm_model: str
    llm_temperature: float
    db_sample_rows: int
    agent_max_iterations: int
    agent_verbose: bool

    @classmethod
    def from_env(cls) -> "Settings":

        database_url = os.getenv("DATABASE_URL", "")
        groq_api_key = os.getenv("GROQ_API_KEY", "")

        missing = [k for k, v in {"DATABASE_URL": database_url, "GROQ_API_KEY": groq_api_key}.items() if not v]
        if missing:
            raise EnvironmentError(
                f"Variáveis de ambiente obrigatórias não encontradas: {', '.join(missing)}\n"
                "Verifique o arquivo .env na raiz do projeto."
            )

        return cls(
            database_url=database_url,
            groq_api_key=groq_api_key,
            llm_model=os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"),
            llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0")),
            db_sample_rows=int(os.getenv("DB_SAMPLE_ROWS", "1")),
            agent_max_iterations=int(os.getenv("AGENT_MAX_ITERATIONS", "10")),
            agent_verbose=os.getenv("AGENT_VERBOSE", "true").lower() == "true",
        )

settings = Settings.from_env()

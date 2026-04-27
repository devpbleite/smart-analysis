from config.settings import settings  
from core.database import get_database
from core.llm import get_llm
from agent.agent import build_agent
from agent.chat import run_chat


def main() -> None:
    db = get_database()
    llm = get_llm()
    agent = build_agent(llm=llm, db=db)
    run_chat(agent)


if __name__ == "__main__":
    main()

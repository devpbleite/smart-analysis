import os
import sys

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from core.database import get_database
from core.llm import get_llm
from agent.agent import build_agent

app = FastAPI(title="InSight AI API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent_instance = None

def get_agent():
    global agent_instance
    if agent_instance is None:
        print("🟡 Inicializando o Motor AI e conexões ao DuckDB...")
        try:
            db = get_database()
            llm = get_llm()
            agent_instance = build_agent(llm=llm, db=db)
            print("🟢 Inteligência carregada com sucesso!")
        except Exception as e:
            print(f"🔴 Falha severa na montagem do agente: {e}")
            raise e
    return agent_instance

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    
class Token(BaseModel):
    access_token: str
    token_type: str

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@app.on_event("startup")
async def startup_event():
    get_agent()

@app.get("/")
def health_check():
    return {"status": "ok", "message": "InSight AI API is running."}

@app.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):

    if form_data.username == "admin" and form_data.password == "admin":
        return {"access_token": "insight_master_token_2026", "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Usuário ou senha incorretos. Acesso bloqueado.")

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest, token: str = Depends(oauth2_scheme)):
    try:
        agent = get_agent()
        resposta = agent.invoke({"input": payload.message})
        return ChatResponse(response=resposta["output"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)

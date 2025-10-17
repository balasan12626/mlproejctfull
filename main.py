from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import timedelta
from typing import Optional
import os
import google.generativeai as genai
from crewai import Agent, Task, Crew
import pathlib

from models import UserCreate, UserLogin, Token, AIRequest, AIResponse
from auth import (
    authenticate_user,
    create_user,
    create_access_token,
    decode_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

app = FastAPI(title="Full-Stack AI App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY environment variable is required. "
        "Please set it in your Replit Secrets or environment variables."
    )

genai.configure(api_key=GEMINI_API_KEY)

gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')

def get_current_user(token: str):
    username = decode_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return username

@app.post("/api/register", response_model=Token)
async def register(user: UserCreate):
    db_user = create_user(user.username, user.email, user.password)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/login", response_model=Token)
async def login(user: UserLogin):
    authenticated_user = authenticate_user(user.username, user.password)
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/hello")
async def hello():
    return {"message": "Hello from FastAPI backend!"}

@app.post("/api/ai/generate", response_model=AIResponse)
async def generate_ai_response(request: AIRequest):
    try:
        os.environ["OPENAI_API_KEY"] = GEMINI_API_KEY
        os.environ["OPENAI_MODEL_NAME"] = "gemini/gemini-2.0-flash-exp"
        
        researcher_agent = Agent(
            role='Senior Research Analyst',
            goal='Research and analyze information to provide accurate insights',
            backstory='You are an expert research analyst with deep knowledge across multiple domains. You excel at finding accurate information and providing well-reasoned insights.',
            verbose=False,
            allow_delegation=False,
            llm="gemini/gemini-2.0-flash-exp"
        )
        
        writer_agent = Agent(
            role='Content Writer',
            goal='Transform research into clear, engaging, and helpful responses',
            backstory='You are a skilled content writer who excels at making complex information accessible and easy to understand. You create responses that are both informative and engaging.',
            verbose=False,
            allow_delegation=False,
            llm="gemini/gemini-2.0-flash-exp"
        )
        
        research_task = Task(
            description=f'Research and analyze this query: {request.prompt}. Provide detailed findings and key insights.',
            agent=researcher_agent,
            expected_output='A comprehensive analysis with key findings and insights about the query'
        )
        
        writing_task = Task(
            description=f'Based on the research findings, create a clear, helpful, and engaging response to: {request.prompt}',
            agent=writer_agent,
            expected_output='A well-written, user-friendly response that addresses the query effectively'
        )
        
        crew = Crew(
            agents=[researcher_agent, writer_agent],
            tasks=[research_task, writing_task],
            verbose=False
        )
        
        crew_result = crew.kickoff()
        final_response = str(crew_result)
        
        gemini_response = gemini_model.generate_content(
            f"Refine and polish this response to make it even better: {final_response}"
        )
        
        return AIResponse(
            response=gemini_response.text,
            model="CrewAI Agents + Gemini 2.5 Flash"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI generation failed: {str(e)}"
        )

frontend_dist = pathlib.Path(__file__).parent / "frontend" / "dist"

if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        file_path = frontend_dist / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        
        return FileResponse(frontend_dist / "index.html")
else:
    @app.get("/")
    async def root():
        return {
            "message": "Backend is running! Frontend not built yet.",
            "instructions": "Run 'bash run.sh' to build frontend and start the server."
        }

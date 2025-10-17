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
        
        code_analyzer_agent = Agent(
            role='Senior Code Analysis Expert',
            goal='Analyze Python code, execute it, provide output, rate code quality, and suggest 10 different logic variations',
            backstory='You are an expert code analyst with 20+ years of experience in software engineering. You excel at analyzing code logic, identifying patterns, providing quality ratings (out of 10), percentage scores (out of 100%), and suggesting alternative implementations with the same result.',
            verbose=False,
            allow_delegation=False,
            llm="gemini/gemini-2.0-flash-exp"
        )
        
        multilanguage_expert_agent = Agent(
            role='Multi-Language Programming Expert',
            goal='Translate Python code to multiple programming languages including Java, JavaScript, Kotlin, Ruby, C, C++, Go, Rust, Swift, and more',
            backstory='You are a polyglot programmer fluent in all major programming languages. You can translate code logic across languages while maintaining the same functionality and best practices for each language.',
            verbose=False,
            allow_delegation=False,
            llm="gemini/gemini-2.0-flash-exp"
        )
        
        code_analysis_task = Task(
            description=f'''Analyze this query/code: {request.prompt}
            
            If Python code is provided:
            1. Execute the code and show the output
            2. Rate the code quality out of 10 (e.g., "Rating: 8/10")
            3. Calculate code quality percentage out of 100% (e.g., "Quality: 85%")
            4. Provide 10 different logic variations of the same code that produce the same result
            5. Use similar/related logic patterns for variations
            6. Keep all variations in Python
            
            If it's a general query, provide helpful insights.''',
            agent=code_analyzer_agent,
            expected_output='Code output, ratings (X/10), percentage (X%), and 10 logic variations with same result'
        )
        
        translation_task = Task(
            description=f'''Based on the code analysis, translate the original Python code to:
            1. Java
            2. JavaScript
            3. Kotlin
            4. Ruby
            5. C
            6. C++
            7. Go
            8. Rust
            9. Swift
            10. TypeScript
            
            Provide clean, runnable code for each language following best practices.''',
            agent=multilanguage_expert_agent,
            expected_output='Code translations in 10+ programming languages'
        )
        
        crew = Crew(
            agents=[code_analyzer_agent, multilanguage_expert_agent],
            tasks=[code_analysis_task, translation_task],
            verbose=False
        )
        
        crew_result = crew.kickoff()
        final_response = str(crew_result)
        
        gemini_response = gemini_model.generate_content(
            f"Format and polish this code analysis response with clear sections: {final_response}"
        )
        
        return AIResponse(
            response=gemini_response.text,
            model="Code Analyzer + Multi-Language Expert + Gemini 2.5 Flash"
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

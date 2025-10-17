from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import timedelta
from typing import Optional
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
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
            role='Expert Python Code Analyst',
            goal='Analyze Python code, execute it, provide output with ratings, and generate 10 different logic variations in the SAME Python language',
            backstory='You are a Python expert with 20+ years of experience. When given Python code, you execute it, rate its quality (X/10 and X%), and provide 10 different logic variations in Python using similar patterns. All variations must produce the same result but use different approaches.',
            verbose=False,
            allow_delegation=False,
            llm="gemini/gemini-2.0-flash-exp"
        )
        
        multilanguage_expert_agent = Agent(
            role='Multi-Language Code Translator',
            goal='Ask user which language they want, then provide 10 different logic variations in that specific language',
            backstory='You are a polyglot programmer. After the Python analysis, you ask: "Do you want this code in another language? (e.g., Java, JavaScript, C++, etc.)". If they specify a language like Java, you provide 10 different logic variations in Java with the same result.',
            verbose=False,
            allow_delegation=False,
            llm="gemini/gemini-2.0-flash-exp"
        )
        
        code_analysis_task = Task(
            description=f'''Analyze this Python code: {request.prompt}
            
            1. Execute the code and show the OUTPUT
            2. Rate code quality: X/10 (e.g., "8/10")
            3. Calculate percentage: X% (e.g., "85%")
            4. Provide 10 DIFFERENT LOGIC variations in PYTHON ONLY (same result, different logic)
            5. Each variation must use similar/related logic patterns
            6. Keep ALL 10 variations in Python language
            
            Format properly with clear sections.''',
            agent=code_analyzer_agent,
            expected_output='Code output, rating (X/10), percentage (X%), and 10 Python logic variations'
        )
        
        translation_task = Task(
            description=f'''After Python analysis:
            
            1. Ask: "Do you want this code in another language? (Java, JavaScript, C++, Kotlin, Ruby, Go, Rust, Swift, TypeScript, C, etc.)"
            2. If user specifies a language (e.g., "Java"), provide 10 different logic variations in that ONE language
            3. All 10 variations must produce same result but use different logic patterns
            4. If user wants multiple languages, provide 10 variations for EACH specified language
            
            Provide clean, well-formatted code with proper syntax.''',
            agent=multilanguage_expert_agent,
            expected_output='Question asking for language preference, then 10 variations in requested language'
        )
        
        crew = Crew(
            agents=[code_analyzer_agent, multilanguage_expert_agent],
            tasks=[code_analysis_task, translation_task],
            verbose=False
        )
        
        loop = asyncio.get_event_loop()
        
        def run_crew():
            return crew.kickoff()
        
        def run_gemini(response_text):
            return gemini_model.generate_content(
                f"Format and polish this code analysis response with clear sections: {response_text}"
            )
        
        with ThreadPoolExecutor() as executor:
            crew_result = await loop.run_in_executor(executor, run_crew)
            final_response = str(crew_result)
            gemini_response = await loop.run_in_executor(executor, run_gemini, final_response)
        
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

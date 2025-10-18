from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import timedelta
from typing import Optional
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
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

# ---------------------------- APP CONFIG ----------------------------
app = FastAPI(title="Full-Stack AI App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------- GROQ CONFIG ----------------------------
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY environment variable is required. "
        "Please set it in your Replit Secrets or environment variables."
    )


# ---------------------------- AUTH HELPERS ----------------------------
def get_current_user(token: str):
    username = decode_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return username


# ---------------------------- AUTH ROUTES ----------------------------
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


# ---------------------------- AI ROUTE ----------------------------
@app.post("/api/ai/generate", response_model=AIResponse)
async def generate_ai_response(request: AIRequest):
    try:
        os.environ["OPENAI_API_KEY"] = GROQ_API_KEY
        os.environ["OPENAI_MODEL_NAME"] = "groq/qwen/qwen3-32b"

        # ===================== SINGLE OPTIMIZED AGENT =====================
        code_expert_agent = Agent(
            role="Expert Code Analyst & Multi-Language Translator",
            goal=(
                "Analyze Python code, execute it, rate quality (X/10 and X%), provide 10 Python variations, "
                "then ask if user wants translations to other languages (Java, JavaScript, C++, etc.) "
                "and provide 10 variations in the requested language."
            ),
            backstory=(
                "You are a world-class software engineer with 20+ years of experience across all major programming languages. "
                "You analyze code execution, evaluate quality, generate logic variations, and translate between languages "
                "while preserving exact behavior and output. You provide clear, structured responses with code blocks."
            ),
            verbose=False,
            allow_delegation=False,
            llm="groq/qwen/qwen3-32b"
        )

        # ===================== SINGLE TASK =====================
        analysis_task = Task(
            description=f"""
            Analyze this Python code:
            ```python
            {request.prompt}
            ```

            STEP 1 - Python Analysis:
            1. Execute the code and show OUTPUT
            2. Rate quality: X/10 and X%
            3. Provide 10 Python variations (same result, different logic)

            STEP 2 - Language Options:
            Ask: "Would you like this in another language? (Java, JavaScript, C++, Kotlin, Ruby, Go, Rust, Swift, TypeScript, C)"

            Format with clear sections and code blocks.
            """,
            agent=code_expert_agent,
            expected_output="Code output, rating (X/10, X%), 10 Python variations, and language translation offer"
        )

        # ===================== CREW EXECUTION =====================
        crew = Crew(
            agents=[code_expert_agent],
            tasks=[analysis_task],
            verbose=False
        )

        loop = asyncio.get_event_loop()

        def run_crew():
            return crew.kickoff()

        with ThreadPoolExecutor() as executor:
            crew_result = await loop.run_in_executor(executor, run_crew)

        return AIResponse(
            response=str(crew_result),
            model="Code Analyzer + Multi-Language Expert + Groq Qwen3-32B"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI generation failed: {str(e)}"
        )


# ---------------------------- FRONTEND HANDLER ----------------------------
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

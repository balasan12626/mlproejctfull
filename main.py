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
            role="Senior FastAPI Backend Developer & Code Architect",
            goal=(
                "Act as a 10-year experienced FastAPI backend developer. For EVERY code snippet, provide: "
                "1) Execution output, 2) Quality rating (X/10 and X%), 3) Time complexity analysis, "
                "4) Space complexity analysis, 5) Line-by-line explanation, 6) Best practices & tips, "
                "7) Code variations, 8) Multi-language translations if requested. "
                "ONLY answer coding-related questions."
            ),
            backstory=(
                "You are a senior backend developer with 10+ years of FastAPI, Python, and full-stack experience. "
                "For every code you analyze, you MUST provide: "
                "• **Time Complexity**: Big-O notation (O(1), O(n), O(log n), etc.) with clear explanation "
                "• **Space Complexity**: Memory usage analysis with Big-O notation "
                "• **Line-by-Line Explanation**: Simple, beginner-friendly explanation of each code line "
                "• **Best Practices & Tips**: Professional advice on optimization, patterns, and improvements "
                "• **Code Output**: Simulated execution results with sample inputs and expected outputs "
                "• **Performance Analysis**: Bottlenecks, optimizations, and algorithmic improvements "
                ""
                "You ONLY respond to coding, programming, algorithms, and technical questions. "
                "For non-coding questions, politely redirect: 'I only assist with coding-related questions.'"
            ),
            verbose=False,
            allow_delegation=False,
            llm="groq/qwen/qwen3-32b"
        )

        # Get language labels
        language_map = {
            'python': 'Python', 'javascript': 'JavaScript', 'java': 'Java',
            'cpp': 'C++', 'c': 'C', 'csharp': 'C#', 'go': 'Go', 'rust': 'Rust',
            'kotlin': 'Kotlin', 'swift': 'Swift', 'ruby': 'Ruby', 'php': 'PHP',
            'typescript': 'TypeScript', 'react': 'React', 'angular': 'Angular'
        }
        
        source_lang_label = language_map.get(request.source_language, request.source_language.capitalize())
        target_lang_labels = [language_map.get(lang, lang.capitalize()) for lang in request.target_languages]
        
        # Build task description
        task_description = f"""
        Analyze this {source_lang_label} code:
        ```{request.source_language}
        {request.prompt}
        ```

        MANDATORY ANALYSIS FORMAT FOR THIS CODE:

        ## 1. Code Execution & Output
        - Simulate code execution and show the expected output
        - Provide sample inputs and their expected results
        - If code has errors, explain them clearly

        ## 2. Quality Rating
        - Overall Rating: X/10 (X%)
        - Strengths: (list 3-5 points)
        - Weaknesses/Areas to improve: (list 2-3 points)

        ## 3. Time Complexity Analysis
        - **Time Complexity**: O(?) - Explain which operations dominate
        - Breakdown: Explain complexity of each major operation
        - Example: "Loop iterates n times = O(n), dictionary lookup = O(1), overall = O(n)"

        ## 4. Space Complexity Analysis  
        - **Space Complexity**: O(?) - Explain memory usage
        - Variables/data structures and their memory impact
        - Example: "Array of size n = O(n), constant variables = O(1), overall = O(n)"

        ## 5. Line-by-Line Explanation
        For EVERY line of code, explain in simple terms:
        - Line 1: [what this line does in beginner-friendly language]
        - Line 2: [explanation]
        - etc.

        ## 6. Best Practices & Tips
        - Performance optimization suggestions
        - Code readability improvements
        - Pythonic/idiomatic patterns
        - Security considerations
        - Error handling recommendations

        ## 7. Code Variations ({request.num_variations} variations)
        Provide {request.num_variations} different approaches that produce the SAME output:
        - Variation 1: [brief description of approach]
        ```{request.source_language}
        [code]
        ```
        Time: O(?), Space: O(?)

        ## 8. Performance Comparison
        - Compare variations by speed and memory
        - Recommend best approach for different scenarios
        """
        
        if request.target_languages:
            translations_format = ""
            for lang_label in target_lang_labels:
                translations_format += f"""
        
        ### {lang_label} Translation
        Provide {request.num_variations} variations in {lang_label}:
        
        **Variation 1**: [description]
        ```{lang_label.lower()}
        [code]
        ```
        - **Time**: O(?)
        - **Space**: O(?)
        - **Key Differences from {source_lang_label}**: [explain syntax/pattern differences]
        - **Best Practices**: [language-specific tips]
        """
            
            task_description += f"""

        ## 9. Multi-Language Translation
        Translate to ALL of these languages: {', '.join(target_lang_labels)}
        {translations_format}
        """
        else:
            task_description += """

        ## 9. Translation Options
        Ask: "Would you like this translated to another language? 
        Available: Java, JavaScript, C++, Kotlin, Ruby, Go, Rust, Swift, TypeScript, C"
        """
        
        task_description += """
        
        IMPORTANT RULES:
        - If the user asks a NON-CODING question, respond: "I only assist with coding-related questions. Please ask about code, algorithms, or programming."
        - Always provide time/space complexity for EVERY code snippet
        - Explain code in simple, beginner-friendly terms
        - Use markdown formatting with code blocks
        - Include actual executable code examples
        """
        
        # ===================== SINGLE TASK =====================
        analysis_task = Task(
            description=task_description,
            agent=code_expert_agent,
            expected_output=(
                f"Complete analysis with: 1) Code execution output, 2) Quality rating (X/10, X%), "
                f"3) Time complexity (O-notation), 4) Space complexity (O-notation), "
                f"5) Line-by-line explanation, 6) Best practices & tips, "
                f"7) {request.num_variations} code variations with complexity analysis, "
                f"8) Performance comparison, 9) Multi-language translations if requested with complexity for each"
            )
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

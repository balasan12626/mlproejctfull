# Full-Stack AI Application

## Overview
A complete full-stack AI Code Analyzer application built with FastAPI backend and React frontend. Upload Python code and get instant analysis including: code execution output, quality ratings (X/10), percentage scores (X%), 10 different logic variations, and translations to 10+ programming languages. Powered by CrewAI agents and Google Gemini 2.5 Flash.

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Uvicorn**: ASGI server
- **Python-Jose**: JWT token generation and validation
- **Passlib**: Password hashing with bcrypt
- **CrewAI**: Multi-agent AI orchestration system
- **Groq AI**: Qwen3-32B model integration via LiteLLM

### Frontend
- **React 18**: UI library
- **Vite**: Build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework with dark mode support
- **Axios**: HTTP client
- **React Syntax Highlighter**: Code syntax highlighting with copy buttons
- **React Markdown**: Markdown parsing for formatted responses

## Project Structure

```
fullstack-ai-app/
├── main.py                    # FastAPI application with all routes
├── models.py                  # Pydantic data models
├── auth.py                    # JWT authentication utilities
├── requirements.txt           # Python dependencies
├── run.sh                     # Build and run script
├── .gitignore                 # Git ignore patterns
└── frontend/                  # React application
    ├── package.json           # Node.js dependencies
    ├── vite.config.js         # Vite configuration
    ├── tailwind.config.js     # Tailwind CSS config
    ├── postcss.config.js      # PostCSS config
    ├── index.html             # HTML entry point
    └── src/
        ├── main.jsx           # React entry point
        ├── App.jsx            # Main app component
        ├── index.css          # Global styles
        └── components/
            ├── Login.jsx      # Login page
            ├── Register.jsx   # Registration page
            ├── Dashboard.jsx  # Main dashboard
            └── AIChat.jsx     # AI chat interface
```

## Features

### Authentication
- User registration with email validation
- Secure login with JWT tokens
- Password hashing using bcrypt
- Protected routes requiring authentication
- Token-based session management

### AI Integration - Code Analyzer
- **CrewAI Agent**: Single optimized AI agent for maximum efficiency
  - **Code Expert Agent**: World-class code analyst that:
    - Executes Python code and shows output
    - Rates code quality out of 10 (e.g., "8/10")
    - Calculates quality percentage out of 100% (e.g., "85%")
    - Provides 10 different logic variations with same result
    - Offers multi-language translation (Java, JavaScript, C++, Kotlin, Ruby, Go, Rust, Swift, TypeScript, C)
    - Provides 10 variations in requested language
- **Groq Qwen3-32B**: Ultra-fast AI model powered by Groq's LPU inference
- **Optimized for Free Tier**: Reduced API calls to stay within 50 requests/day limit
- Real-time code analysis interface
- Comprehensive code quality assessment
- No authentication required

### API Endpoints
- `POST /api/register`: User registration
- `POST /api/login`: User login
- `GET /api/hello`: Health check endpoint
- `POST /api/ai/generate`: AI response generation (protected)

### Frontend Features
- **DeepSeek-Style UI**: Clean, full-page chat interface
- **Dark/Light Theme Toggle**: Switch between themes with one click
- **Code Syntax Highlighting**: Dark code blocks with language-specific highlighting
- **Copy Code Buttons**: Easy-to-use copy buttons for each code block
- **Async Responses**: Fast, non-blocking AI responses
- **Modern Design**: Clean, minimal interface optimized for code analysis
- **Language Selection**: Choose source language from 15+ options (Python, Java, JavaScript, C++, React, Angular, etc.)
- **Customizable Variations**: Select how many code variations to generate (1-20)
- **Multi-Language Translation**: Select multiple target languages for automatic translation
- **Smart Filtering**: Source language automatically removed from target language options

## Environment Variables
- `SESSION_SECRET`: Secret key for JWT token signing (managed by Replit Secrets)
- `GROQ_API_KEY`: Groq API key (required, managed by Replit Secrets)

### Security Note
All API keys and secrets are stored securely in Replit Secrets and never hardcoded in the source code. The application will fail to start if required environment variables are missing.

## Running the Application
The application runs automatically via the configured workflow. The workflow:
1. Installs frontend dependencies (npm install)
2. Builds the React frontend (npm run build)
3. Installs Python dependencies (pip install)
4. Starts FastAPI server on port 5000

## Development Notes
- Frontend dev server configured to allow all hosts for Replit environment
- CORS enabled for cross-origin requests
- Static files served from FastAPI for production build
- JWT tokens expire after 30 minutes

## Architecture Decisions
- **Single server deployment**: FastAPI serves both API and static frontend files
- **In-memory user storage**: Using dictionary for user data (replace with database for production)
- **JWT authentication**: Stateless authentication for scalability
- **Vite for frontend**: Fast build times and modern development experience
- **Tailwind CSS**: Rapid UI development with utility classes

## Security Best Practices
- No hardcoded API keys or secrets in source code
- All sensitive credentials stored in Replit Secrets
- Password hashing with bcrypt (cost factor 12)
- JWT tokens with 30-minute expiration
- HTTPS-only in production
- Input validation on all API endpoints
- Form autocomplete attributes for password managers
- Environment variable validation at startup

## Recent Changes
- 2025-10-18: Advanced Language Selection Controls
  - **Source Language Selection**: Dropdown to choose from 15+ programming languages
  - **Custom Variation Count**: Input field to set number of variations (1-20)
  - **Multi-Language Translation**: Multi-select dropdown for target languages
  - **Smart Filtering**: Auto-removes source language from target options
  - **Dynamic Prompts**: AI agent adapts based on user selections
  - **Enhanced UX**: Clean UI with proper validation and state management

- 2025-10-17: Switched to Groq AI
  - **Replaced Gemini with Groq**: Changed from Google Gemini to Groq's Qwen3-32B model
  - **Ultra-Fast Inference**: Groq's LPU provides lightning-fast responses
  - **Removed Gemini Dependency**: Cleaned up google-generativeai package
  - **All Logic Preserved**: Same code analysis, ratings, and translations

- 2025-10-17: API Optimization & Error Fixes
  - **Fixed ThreadPoolExecutor Error**: Resolved "cannot schedule new futures after shutdown" by keeping executor context open
  - **Reduced API Calls**: Optimized from 2 agents + polishing to 1 agent (50% fewer API calls)
  - **Single Agent Architecture**: Combined Code Analyzer + Multi-Language Expert into one efficient agent
  - **Free Tier Optimization**: Stays within Gemini's 50 requests/day limit
  - **Removed Redundant Polishing**: CrewAI output is already well-formatted, no need for extra Gemini call

- 2025-10-17: Major UI Overhaul & Performance Improvements
  - **DeepSeek-Style UI**: Complete redesign with clean, full-page chat interface
  - **Dark/Light Theme**: Added theme toggle with dark mode as default
  - **Async Backend**: Implemented async/await with ThreadPoolExecutor for fast responses
  - **Code Highlighting**: Added react-syntax-highlighter with dark code blocks
  - **Copy Buttons**: Easy copy-to-clipboard for all code blocks
  - **Performance**: Non-blocking AI execution for ChatGPT/Gemini-like speed

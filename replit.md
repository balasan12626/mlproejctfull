# Full-Stack AI Application

## Overview
A complete full-stack web application built with FastAPI backend and React frontend, featuring advanced AI capabilities powered by CrewAI agents working together with Google Gemini 2.5 Flash, providing intelligent and well-researched responses through a clean and modern interface.

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Uvicorn**: ASGI server
- **Python-Jose**: JWT token generation and validation
- **Passlib**: Password hashing with bcrypt
- **CrewAI**: Multi-agent AI orchestration system
- **Google Generative AI**: Gemini 2.5 Flash model integration

### Frontend
- **React 18**: UI library
- **Vite**: Build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **React Router**: Client-side routing
- **Axios**: HTTP client

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

### AI Integration
- **CrewAI Agents**: Multi-agent AI system with specialized roles
  - Research Analyst Agent: Analyzes and researches queries
  - Content Writer Agent: Creates clear, engaging responses
- **Gemini 2.5 Flash**: Google's latest multimodal AI model for final refinement
- Real-time AI chat interface with agent collaboration
- Intelligent, well-researched responses
- No authentication required

### API Endpoints
- `POST /api/register`: User registration
- `POST /api/login`: User login
- `GET /api/hello`: Health check endpoint
- `POST /api/ai/generate`: AI response generation (protected)

### Frontend Features
- Modern, responsive UI with Tailwind CSS
- Real-time chat interface
- Authentication flow with protected routes
- Loading states and error handling
- Beautiful gradient designs

## Environment Variables
- `SESSION_SECRET`: Secret key for JWT token signing (managed by Replit Secrets)
- `GEMINI_API_KEY`: Google Gemini API key (required, managed by Replit Secrets)

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
- 2025-10-17: Initial project setup and updates
  - Created FastAPI backend with JWT authentication
  - Integrated CrewAI multi-agent system with Gemini 2.5 Flash
  - Implemented two specialized AI agents:
    - Research Analyst: Analyzes and researches user queries
    - Content Writer: Creates clear, engaging responses
  - Built React frontend with Tailwind CSS
  - Configured automatic build and deployment
  - Implemented secure environment variable management
  - Added autocomplete attributes for better UX and security
  - Removed login/registration pages for direct access
  - Enhanced AI responses through agent collaboration

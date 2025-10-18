from pydantic import BaseModel, EmailStr
from typing import Optional, List

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class AIRequest(BaseModel):
    prompt: str
    source_language: Optional[str] = 'python'
    num_variations: Optional[int] = 10
    target_languages: Optional[List[str]] = []
    
class AIResponse(BaseModel):
    response: str
    model: str

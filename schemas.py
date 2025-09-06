
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field



class UserCreate(BaseModel):
    login: str
    password_hash: str
    role: str 
    
class UserLogin(BaseModel):
    login: str
    password: str

class UserRead(BaseModel):
    id: int
    login: str
    role: str
    created_at: datetime
    updated_at: datetime | None = None  # может быть None

    class Config:
        from_attributes = True   
    
    
    
class TaskCreate(BaseModel):
    worker: str
    title: str = Field(min_length=5, max_length=50)
    description: str = Field(max_length=500)
    status: str
    

class TaskRead(BaseModel):
    id: int
    worker: str
    title: str
    status: str
     
     
     
    class Config:
        from_attributes = True  
        

class TasksUpdate(BaseModel):
    worker: str
    title: Optional[str] = Field(None, max_length= 50)
    description: Optional[str] = Field(max_length=500)
    status: str
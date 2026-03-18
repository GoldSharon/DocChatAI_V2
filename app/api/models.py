from pydantic import BaseModel,Field
from typing import Optional

class ChatRequest(BaseModel):
    question:str 
    document_id : Optional[str] = None 
    session_id: Optional[str] = None 

class DocumentUploadResponse(BaseModel):
    document_id : str 
    filename : str
    message : str 
    chunk_ciunt : int 


class ChatResponse(BaseModel):
    question : str 
    answer : str 
    source : list[str] = Field(default_factory=list)

class HelathResponse(BaseModel):
    status : str 
    version: str 
    app_name : str 



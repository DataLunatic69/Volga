from app.config import settings
from langchain_groq import ChatGroq
from typing import Optional
import os


class LLMClient:
    """Singleton client for LLM operations."""
    
    _instance: Optional['LLMClient'] = None
    _llm: Optional[ChatGroq] = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one LLM instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__init__()
        return cls._instance
    
    def __init__(self):
        """Initialize the LLM client with settings."""
        self.model = settings.LLM_MODEL
        self.api_key = settings.GROQ_API_KEY
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is not set in environment variables")
        
        if not self.model:
            raise ValueError("LLM_MODEL is not set in environment variables")
        
       
        self._llm = ChatGroq(
            model=self.model,
            api_key=self.api_key,
            temperature=settings.LLM_TEMPERATURE if hasattr(settings, 'LLM_TEMPERATURE') else 0.1,
            max_tokens=settings.LLM_MAX_TOKENS if hasattr(settings, 'LLM_MAX_TOKENS') else 2000
        )
        
    def __call__(self):
        """Make the instance callable to get the LLM."""
        return self._llm
    
    @property
    def llm(self):
        """Property to access the LLM."""
        return self._llm
    
    def invoke(self, prompt: str, **kwargs):
        """Convenience method to invoke the LLM with a prompt."""
        return self._llm.invoke(prompt, **kwargs)
    
    def stream(self, prompt: str, **kwargs):
        """Convenience method to stream LLM responses."""
        return self._llm.stream(prompt, **kwargs)
    
    def get_model_info(self) -> dict:
        """Get information about the current LLM configuration."""
        return {
            "model": self.model,
            "provider": "groq",
            "temperature": getattr(self._llm, 'temperature', 'default'),
            "max_tokens": getattr(self._llm, 'max_tokens', 'default')
        }



 
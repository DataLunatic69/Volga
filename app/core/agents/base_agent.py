"""Base agent class for all specialized agents."""
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """Abstract base class for all AI agents."""
    
    def __init__(self, name: str, description: str):
        """Initialize base agent.
        
        Args:
            name: Agent name.
            description: Agent description.
        """
        self.name = name
        self.description = description
    
    @abstractmethod
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process state and generate response.
        
        Args:
            state: Current workflow state.
            
        Returns:
            Updated state with agent response.
        """
        pass
    
    @abstractmethod
    async def should_handle(self, state: Dict[str, Any]) -> bool:
        """Determine if this agent should handle the request.
        
        Args:
            state: Current workflow state.
            
        Returns:
            True if agent should handle, False otherwise.
        """
        pass

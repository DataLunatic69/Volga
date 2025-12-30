"""
Embedding generation utilities using sentence transformers.
"""
from typing import List, Dict, Any
import logging
from functools import lru_cache

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generate embeddings for text using sentence transformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the embedding model.
        
        Args:
            model_name: Name of the sentence transformer model
        """
        self.model_name = model_name
        self.model = None
        
    def load_model(self):
        """Load the sentence transformer model."""
        if self.model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded successfully")
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as list of floats
        """
        self.load_model()
        
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
        """
        self.load_model()
        
        if not texts:
            return []
        
        # Filter out empty texts
        valid_texts = [t for t in texts if t and t.strip()]
        
        if not valid_texts:
            raise ValueError("All texts are empty")
        
        embeddings = self.model.encode(valid_texts, convert_to_numpy=True, show_progress_bar=True)
        return embeddings.tolist()


def create_property_text(property_data: Dict[str, Any]) -> str:
    """Create searchable text representation of a property.
    
    Args:
        property_data: Property data dictionary
        
    Returns:
        Concatenated text for embedding
    """
    parts = []
    
    # Title and description
    if property_data.get("title"):
        parts.append(property_data["title"])
    
    if property_data.get("description"):
        parts.append(property_data["description"])
    
    # Property type and transaction type
    if property_data.get("property_type"):
        parts.append(f"{property_data['property_type']} property")
    
    if property_data.get("transaction_type"):
        parts.append(f"for {property_data['transaction_type']}")
    
    # Location
    if property_data.get("area_name"):
        parts.append(f"in {property_data['area_name']}")
    
    # Size details
    if property_data.get("bedrooms"):
        parts.append(f"{property_data['bedrooms']} bedroom")
    
    if property_data.get("bathrooms"):
        parts.append(f"{property_data['bathrooms']} bathroom")
    
    # Price
    if property_data.get("price"):
        price_period = property_data.get("price_period", "")
        parts.append(f"£{property_data['price']}/{price_period}")
    
    # Furnishing
    if property_data.get("furnishing"):
        parts.append(property_data["furnishing"])
    
    # Features
    if property_data.get("features"):
        features_text = ", ".join(property_data["features"])
        parts.append(f"Features: {features_text}")
    
    return " ".join(parts)


def create_contact_preference_text(preference_data: Dict[str, Any]) -> str:
    """Create searchable text representation of contact preferences.
    
    Args:
        preference_data: Contact preference data dictionary
        
    Returns:
        Concatenated text for embedding
    """
    parts = []
    
    # Property type and transaction
    if preference_data.get("property_type"):
        parts.append(f"Looking for {preference_data['property_type']}")
    
    if preference_data.get("transaction_type"):
        parts.append(f"to {preference_data['transaction_type']}")
    
    # Budget
    if preference_data.get("budget_min") and preference_data.get("budget_max"):
        parts.append(f"budget £{preference_data['budget_min']} to £{preference_data['budget_max']}")
    
    # Locations
    if preference_data.get("preferred_locations"):
        locations = ", ".join(preference_data["preferred_locations"])
        parts.append(f"in {locations}")
    
    # Bedrooms and bathrooms
    if preference_data.get("bedrooms_min"):
        parts.append(f"{preference_data['bedrooms_min']} bedroom minimum")
    
    if preference_data.get("bathrooms_min"):
        parts.append(f"{preference_data['bathrooms_min']} bathroom minimum")
    
    # Furnishing
    if preference_data.get("furnishing"):
        parts.append(preference_data["furnishing"])
    
    # Must-have features
    if preference_data.get("must_have_features"):
        features = ", ".join(preference_data["must_have_features"])
        parts.append(f"Must have: {features}")
    
    # Urgency
    if preference_data.get("urgency"):
        parts.append(f"Urgency: {preference_data['urgency']}")
    
    # Additional notes
    if preference_data.get("additional_notes"):
        parts.append(preference_data["additional_notes"])
    
    return " ".join(parts)


# Singleton instance
embedding_generator = EmbeddingGenerator()
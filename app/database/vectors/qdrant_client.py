"""
Qdrant vector database client for semantic search.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
import logging

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    SearchRequest,
)
from qdrant_client.http import models

from app.config import settings

logger = logging.getLogger(__name__)


class QdrantManager:
    """Manager for Qdrant vector database operations."""
    
    def __init__(self):
        """Initialize Qdrant client."""
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            timeout=30
        )
        self.properties_collection = "properties_embeddings"
        self.contacts_collection = "contact_preferences_embeddings"
        
    async def create_collections(self):
        """Create Qdrant collections if they don't exist."""
        try:
            # Create properties collection
            if not self.client.collection_exists(self.properties_collection):
                self.client.create_collection(
                    collection_name=self.properties_collection,
                    vectors_config=VectorParams(
                        size=384,  # all-MiniLM-L6-v2 embedding size
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {self.properties_collection}")
            
            # Create contact preferences collection
            if not self.client.collection_exists(self.contacts_collection):
                self.client.create_collection(
                    collection_name=self.contacts_collection,
                    vectors_config=VectorParams(
                        size=384,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {self.contacts_collection}")
                
        except Exception as e:
            logger.error(f"Error creating collections: {e}")
            raise
    
    async def upsert_property(
        self,
        property_id: UUID,
        embedding: List[float],
        payload: Dict[str, Any]
    ):
        """Insert or update a property embedding.
        
        Args:
            property_id: UUID of the property
            embedding: Vector embedding
            payload: Metadata payload
        """
        try:
            self.client.upsert(
                collection_name=self.properties_collection,
                points=[
                    PointStruct(
                        id=str(property_id),
                        vector=embedding,
                        payload=payload
                    )
                ]
            )
            logger.info(f"Upserted property embedding: {property_id}")
        except Exception as e:
            logger.error(f"Error upserting property {property_id}: {e}")
            raise
    
    async def upsert_contact_preference(
        self,
        contact_id: UUID,
        embedding: List[float],
        payload: Dict[str, Any]
    ):
        """Insert or update a contact preference embedding.
        
        Args:
            contact_id: UUID of the contact
            embedding: Vector embedding
            payload: Metadata payload
        """
        try:
            self.client.upsert(
                collection_name=self.contacts_collection,
                points=[
                    PointStruct(
                        id=str(contact_id),
                        vector=embedding,
                        payload=payload
                    )
                ]
            )
            logger.info(f"Upserted contact preference embedding: {contact_id}")
        except Exception as e:
            logger.error(f"Error upserting contact {contact_id}: {e}")
            raise
    
    async def search_properties(
        self,
        query_vector: List[float],
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        agency_id: Optional[UUID] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar properties.
        
        Args:
            query_vector: Query embedding vector
            limit: Number of results to return
            filters: Optional filters for the search
            agency_id: Filter by agency ID
            
        Returns:
            List of search results with scores
        """
        try:
            # Build filter conditions
            filter_conditions = []
            
            if agency_id:
                filter_conditions.append(
                    FieldCondition(
                        key="agency_id",
                        match=MatchValue(value=str(agency_id))
                    )
                )
            
            if filters:
                if "status" in filters:
                    filter_conditions.append(
                        FieldCondition(
                            key="status",
                            match=MatchValue(value=filters["status"])
                        )
                    )
                
                if "property_type" in filters:
                    filter_conditions.append(
                        FieldCondition(
                            key="property_type",
                            match=MatchValue(value=filters["property_type"])
                        )
                    )
            
            # Construct filter
            search_filter = None
            if filter_conditions:
                search_filter = Filter(must=filter_conditions)
            
            # Perform search
            results = self.client.search(
                collection_name=self.properties_collection,
                query_vector=query_vector,
                limit=limit,
                query_filter=search_filter
            )
            
            return [
                {
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload
                }
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error searching properties: {e}")
            raise
    
    async def search_similar_contacts(
        self,
        query_vector: List[float],
        limit: int = 5,
        agency_id: Optional[UUID] = None
    ) -> List[Dict[str, Any]]:
        """Search for contacts with similar preferences.
        
        Args:
            query_vector: Query embedding vector
            limit: Number of results to return
            agency_id: Filter by agency ID
            
        Returns:
            List of similar contacts
        """
        try:
            filter_conditions = []
            
            if agency_id:
                filter_conditions.append(
                    FieldCondition(
                        key="agency_id",
                        match=MatchValue(value=str(agency_id))
                    )
                )
            
            search_filter = None
            if filter_conditions:
                search_filter = Filter(must=filter_conditions)
            
            results = self.client.search(
                collection_name=self.contacts_collection,
                query_vector=query_vector,
                limit=limit,
                query_filter=search_filter
            )
            
            return [
                {
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload
                }
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error searching similar contacts: {e}")
            raise
    
    async def delete_property(self, property_id: UUID):
        """Delete a property embedding.
        
        Args:
            property_id: UUID of the property to delete
        """
        try:
            self.client.delete(
                collection_name=self.properties_collection,
                points_selector=models.PointIdsList(
                    points=[str(property_id)]
                )
            )
            logger.info(f"Deleted property embedding: {property_id}")
        except Exception as e:
            logger.error(f"Error deleting property {property_id}: {e}")
            raise
    
    async def delete_contact_preference(self, contact_id: UUID):
        """Delete a contact preference embedding.
        
        Args:
            contact_id: UUID of the contact to delete
        """
        try:
            self.client.delete(
                collection_name=self.contacts_collection,
                points_selector=models.PointIdsList(
                    points=[str(contact_id)]
                )
            )
            logger.info(f"Deleted contact preference embedding: {contact_id}")
        except Exception as e:
            logger.error(f"Error deleting contact {contact_id}: {e}")
            raise
    
    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get information about a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Collection information
        """
        try:
            info = self.client.get_collection(collection_name)
            return {
                "name": collection_name,
                "points_count": info.points_count,
                "vectors_count": info.points_count,  # In Qdrant, each point has one vector
                "status": info.status
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            raise


# Singleton instance
qdrant_manager = QdrantManager()
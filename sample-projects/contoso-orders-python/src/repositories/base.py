"""
Base Repository Pattern

Provides common interface for all repositories.

Team Convention: All repository methods return Optional[T] for single-item lookups.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """
    Abstract base repository defining the standard data access interface.
    
    All concrete repositories must implement these methods.
    
    Architecture Note: We use the Repository pattern to isolate data access
    logic from business logic. This allows us to:
    - Swap data stores without changing service code
    - Easily mock data access in tests
    - Apply consistent error handling
    """
    
    @abstractmethod
    def find_by_id(self, entity_id: str) -> Optional[T]:
        """
        Find an entity by its unique identifier.
        
        Returns None if not found (never raises for missing entities).
        """
        pass
    
    @abstractmethod
    def find_all(
        self, 
        offset: int = 0, 
        limit: int = 100,
        **filters
    ) -> List[T]:
        """
        Find all entities matching optional filters.
        
        Supports pagination via offset/limit.
        """
        pass
    
    @abstractmethod
    def save(self, entity: T) -> T:
        """
        Save an entity (create or update).
        
        Returns the saved entity with any generated fields populated.
        """
        pass
    
    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """
        Delete an entity by ID.
        
        Returns True if entity was deleted, False if not found.
        """
        pass
    
    @abstractmethod
    def count(self, **filters) -> int:
        """Count entities matching optional filters."""
        pass
    
    def exists(self, entity_id: str) -> bool:
        """Check if an entity exists."""
        return self.find_by_id(entity_id) is not None

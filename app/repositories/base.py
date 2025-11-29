from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Type, List, Optional, Tuple
from sqlalchemy.orm import Session

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class IRepository(ABC, Generic[ModelType]):

    
    @abstractmethod
    def get(self, db: Session, id: str) -> Optional[ModelType]:
        """Get a single record by ID"""
        pass
    
    @abstractmethod
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all records with pagination"""
        pass
    
    @abstractmethod
    def create(self, db: Session, obj_in: dict) -> ModelType:
        """Create a new record"""
        pass
    
    @abstractmethod
    def update(self, db: Session, id: str, obj_in: dict) -> Optional[ModelType]:
        """Update an existing record"""
        pass
    
    @abstractmethod
    def delete(self, db: Session, id: str) -> bool:
        """Delete a record by ID"""
        pass


class CRUDBase(IRepository[ModelType]):
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    def get(self, db: Session, id: str) -> Optional[ModelType]:
        """Get a single record by ID"""
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all records with pagination"""
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def get_with_count(self, db: Session, skip: int = 0, limit: int = 100) -> Tuple[List[ModelType], int]:
        """Get all records with pagination and total count"""
        query = db.query(self.model)
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total
    
    def create(self, db: Session, obj_in: dict) -> ModelType:
        """Create a new record"""
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, id: str, obj_in: dict) -> Optional[ModelType]:
        """Update an existing record"""
        db_obj = self.get(db, id)
        if db_obj is None:
            return None
        
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: str) -> bool:
        """Delete a record by ID"""
        obj = db.query(self.model).filter(self.model.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False
    
    def exists(self, db: Session, id: str) -> bool:
        """Check if a record exists"""
        return db.query(self.model).filter(self.model.id == id).first() is not None

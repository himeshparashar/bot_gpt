"""
Common Schemas - Generic Response DTOs
"""
from pydantic import BaseModel
from typing import Optional


class StatusResponse(BaseModel):
    """Generic status response"""
    success: bool
    message: str


class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    version: Optional[str] = None

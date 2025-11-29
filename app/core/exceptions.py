"""
Custom Exception Classes
"""
from fastapi import HTTPException, status


class ChatException(HTTPException):
    """Exception raised for chat-related errors"""
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class LLMException(HTTPException):
    """Exception raised for LLM provider errors"""
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)


class DocumentException(HTTPException):
    """Exception raised for document processing errors"""
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)

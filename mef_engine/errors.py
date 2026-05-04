from enum import Enum
from typing import Any, Optional, Dict
from pydantic import BaseModel

class ErrorCode(str, Enum):
    INVALID_INPUT = "entrada inválida"
    UNSTABLE_MODEL = "modelo instável"
    NUMERICAL_FAILURE = "falha numérica"
    OUT_OF_SCOPE = "fora de escopo"
    INTERNAL_ERROR = "erro interno"

class ErrorResponse(BaseModel):
    code: str
    type: ErrorCode
    message: str
    detail: Optional[str] = None
    module: Optional[str] = None

class StandardErrorResponse(BaseModel):
    error: ErrorResponse

class StructuralError(Exception):
    def __init__(
        self, 
        code: str,
        error_type: ErrorCode, 
        message: str, 
        detail: Optional[str] = None,
        module: Optional[str] = None
    ):
        self.code = code
        self.error_type = error_type
        self.message = message
        self.detail = detail
        self.module = module
        super().__init__(self.message)

# Specific exceptions
class InvalidInputError(StructuralError):
    def __init__(self, message: str, detail: Optional[str] = None, module: Optional[str] = None):
        super().__init__("VAL-001", ErrorCode.INVALID_INPUT, message, detail, module)

class UnstableModelError(StructuralError):
    def __init__(self, message: str, detail: Optional[str] = None, module: Optional[str] = None):
        super().__init__("STB-001", ErrorCode.UNSTABLE_MODEL, message, detail, module)

class NumericalFailureError(StructuralError):
    def __init__(self, message: str, detail: Optional[str] = None, module: Optional[str] = None):
        super().__init__("NUM-001", ErrorCode.NUMERICAL_FAILURE, message, detail, module)

class OutOfScopeError(StructuralError):
    def __init__(self, message: str, detail: Optional[str] = None, module: Optional[str] = None):
        super().__init__("SCP-001", ErrorCode.OUT_OF_SCOPE, message, detail, module)

class InternalStructuralError(StructuralError):
    def __init__(self, message: str, detail: Optional[str] = None, module: Optional[str] = None):
        super().__init__("INT-001", ErrorCode.INTERNAL_ERROR, message, detail, module)

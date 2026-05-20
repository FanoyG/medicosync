class AppException(Exception):
    def __init__(self, detail: str, status_code: int):
        self.detail = detail
        self.status_code = status_code

class NotFoundException(AppException):
    def __init__(self, detail: str = "Not found"):
        super().__init__(detail, status_code=404)  

class UnauthorizedException(AppException):
    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(detail, status_code=401)  

class ForbiddenException(AppException):
    def __init__(self, detail: str = "Access denied"):
        super().__init__(detail, status_code=403)  

class ConflictException(AppException):
    def __init__(self, detail: str = "Already exists"):
        super().__init__(detail, status_code=409)  

class RequestConflictException(AppException):
    def __init__(self, detail: str = "Too many Request"):
        super().__init__(detail, status_code=429)
    
class BadRequestException(AppException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(detail, status_code=400)


class DuplicateEmailException(AppException):
    """Raised when a user tries to register with an email that already exists in the system."""

    def __init__(self, email: str):
        self.email = email
        self.message = (
            f"The account registration failed. '{email}' is already registered."
        )
        super().__init__(self.message, status_code=409)

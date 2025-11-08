"""Custom exceptions for Pesapal SDK."""


class PesapalError(Exception):
    """Base exception for all Pesapal SDK errors."""
    pass


class PesapalAPIError(PesapalError):
    """Exception raised when Pesapal API returns an error."""
    
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class PesapalAuthenticationError(PesapalAPIError):
    """Exception raised when authentication fails."""
    pass


class PesapalValidationError(PesapalError):
    """Exception raised when request validation fails."""
    pass


class PesapalNetworkError(PesapalError):
    """Exception raised when network request fails."""
    pass


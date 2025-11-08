"""Pesapal API client."""

import httpx
from typing import Optional
from decimal import Decimal

from pesapal.models import PaymentRequest, PaymentResponse, PaymentStatus
from pesapal.constants import (
    PESAPAL_SANDBOX_BASE_URL,
    PESAPAL_PRODUCTION_BASE_URL,
    ENDPOINT_SUBMIT_ORDER,
    ENDPOINT_GET_STATUS,
)
from pesapal.exceptions import (
    PesapalAPIError,
    PesapalAuthenticationError,
    PesapalNetworkError,
    PesapalValidationError,
)
from pesapal.utils import generate_signature


class PesapalClient:
    """Client for interacting with Pesapal Payment API."""
    
    def __init__(
        self,
        consumer_key: str,
        consumer_secret: str,
        sandbox: bool = True,
        timeout: int = 30
    ):
        """
        Initialize Pesapal client.
        
        Args:
            consumer_key: Pesapal consumer key
            consumer_secret: Pesapal consumer secret
            sandbox: Use sandbox environment (default: True)
            timeout: Request timeout in seconds (default: 30)
        """
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.sandbox = sandbox
        self.base_url = PESAPAL_SANDBOX_BASE_URL if sandbox else PESAPAL_PRODUCTION_BASE_URL
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def close(self):
        """Close HTTP client."""
        await self._client.aclose()
    
    def _get_headers(self) -> dict:
        """Get default headers for API requests."""
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None,
        params: Optional[dict] = None
    ) -> dict:
        """
        Make HTTP request to Pesapal API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            
        Returns:
            Response JSON data
            
        Raises:
            PesapalAPIError: If API returns an error
            PesapalNetworkError: If network request fails
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        try:
            response = await self._client.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params
            )
            
            # Handle authentication errors
            if response.status_code == 401:
                raise PesapalAuthenticationError(
                    "Authentication failed. Check your consumer key and secret.",
                    status_code=401
                )
            
            # Handle other errors
            if response.status_code >= 400:
                error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                raise PesapalAPIError(
                    f"API error: {response.status_code}",
                    status_code=response.status_code,
                    response_data=error_data
                )
            
            return response.json()
            
        except httpx.RequestError as e:
            raise PesapalNetworkError(f"Network error: {str(e)}")
        except PesapalAPIError:
            raise
        except Exception as e:
            raise PesapalAPIError(f"Unexpected error: {str(e)}")
    
    async def submit_order(self, payment_request: PaymentRequest) -> PaymentResponse:
        """
        Submit a payment order to Pesapal.
        
        Args:
            payment_request: Payment request details
            
        Returns:
            PaymentResponse with redirect URL
            
        Raises:
            PesapalValidationError: If request validation fails
            PesapalAPIError: If API returns an error
        """
        # Validate request
        try:
            payment_request.model_validate(payment_request.model_dump())
        except Exception as e:
            raise PesapalValidationError(f"Invalid payment request: {str(e)}")
        
        # Prepare request data
        request_data = payment_request.model_dump(exclude_none=True)
        request_data["amount"] = str(request_data["amount"])  # Convert Decimal to string
        
        # Add authentication
        request_data["consumer_key"] = self.consumer_key
        request_data["consumer_secret"] = self.consumer_secret
        
        # Generate signature
        signature = generate_signature(request_data, self.consumer_secret)
        request_data["signature"] = signature
        
        # Make API request
        response_data = await self._request("POST", ENDPOINT_SUBMIT_ORDER, data=request_data)
        
        # Parse response
        return PaymentResponse(**response_data)
    
    async def get_payment_status(
        self,
        order_tracking_id: str,
        merchant_reference: Optional[str] = None
    ) -> PaymentStatus:
        """
        Get payment status from Pesapal.
        
        Args:
            order_tracking_id: Pesapal order tracking ID
            merchant_reference: Optional merchant reference for validation
            
        Returns:
            PaymentStatus with current payment status
            
        Raises:
            PesapalAPIError: If API returns an error
        """
        # Prepare request data
        request_data = {
            "order_tracking_id": order_tracking_id,
            "consumer_key": self.consumer_key,
            "consumer_secret": self.consumer_secret,
        }
        
        if merchant_reference:
            request_data["merchant_reference"] = merchant_reference
        
        # Generate signature
        signature = generate_signature(request_data, self.consumer_secret)
        request_data["signature"] = signature
        
        # Make API request
        response_data = await self._request("GET", ENDPOINT_GET_STATUS, params=request_data)
        
        # Parse response
        return PaymentStatus(**response_data)
    
    async def initiate_payment(
        self,
        order_id: str,
        amount: Decimal,
        currency: str,
        description: str,
        callback_url: str,
        customer: Optional[dict] = None,
        billing_address: Optional[dict] = None
    ) -> PaymentResponse:
        """
        Convenience method to initiate a payment.
        
        Args:
            order_id: Unique order ID
            amount: Payment amount
            currency: Currency code (KES, TZS, etc.)
            description: Order description
            callback_url: Callback URL for payment status
            customer: Optional customer information
            billing_address: Optional billing address
            
        Returns:
            PaymentResponse with redirect URL
        """
        payment_request = PaymentRequest(
            id=order_id,
            amount=amount,
            currency=currency,
            description=description,
            callback_url=callback_url,
            customer=customer,
            billing_address=billing_address
        )
        
        return await self.submit_order(payment_request)


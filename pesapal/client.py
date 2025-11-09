"""Pesapal API client."""

import logging
import httpx
from typing import Optional
from decimal import Decimal

from pesapal.models import PaymentRequest, PaymentResponse, PaymentStatus
from pesapal.constants import (
    PESAPAL_SANDBOX_BASE_URL,
    PESAPAL_PRODUCTION_BASE_URL,
    ENDPOINT_AUTH_TOKEN,
    ENDPOINT_SUBMIT_ORDER,
    ENDPOINT_GET_STATUS,
)
from pesapal.exceptions import (
    PesapalAPIError,
    PesapalAuthenticationError,
    PesapalNetworkError,
    PesapalValidationError,
)

logger = logging.getLogger(__name__)


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
        self._access_token: Optional[str] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def close(self):
        """Close HTTP client."""
        await self._client.aclose()
    
    async def _get_access_token(self) -> str:
        """
        Get OAuth access token from Pesapal API 3.0.
        
        Returns:
            Access token string
            
        Raises:
            PesapalAuthenticationError: If token request fails
        """
        if self._access_token:
            return self._access_token
        
        try:
            auth_data = {
                "consumer_key": self.consumer_key,
                "consumer_secret": self.consumer_secret
            }
            
            response = await self._client.post(
                f"{self.base_url}{ENDPOINT_AUTH_TOKEN}",
                json=auth_data,
                headers={"Content-Type": "application/json", "Accept": "application/json"}
            )
            
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", {}).get("message", response.text)
                except:
                    error_msg = response.text
                
                raise PesapalAuthenticationError(
                    f"Failed to get access token: {response.status_code} - {error_msg}",
                    status_code=response.status_code
                )
            
            token_data = response.json()
            self._access_token = token_data.get("token")
            
            if not self._access_token:
                raise PesapalAuthenticationError(
                    f"No access token in response: {token_data}",
                    status_code=response.status_code
                )
            
            logger.info("OAuth token obtained successfully")
            return self._access_token
            
        except httpx.RequestError as e:
            raise PesapalAuthenticationError(f"Network error getting token: {str(e)}")
        except PesapalAuthenticationError:
            raise
        except Exception as e:
            raise PesapalAuthenticationError(f"Unexpected error getting token: {str(e)}")
    
    def _get_headers(self, include_auth: bool = False) -> dict:
        """
        Get default headers for API requests.
        
        Args:
            include_auth: Whether to include Authorization header (requires token)
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        if include_auth and self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"
        
        return headers
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None,
        params: Optional[dict] = None,
        custom_headers: Optional[dict] = None
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
        headers = custom_headers or self._get_headers()
        
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
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", error_data.get("message", "Authentication failed"))
                except:
                    error_msg = response.text or "Authentication failed. Check your consumer key and secret."
                
                logger.error(
                    f"Authentication failed: {error_msg}",
                    extra={"status_code": response.status_code, "url": url}
                )
                
                raise PesapalAuthenticationError(
                    f"Authentication failed: {error_msg}. Check your consumer key and secret.",
                    status_code=401
                )
            
            # Handle other errors
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                except:
                    error_data = {"error": response.text}
                
                error_message = error_data.get("error", error_data.get("message", f"API error: {response.status_code}"))
                raise PesapalAPIError(
                    error_message,
                    status_code=response.status_code,
                    response_data=error_data
                )
            
            response_data = response.json()
            logger.debug(f"Pesapal API response: {response.status_code} - {endpoint}")
            return response_data
            
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
        
        # Get OAuth access token (required for Pesapal API 3.0)
        token = await self._get_access_token()
        
        # Prepare request data according to Pesapal API 3.0 format
        # NOTE: Do NOT include consumer_key, consumer_secret, or signature in request body
        # Authentication is done via Bearer token in Authorization header
        request_data = {
            "id": payment_request.id,
            "currency": payment_request.currency,
            "amount": float(payment_request.amount),  # Pesapal expects number, not string
            "description": payment_request.description,
            "callback_url": payment_request.callback_url,
        }
        
        # Add required/optional fields
        # notification_id is required for Pesapal API 3.0
        if payment_request.notification_id:
            request_data["notification_id"] = payment_request.notification_id
        else:
            logger.warning("notification_id not provided in payment request")
        
        # Add optional redirect_mode (TOP_WINDOW or PARENT_WINDOW, default: TOP_WINDOW)
        if payment_request.redirect_mode:
            request_data["redirect_mode"] = payment_request.redirect_mode
        else:
            # Default to TOP_WINDOW as per Pesapal docs
            request_data["redirect_mode"] = "TOP_WINDOW"
        
        # Add optional cancellation_url
        if payment_request.cancellation_url:
            request_data["cancellation_url"] = payment_request.cancellation_url
        
        # Add optional branch
        if payment_request.branch:
            request_data["branch"] = payment_request.branch
        
        # billing_address is required by Pesapal (but we allow optional for flexibility)
        if payment_request.billing_address:
            request_data["billing_address"] = payment_request.billing_address
        else:
            logger.warning("billing_address not provided - Pesapal may require this")
        
        logger.info(
            f"Submitting payment order: {payment_request.id} - "
            f"{request_data['amount']} {request_data['currency']}"
        )
        
        # Use Bearer token authentication
        headers = self._get_headers(include_auth=True)
        
        # Make API request
        response_data = await self._request("POST", ENDPOINT_SUBMIT_ORDER, data=request_data, custom_headers=headers)
        
        # Handle different response formats from Pesapal API v3
        # Pesapal might return different field names, so we need to map them
        mapped_response = {}
        
        # Map field names (Pesapal API 3.0 response uses snake_case)
        # Response format: { "order_tracking_id": "...", "redirect_url": "...", "status": "200", "message": "..." }
        field_mapping = {
            "order_tracking_id": ["order_tracking_id", "orderTrackingId", "OrderTrackingId", "tracking_id"],
            "merchant_reference": ["merchant_reference", "merchantReference", "MerchantReference", "reference"],
            "redirect_url": ["redirect_url", "redirectUrl", "RedirectUrl", "payment_url", "paymentUrl"],
            "status": ["status", "Status", "payment_status_code"],
            "message": ["message", "Message", "error_message", "errorMessage"]
        }
        
        for our_field, possible_fields in field_mapping.items():
            for field in possible_fields:
                if field in response_data:
                    mapped_response[our_field] = response_data[field]
                    break
        
        # If no mapping found, try direct assignment
        if not mapped_response:
            mapped_response = response_data
        
        # Validate response has required fields
        if not mapped_response.get("order_tracking_id") and not mapped_response.get("redirect_url"):
            # Check if it's an error response
            error_msg = mapped_response.get("message") or mapped_response.get("error") or mapped_response.get("errorMessage")
            if error_msg:
                raise PesapalAPIError(
                    f"Pesapal API error: {error_msg}",
                    status_code=400,
                    response_data=response_data
                )
            
            logger.error(
                f"Invalid Pesapal response: Missing order_tracking_id and redirect_url",
                extra={"response_keys": list(response_data.keys())}
            )
            
            raise PesapalAPIError(
                f"Invalid response from Pesapal API: Missing order_tracking_id and redirect_url. "
                f"Response: {response_data}",
                response_data=response_data
            )
        
        # Parse response (make fields optional to handle missing data)
        try:
            return PaymentResponse(**mapped_response)
        except Exception as e:
            logger.error(
                f"Failed to parse Pesapal response: {e}",
                extra={"response_data": response_data}
            )
            raise PesapalAPIError(
                f"Unexpected response format from Pesapal API: {response_data}",
                response_data=response_data
            )
    
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
        # Get OAuth access token
        token = await self._get_access_token()
        
        # Prepare query parameters (Pesapal API 3.0 uses query params for GET requests)
        params = {
            "orderTrackingId": order_tracking_id  # Note: camelCase in query parameter
        }
        
        if merchant_reference:
            params["merchantReference"] = merchant_reference
        
        # Use Bearer token authentication
        headers = self._get_headers(include_auth=True)
        
        # Make API request
        response_data = await self._request("GET", ENDPOINT_GET_STATUS, params=params, custom_headers=headers)
        
        # Log raw response for debugging
        logger.info(f"Raw Pesapal status response keys: {list(response_data.keys())}")
        logger.debug(f"Raw Pesapal status response: {response_data}")
        
        # Map field names (Pesapal may return camelCase or snake_case)
        # Handle payment_method field variations
        field_mapping = {
            "payment_method": ["payment_method", "paymentMethod", "PaymentMethod", "payment_method_used", "PaymentMethodUsed"],
            "payment_status_description": ["payment_status_description", "paymentStatusDescription", "PaymentStatusDescription", "status_description"],
            "confirmation_code": ["confirmation_code", "confirmationCode", "ConfirmationCode", "transaction_code"],
            "status_code": ["status_code", "statusCode", "StatusCode", "payment_status_code"],
            "order_tracking_id": ["order_tracking_id", "orderTrackingId", "OrderTrackingId"],
            "merchant_reference": ["merchant_reference", "merchantReference", "MerchantReference"],
        }
        
        mapped_response = {}
        for our_field, possible_fields in field_mapping.items():
            for field in possible_fields:
                if field in response_data:
                    mapped_response[our_field] = response_data[field]
                    logger.debug(f"Mapped {field} -> {our_field}: {response_data[field]}")
                    break
        
        # Copy all other fields as-is
        for key, value in response_data.items():
            if key not in mapped_response:
                mapped_response[key] = value
        
        # Log payment_method extraction
        if "payment_method" in mapped_response:
            logger.info(f"Payment method extracted: {mapped_response['payment_method']}")
        else:
            logger.warning(f"Payment method not found in response. Available fields: {list(response_data.keys())}")
        
        # Parse response
        return PaymentStatus(**mapped_response)
    
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


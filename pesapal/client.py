"""Pesapal API client."""

import logging
import httpx
from typing import Optional
from decimal import Decimal
from datetime import datetime, timedelta

from pesapal.models import PaymentRequest, PaymentResponse, PaymentStatus, IPNRegistration
from pesapal.constants import (
    PESAPAL_SANDBOX_BASE_URL,
    PESAPAL_PRODUCTION_BASE_URL,
    ENDPOINT_AUTH_TOKEN,
    ENDPOINT_SUBMIT_ORDER,
    ENDPOINT_GET_STATUS,
    ENDPOINT_IPN_REGISTER,
    ENDPOINT_IPN_LIST,
    ENDPOINT_REFUND,
    ENDPOINT_CANCEL_ORDER,
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
        self._token_expires_at: Optional[datetime] = None  # Track token expiration (5 minutes lifetime)
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def close(self):
        """Close HTTP client."""
        await self._client.aclose()
    
    async def _get_access_token(self, force_refresh: bool = False) -> str:
        """
        Get OAuth access token from Pesapal API 3.0.
        
        Token lifetime is 5 minutes. This method handles automatic renewal.
        
        Args:
            force_refresh: Force token refresh even if token exists
            
        Returns:
            Access token string
            
        Raises:
            PesapalAuthenticationError: If token request fails
        """
        # Check if token exists and is still valid (with 30 second buffer)
        if not force_refresh and self._access_token and self._token_expires_at:
            if datetime.utcnow() < (self._token_expires_at - timedelta(seconds=30)):
                return self._access_token
            # Token expired or about to expire, clear it
            logger.info("Access token expired or about to expire, refreshing...")
            self._access_token = None
            self._token_expires_at = None
        
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
            
            # Set token expiration (5 minutes from now as per Pesapal docs)
            self._token_expires_at = datetime.utcnow() + timedelta(minutes=5)
            
            logger.info("OAuth token obtained successfully (expires in 5 minutes)")
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
        custom_headers: Optional[dict] = None,
        include_auth: bool = False
    ) -> dict:
        """
        Make HTTP request to Pesapal API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            custom_headers: Custom headers (if provided, include_auth is ignored)
            include_auth: Whether to include Authorization header (requires token)
            
        Returns:
            Response JSON data
            
        Raises:
            PesapalAPIError: If API returns an error
            PesapalNetworkError: If network request fails
        """
        url = f"{self.base_url}{endpoint}"
        headers = custom_headers or self._get_headers(include_auth=include_auth)
        
        try:
            response = await self._client.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params
            )
            
            # Handle authentication errors (401) - token may have expired
            if response.status_code == 401:
                # Clear expired token
                self._access_token = None
                self._token_expires_at = None
                
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", error_data.get("message", "Authentication failed"))
                except:
                    error_msg = response.text or "Authentication failed. Check your consumer key and secret."
                
                logger.warning(
                    f"Authentication failed (401): {error_msg}. Token may have expired.",
                    extra={"status_code": response.status_code, "url": url}
                )
                
                # If this was an authenticated request, try refreshing token once
                if include_auth and not custom_headers:
                    logger.info("Attempting to refresh token and retry request...")
                    # Get fresh token
                    await self._get_access_token(force_refresh=True)
                    # Retry request with new token
                    headers = self._get_headers(include_auth=True)
                    response = await self._client.request(
                        method=method,
                        url=url,
                        headers=headers,
                        json=data,
                        params=params
                    )
                    # Continue with normal error handling below
                else:
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
        
        # Make API request with authentication (token will be auto-refreshed if expired)
        response_data = await self._request("POST", ENDPOINT_SUBMIT_ORDER, data=request_data, include_auth=True)
        
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
        # Get OAuth access token (will be auto-refreshed if expired)
        token = await self._get_access_token()
        
        # Prepare query parameters (Pesapal API 3.0 uses query params for GET requests)
        params = {
            "orderTrackingId": order_tracking_id  # Note: camelCase in query parameter
        }
        
        if merchant_reference:
            params["merchantReference"] = merchant_reference
        
        # Make API request with authentication
        response_data = await self._request("GET", ENDPOINT_GET_STATUS, params=params, include_auth=True)
        
        # Log raw response for debugging
        logger.info(f"Raw Pesapal status response keys: {list(response_data.keys())}")
        logger.debug(f"Raw Pesapal status response: {response_data}")
        
        # Map field names (Pesapal may return camelCase or snake_case)
        # Handle all field variations according to Pesapal documentation
        field_mapping = {
            "payment_method": ["payment_method", "paymentMethod", "PaymentMethod"],
            "payment_status_description": ["payment_status_description", "paymentStatusDescription", "PaymentStatusDescription"],
            "confirmation_code": ["confirmation_code", "confirmationCode", "ConfirmationCode"],
            "status_code": ["status_code", "statusCode", "StatusCode"],  # Integer: 0=INVALID, 1=COMPLETED, 2=FAILED, 3=REVERSED
            "order_tracking_id": ["order_tracking_id", "orderTrackingId", "OrderTrackingId"],
            "merchant_reference": ["merchant_reference", "merchantReference", "MerchantReference"],
            "payment_account": ["payment_account", "paymentAccount", "PaymentAccount"],
            "call_back_url": ["call_back_url", "callBackUrl", "CallBackUrl", "callback_url"],
            "created_date": ["created_date", "createdDate", "CreatedDate"],
            "error": ["error", "Error"],  # Error object
            "status": ["status", "Status"],  # HTTP status
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
    
    async def register_ipn(self, ipn_url: str, ipn_notification_type: str = "GET") -> IPNRegistration:
        """
        Register an IPN (Instant Payment Notification) URL with Pesapal.
        
        According to Pesapal docs, this endpoint registers your IPN URL and returns
        a notification_id that you use when submitting orders.
        
        Args:
            ipn_url: Your IPN callback URL (must be publicly accessible via HTTPS)
            ipn_notification_type: Notification type - "GET" or "POST" (default: "GET")
            
        Returns:
            IPNRegistration with notification_id
            
        Raises:
            PesapalAPIError: If registration fails
        """
        # Get OAuth access token
        token = await self._get_access_token()
        
        # Prepare request data
        request_data = {
            "url": ipn_url,
            "ipn_notification_type": ipn_notification_type.upper()
        }
        
        logger.info(f"Registering IPN URL: {ipn_url} (type: {ipn_notification_type})")
        
        # Make API request with authentication
        response_data = await self._request("POST", ENDPOINT_IPN_REGISTER, data=request_data, include_auth=True)
        
        # Parse response - Pesapal returns notification_id
        # Response format may vary, handle different field names
        notification_id = (
            response_data.get("notification_id") or
            response_data.get("notificationId") or
            response_data.get("NotificationId") or
            response_data.get("ipn_id") or
            response_data.get("ipnId")
        )
        
        if not notification_id:
            raise PesapalAPIError(
                f"Invalid IPN registration response: Missing notification_id. Response: {response_data}",
                response_data=response_data
            )
        
        logger.info(f"IPN registered successfully: notification_id={notification_id}")
        
        return IPNRegistration(
            notification_id=notification_id,
            ipn_notification_type=ipn_notification_type.upper(),
            ipn_url=ipn_url
        )
    
    async def get_registered_ipns(self) -> list[IPNRegistration]:
        """
        Get list of registered IPN URLs.
        
        According to Pesapal docs, this endpoint returns all registered IPN URLs
        for your merchant account.
        
        Returns:
            List of IPNRegistration objects
            
        Raises:
            PesapalAPIError: If request fails
        """
        # Get OAuth access token
        token = await self._get_access_token()
        
        logger.info("Fetching registered IPN URLs...")
        
        # Make API request with authentication
        response_data = await self._request("GET", ENDPOINT_IPN_LIST, include_auth=True)
        
        # Parse response - Pesapal may return array or object with array
        ipn_list = []
        
        # Handle different response formats
        if isinstance(response_data, list):
            ipn_data_list = response_data
        elif isinstance(response_data, dict):
            # Try common field names
            ipn_data_list = (
                response_data.get("ipns") or
                response_data.get("ipn_list") or
                response_data.get("notifications") or
                response_data.get("data") or
                [response_data]  # Single IPN in object
            )
        else:
            raise PesapalAPIError(
                f"Unexpected IPN list response format: {type(response_data)}",
                response_data=response_data
            )
        
        # Parse each IPN registration
        for ipn_data in ipn_data_list:
            if isinstance(ipn_data, dict):
                notification_id = (
                    ipn_data.get("notification_id") or
                    ipn_data.get("notificationId") or
                    ipn_data.get("NotificationId") or
                    ipn_data.get("ipn_id")
                )
                ipn_url = (
                    ipn_data.get("url") or
                    ipn_data.get("ipn_url") or
                    ipn_data.get("ipnUrl") or
                    ipn_data.get("notification_url")
                )
                ipn_type = (
                    ipn_data.get("ipn_notification_type") or
                    ipn_data.get("ipnNotificationType") or
                    ipn_data.get("notification_type") or
                    "GET"
                )
                
                if notification_id and ipn_url:
                    ipn_list.append(IPNRegistration(
                        notification_id=notification_id,
                        ipn_notification_type=ipn_type.upper(),
                        ipn_url=ipn_url
                    ))
        
        logger.info(f"Found {len(ipn_list)} registered IPN(s)")
        return ipn_list
    
    async def refund_order(
        self,
        confirmation_code: str,
        amount: Decimal,
        username: str,
        remarks: str,
        order_tracking_id: Optional[str] = None
    ) -> dict:
        """
        Request a refund for an order.
        
        According to Pesapal API 3.0 documentation, refund requires:
        - confirmation_code: The payment confirmation code returned by the processor (REQUIRED)
        - amount: The amount to be refunded (REQUIRED)
        - username: The identity of the user initiating the refund (REQUIRED)
        - remarks: A brief description of the reason for the refund (REQUIRED)
        
        Args:
            confirmation_code: Payment confirmation code from Pesapal
            amount: Refund amount (must match payment amount for full refund)
            username: Identity of user initiating refund
            remarks: Reason/description for the refund
            order_tracking_id: Optional order tracking ID (for logging/reference)
            
        Returns:
            Refund response data
            
        Raises:
            PesapalAPIError: If refund request fails
            PesapalValidationError: If required parameters are missing
        """
        # Validate required parameters
        if not confirmation_code:
            raise PesapalValidationError("confirmation_code is required for refund")
        if not amount or amount <= 0:
            raise PesapalValidationError("amount must be greater than 0")
        if not username:
            raise PesapalValidationError("username is required for refund")
        if not remarks:
            raise PesapalValidationError("remarks is required for refund")
        
        # Get OAuth access token
        token = await self._get_access_token()
        
        # Prepare request data according to Pesapal API 3.0 spec
        # CRITICAL: Pesapal requires amount as string with EXACTLY 2 decimal places (e.g., "100.00")
        # The amount must match the original transaction amount exactly
        # Format: Convert Decimal to string with exactly 2 decimal places
        amount_str = f"{float(amount):.2f}"
        
        request_data = {
            "confirmation_code": confirmation_code,
            "amount": amount_str,  # String with exactly 2 decimal places (e.g., "2000.00")
            "username": username,
            "remarks": remarks
        }
        
        logger.info(f"Requesting refund: confirmation_code={confirmation_code}, amount={amount_str}, username={username}")
        logger.debug(f"Refund request payload: {request_data}")
        logger.debug(f"Amount formatting: Decimal({amount}) -> '{amount_str}'")
        
        # Make API request with authentication
        response_data = await self._request("POST", ENDPOINT_REFUND, data=request_data, include_auth=True)
        
        logger.info(f"Refund request submitted: {response_data}")
        return response_data
    
    async def cancel_order(self, order_tracking_id: str) -> dict:
        """
        Cancel an order.
        
        Args:
            order_tracking_id: Pesapal order tracking ID
            
        Returns:
            Cancellation response data
            
        Raises:
            PesapalAPIError: If cancellation fails
        """
        # Get OAuth access token
        token = await self._get_access_token()
        
        # Prepare request data
        request_data = {
            "order_tracking_id": order_tracking_id
        }
        
        logger.info(f"Cancelling order: {order_tracking_id}")
        
        # Make API request with authentication
        response_data = await self._request("POST", ENDPOINT_CANCEL_ORDER, data=request_data, include_auth=True)
        
        logger.info(f"Order cancellation submitted: {response_data}")
        return response_data


# Pesapal Python SDK

Python SDK for Pesapal Payment Gateway API 3.0 - Clean, async interface for payment processing.

## Installation

```bash
pip install pesapal-python-sdk
```

## Quick Start

### Prerequisites

1. **Pesapal Account**: Sign up at [developer.pesapal.com](https://developer.pesapal.com)
2. **Credentials**: Get your `consumer_key` and `consumer_secret`
3. **Callback URL**: A publicly accessible HTTPS endpoint for payment notifications

### Basic Example

```python
import asyncio
from pesapal import PesapalClient, PaymentRequest
from decimal import Decimal

async def main():
    # Initialize client
    client = PesapalClient(
        consumer_key="your_consumer_key",
        consumer_secret="your_consumer_secret",
        sandbox=True  # Set to False for production
    )
    
    # Step 1: Register IPN (Instant Payment Notification)
    ipn_response = await client.register_ipn(
        ipn_url="https://your-domain.com/callback",
        ipn_notification_type="GET"
    )
    ipn_id = ipn_response.notification_id
    
    # Step 2: Create payment request
    payment = PaymentRequest(
        id="ORDER-123",
        amount=Decimal("50000.00"),
        currency="TZS",
        description="Payment for order #123",
        callback_url="https://your-domain.com/callback",
        notification_id=ipn_id,  # Use the registered IPN ID
        billing_address={
            "email_address": "customer@example.com",
            "phone_number": "+255123456789",
            "country_code": "TZ",
            "first_name": "John",
            "last_name": "Doe",
            "line_1": "123 Main Street",
            "city": "Dar es Salaam",
            "postal_code": "11101"
        }
    )
    
    # Step 3: Submit payment
    response = await client.submit_order(payment)
    print(f"Redirect URL: {response.redirect_url}")
    print(f"Tracking ID: {response.order_tracking_id}")
    
    # Step 4: Check payment status
    status = await client.get_payment_status(response.order_tracking_id)
    print(f"Status: {status.payment_status_description}")

asyncio.run(main())
```

## Features

- ✅ Async/await support
- ✅ Type-safe with Pydantic models
- ✅ Payment processing & status checking
- ✅ Refunds & cancellations
- ✅ IPN management
- ✅ Webhook signature verification
- ✅ Sandbox & production modes

## Usage Guide

### 1. Initialize Client

```python
from pesapal import PesapalClient

# Sandbox (testing)
client = PesapalClient(
    consumer_key="your_key",
    consumer_secret="your_secret",
    sandbox=True
)

# Production
client = PesapalClient(
    consumer_key="your_key",
    consumer_secret="your_secret",
    sandbox=False
)
```

### 2. Register IPN (One-Time Setup)

Register your IPN URL once and save the IPN ID for all future payments.

```python
# Register IPN URL
ipn = await client.register_ipn(
    ipn_url="https://your-domain.com/callback",
    ipn_notification_type="GET"  # or "POST"
)

# Save this IPN ID
ipn_id = ipn.notification_id
print(f"IPN ID: {ipn_id}")  # Store this in your database/config

# List all registered IPNs
ipn_list = await client.get_registered_ipns()
for registered_ipn in ipn_list:
    print(f"{registered_ipn.notification_id}: {registered_ipn.ipn_url}")
```

### 3. Create Payment Request

```python
from pesapal import PaymentRequest
from decimal import Decimal

payment = PaymentRequest(
    id="ORDER-001",  # Unique order ID (max 50 chars)
    amount=Decimal("75000.00"),  # Use Decimal for currency
    currency="TZS",  # TZS, KES, UGX, RWF, USD
    description="Product purchase",  # Max 100 chars
    callback_url="https://your-domain.com/callback",
    notification_id=ipn_id,  # From step 2
    billing_address={
        "email_address": "customer@example.com",
        "phone_number": "+255712345678",
        "country_code": "TZ",
        "first_name": "Jane",
        "middle_name": "",  # Optional
        "last_name": "Smith",
        "line_1": "456 Market Street",
        "line_2": "",  # Optional
        "city": "Dar es Salaam",
        "state": "",  # Optional
        "postal_code": "11102",
        "zip_code": "11102"  # Same as postal_code
    }
)
```

### 4. Submit Payment Order

```python
response = await client.submit_order(payment)

# Response contains:
print(f"Tracking ID: {response.order_tracking_id}")
print(f"Redirect URL: {response.redirect_url}")

# Redirect customer to response.redirect_url
```

### 5. Check Payment Status

```python
# Using tracking ID (recommended)
status = await client.get_payment_status(
    order_tracking_id="tracking-id-from-response"
)

print(f"Status: {status.payment_status_description}")
print(f"Status Code: {status.status_code}")  # "0"=Pending, "1"=Completed, "2"=Failed
print(f"Amount: {status.amount} {status.currency}")
print(f"Payment Method: {status.payment_method}")
print(f"Confirmation Code: {status.confirmation_code}")
```

### 6. Process Refund

```python
result = await client.refund_order(
    confirmation_code="confirmation-code-from-payment",
    amount=Decimal("25000.00"),  # Refund amount (must be <= original amount)
    username="admin",  # Your username/identifier
    remarks="Customer requested refund"
)

print(f"Refund Status: {result.get('status')}")
print(f"Refund Message: {result.get('message')}")
```

### 7. Cancel Pending Order

```python
result = await client.cancel_order(
    order_tracking_id="tracking-id"
)

print(f"Cancel Status: {result.get('status')}")
```

## Complete Payment Flow Example

```python
import asyncio
from pesapal import PesapalClient, PaymentRequest, PesapalError
from decimal import Decimal

async def complete_payment_flow():
    # Initialize client
    client = PesapalClient(
        consumer_key="your_consumer_key",
        consumer_secret="your_consumer_secret",
        sandbox=True
    )
    
    # 1. Register IPN (do this once, reuse the IPN ID)
    try:
        ipn = await client.register_ipn(
            ipn_url="https://your-domain.com/callback",
            ipn_notification_type="GET"
        )
        print(f"Registered IPN ID: {ipn.notification_id}")
    except PesapalError as e:
        print(f"IPN already registered or error: {e}")
        # Use existing IPN ID
        ipn_id = "your-existing-ipn-id"
    else:
        ipn_id = ipn.notification_id
    
    # 2. Create payment request
    payment = PaymentRequest(
        id="ORDER-TZS-001",
        amount=Decimal("75000.00"),
        currency="TZS",
        description="Online purchase",
        callback_url="https://your-domain.com/callback",
        notification_id=ipn_id,
        billing_address={
            "email_address": "customer@example.com",
            "phone_number": "+255712345678",
            "country_code": "TZ",
            "first_name": "Jane",
            "middle_name": "",
            "last_name": "Smith",
            "line_1": "456 Market Street",
            "line_2": "",
            "city": "Dar es Salaam",
            "state": "",
            "postal_code": "11102",
            "zip_code": "11102"
        }
    )
    
    # 3. Submit payment order
    try:
        response = await client.submit_order(payment)
        print(f"Payment URL: {response.redirect_url}")
        print(f"Tracking ID: {response.order_tracking_id}")
    except PesapalError as e:
        print(f"Payment submission failed: {e}")
        return None
    
    # 4. Check payment status
    status = await client.get_payment_status(response.order_tracking_id)
    print(f"Payment Status: {status.payment_status_description}")
    print(f"Amount: {status.amount} {status.currency}")
    
    return response

asyncio.run(complete_payment_flow())
```

## Webhook Signature Verification

Verify webhook signatures to ensure requests are from Pesapal:

```python
from pesapal.utils import verify_webhook_signature

# In your webhook handler
webhook_data = {
    "OrderTrackingId": "...",
    "OrderMerchantReference": "...",
    "OrderNotificationType": "IPNCHANGE"
}

signature = request.headers.get("X-Pesapal-Signature")
is_valid = verify_webhook_signature(
    webhook_data,
    signature,
    consumer_secret="your_consumer_secret"
)

if is_valid:
    # Process webhook
    pass
else:
    # Reject webhook
    pass
```

## Error Handling

```python
from pesapal import (
    PesapalError,
    PesapalAPIError,
    PesapalAuthenticationError,
    PesapalValidationError,
    PesapalNetworkError
)

try:
    response = await client.submit_order(payment)
except PesapalAuthenticationError:
    print("Authentication failed - check your credentials")
except PesapalValidationError as e:
    print(f"Validation error: {e} - check your payment request data")
except PesapalAPIError as e:
    print(f"API error: {e} - Pesapal returned an error")
except PesapalNetworkError as e:
    print(f"Network error: {e} - check your internet connection")
except PesapalError as e:
    print(f"General error: {e}")
```

## Payment Flow

```
1. Initialize Client
   → PesapalClient(consumer_key, consumer_secret, sandbox=True)

2. Register IPN (one-time setup)
   → client.register_ipn(ipn_url, ipn_notification_type="GET")
   → Save the returned notification_id

3. Create Payment Request
   → PaymentRequest(id, amount, currency, callback_url, notification_id, billing_address)

4. Submit Order
   → client.submit_order(payment_request)
   → Returns redirect_url and order_tracking_id

5. Redirect Customer
   → Customer completes payment on Pesapal using redirect_url

6. Check Status
   → client.get_payment_status(order_tracking_id)
   → Monitor payment status changes

7. Process Refund (if needed)
   → client.refund_order(confirmation_code, amount, username, remarks)
```

## Supported Currencies

- **TZS** (Tanzanian Shilling) - Example: 50000.00 TZS
- **KES** (Kenyan Shilling) - Example: 1000.00 KES
- **UGX** (Ugandan Shilling) - Example: 50000.00 UGX
- **RWF** (Rwandan Franc) - Example: 10000.00 RWF
- **USD** (US Dollar) - Example: 50.00 USD

## API Reference

### PesapalClient

Main client for interacting with Pesapal API.

**Initialization:**
```python
PesapalClient(
    consumer_key: str,
    consumer_secret: str,
    sandbox: bool = True,
    timeout: int = 30
)
```

**Methods:**

- `register_ipn(ipn_url: str, ipn_notification_type: str = "GET") -> IPNRegistration`
  - Register an IPN URL and get notification_id
  
- `get_registered_ipns() -> List[IPNRegistration]`
  - Get list of all registered IPN URLs
  
- `submit_order(payment_request: PaymentRequest) -> PaymentResponse`
  - Submit a payment order and get redirect URL
  
- `get_payment_status(order_tracking_id: str) -> PaymentStatus`
  - Get current payment status by tracking ID
  
- `refund_order(confirmation_code: str, amount: Decimal, username: str, remarks: str) -> dict`
  - Process a refund for a completed payment
  
- `cancel_order(order_tracking_id: str) -> dict`
  - Cancel a pending payment order

### Models

**PaymentRequest:**
```python
PaymentRequest(
    id: str,                    # Unique order ID (max 50 chars)
    amount: Decimal,            # Payment amount
    currency: str,              # Currency code (TZS, KES, etc.)
    description: str,           # Order description (max 100 chars)
    callback_url: str,          # Callback URL for redirect
    notification_id: Optional[str] = None,  # IPN notification ID
    billing_address: Optional[dict] = None,  # Billing address
    customer: Optional[dict] = None,         # Customer info
    redirect_mode: Optional[str] = None,     # TOP_WINDOW or PARENT_WINDOW
    cancellation_url: Optional[str] = None    # Cancellation redirect URL
)
```

**PaymentResponse:**
```python
PaymentResponse(
    order_tracking_id: str,     # Tracking ID for status checks
    redirect_url: str           # URL to redirect customer
)
```

**PaymentStatus:**
```python
PaymentStatus(
    order_tracking_id: str,
    payment_method: Optional[str],
    amount: Decimal,
    currency: str,
    status_code: str,           # "0"=Pending, "1"=Completed, "2"=Failed
    payment_status_description: str,
    confirmation_code: Optional[str]
)
```

**IPNRegistration:**
```python
IPNRegistration(
    notification_id: str,    # IPN ID to use in payments
    ipn_url: str,
    ipn_notification_type: str   # "GET" or "POST"
)
```

### Exceptions

- `PesapalError` - Base exception for all Pesapal errors
- `PesapalAPIError` - API-related errors
- `PesapalAuthenticationError` - Authentication failures
- `PesapalValidationError` - Validation errors
- `PesapalNetworkError` - Network/connection errors

## Requirements

- Python 3.8+
- httpx >= 0.24.0
- pydantic >= 2.0.0

## License

MIT License

## Support

- **GitHub Issues**: [github.com/erickblema/pesapal-python-sdk/issues](https://github.com/erickblema/pesapal-python-sdk/issues)
- **Pesapal Docs**: [developer.pesapal.com](https://developer.pesapal.com)
- **Contact**: ericklema360@gmail.com

# Pesapal Python SDK

Python SDK for Pesapal Payment Gateway API 3.0 - Clean, async interface for payment processing.

## Installation

```bash
pip install pesapal-python-sdk
```

## Quick Start

```python
from pesapal import PesapalClient, PaymentRequest
from decimal import Decimal

# Initialize client
client = PesapalClient(
    consumer_key="your_consumer_key",
    consumer_secret="your_consumer_secret",
    sandbox=True
)

# Submit payment
payment = PaymentRequest(
    id="ORDER-123",
    amount=Decimal("50000.00"),
    currency="TZS",
    description="Payment for order #123",
    callback_url="https://your-domain.com/callback",
    notification_id="your_ipn_notification_id"
)

response = await client.submit_order(payment)
print(f"Redirect URL: {response.redirect_url}")
print(f"Tracking ID: {response.order_tracking_id}")
```

## Features

- ✅ Async/await support
- ✅ Type-safe with Pydantic models
- ✅ Payment processing & status checking
- ✅ Refunds & cancellations
- ✅ IPN management
- ✅ Webhook signature verification
- ✅ Sandbox & production modes

## Usage

### Complete Payment Example

```python
import asyncio
from pesapal import PesapalClient, PaymentRequest
from decimal import Decimal

async def create_payment():
    client = PesapalClient(
        consumer_key="your_consumer_key",
        consumer_secret="your_consumer_secret",
        sandbox=True
    )
    
    payment = PaymentRequest(
        id="ORDER-TZS-001",
        amount=Decimal("75000.00"),
        currency="TZS",
        description="Online purchase",
        callback_url="https://your-domain.com/callback",
        notification_id="your_ipn_id",
        customer={
            "email": "customer@example.com",
            "phone_number": "+255712345678",
            "first_name": "Jane",
            "last_name": "Smith"
        },
        billing_address={
            "email_address": "customer@example.com",
            "phone_number": "+255712345678",
            "country_code": "TZ",
            "first_name": "Jane",
            "last_name": "Smith",
            "line_1": "456 Market Street",
            "city": "Dar es Salaam",
            "postal_code": "11102"
        }
    )
    
    response = await client.submit_order(payment)
    return response

asyncio.run(create_payment())
```

### Check Payment Status

```python
status = await client.get_payment_status(
    order_tracking_id="tracking-id",
    order_id="ORDER-TZS-001"
)
print(f"Status: {status.payment_status_description}")
print(f"Amount: {status.amount} {status.currency}")
print(f"Payment Method: {status.payment_method}")
```

### Process Refund

```python
result = await client.refund_order(
    confirmation_code="confirmation-code",
    amount=Decimal("25000.00"),  # Refund amount in TZS
    username="admin",
    remarks="Customer requested refund"
)
print(f"Refund Result: {result}")
```

### Cancel Order

```python
result = await client.cancel_order(
    order_tracking_id="tracking-id"
)
print(f"Cancel Result: {result}")
```

### Register IPN

```python
ipn = await client.register_ipn(
    ipn_url="https://your-domain.com/webhooks/pesapal",
    ipn_notification_type="POST"
)
print(f"IPN ID: {ipn.notification_id}")
print(f"IPN URL: {ipn.ipn_url}")
```

### List Registered IPNs

```python
ipn_list = await client.get_registered_ipns()
for ipn in ipn_list:
    print(f"ID: {ipn.notification_id}")
    print(f"URL: {ipn.ipn_url}")
    print(f"Type: {ipn.ipn_notification_type}")
```

## Webhook Signature Verification

```python
from pesapal.utils import verify_webhook_signature

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
```

## Error Handling

```python
from pesapal import (
    PesapalError,
    PesapalAPIError,
    PesapalAuthenticationError,
    PesapalValidationError
)

try:
    response = await client.submit_order(payment)
except PesapalAuthenticationError:
    print("Authentication failed")
except PesapalValidationError as e:
    print(f"Validation error: {e}")
except PesapalAPIError as e:
    print(f"API error: {e}")
```

## Payment Flow

```
1. Initialize Client → PesapalClient(consumer_key, consumer_secret)
2. Create Payment → PaymentRequest(amount, currency="TZS", ...)
3. Submit Order → client.submit_order(payment)
4. Redirect Customer → Customer pays on Pesapal
5. Check Status → client.get_payment_status(tracking_id, order_id)
6. Process Refund → client.refund_order(...) [if needed]
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

**Methods:**
- `submit_order(payment_request: PaymentRequest) -> PaymentResponse`
- `get_payment_status(order_tracking_id: str, order_id: str) -> PaymentStatus`
- `refund_order(confirmation_code: str, amount: Decimal, username: str, remarks: str) -> dict`
- `cancel_order(order_tracking_id: str) -> dict`
- `register_ipn(ipn_url: str, ipn_notification_type: str = "GET") -> IPNRegistration`
- `get_registered_ipns() -> List[IPNRegistration]`

### Models

- `PaymentRequest` - Payment order request
- `PaymentResponse` - Payment submission response
- `PaymentStatus` - Payment status information
- `IPNRegistration` - IPN registration information

### Exceptions

- `PesapalError` - Base exception
- `PesapalAPIError` - API errors
- `PesapalAuthenticationError` - Authentication failures
- `PesapalValidationError` - Validation errors
- `PesapalNetworkError` - Network errors

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

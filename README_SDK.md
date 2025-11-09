# Pesapal Python SDK

[![PyPI version](https://badge.fury.io/py/pesapal-python-sdk.svg)](https://badge.fury.io/py/pesapal-python-sdk)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Python SDK for integrating with Pesapal Payment Gateway API 3.0. This SDK provides a clean, async interface for payment processing, status checking, refunds, cancellations, and IPN management.

## Features

- ✅ **Async/Await Support** - Built with modern Python async patterns
- ✅ **Type Safety** - Full type hints and Pydantic models
- ✅ **Payment Processing** - Submit orders, check status, handle callbacks
- ✅ **Refunds & Cancellations** - Process refunds and cancel pending orders
- ✅ **IPN Management** - Register and manage Instant Payment Notifications
- ✅ **Webhook Verification** - Built-in signature verification
- ✅ **Error Handling** - Comprehensive exception handling
- ✅ **Sandbox Support** - Test with Pesapal sandbox environment

## Installation

```bash
pip install pesapal-python-sdk
```

## Quick Start

### 1. Initialize the Client

```python
from pesapal import PesapalClient

client = PesapalClient(
    consumer_key="your_consumer_key",
    consumer_secret="your_consumer_secret",
    sandbox=True  # Set to False for production
)
```

### 2. Submit a Payment Order

```python
from pesapal import PaymentRequest
from decimal import Decimal

payment_request = PaymentRequest(
    id="ORDER-123",
    amount=Decimal("1000.00"),
    currency="KES",
    description="Payment for order #123",
    callback_url="https://your-domain.com/callback",
    notification_id="your_ipn_notification_id",
    customer={
        "email": "customer@example.com",
        "phone_number": "+254712345678",
        "first_name": "John",
        "last_name": "Doe"
    },
    billing_address={
        "email_address": "customer@example.com",
        "phone_number": "+254712345678",
        "country_code": "KE",
        "first_name": "John",
        "last_name": "Doe",
        "line_1": "123 Main St",
        "city": "Nairobi",
        "postal_code": "00100"
    }
)

response = await client.submit_order(payment_request)
print(f"Redirect URL: {response.redirect_url}")
print(f"Tracking ID: {response.order_tracking_id}")
```

### 3. Check Payment Status

```python
status = await client.get_payment_status(
    order_tracking_id="tracking-id-here",
    order_id="ORDER-123"
)

print(f"Status: {status.payment_status_description}")
print(f"Payment Method: {status.payment_method}")
print(f"Confirmation Code: {status.confirmation_code}")
```

### 4. Process a Refund

```python
from decimal import Decimal

result = await client.refund_order(
    confirmation_code="confirmation-code-here",
    amount=Decimal("500.00"),
    username="admin",
    remarks="Customer requested refund",
    order_tracking_id="tracking-id-here"
)
```

### 5. Cancel an Order

```python
result = await client.cancel_order(
    order_tracking_id="tracking-id-here"
)
```

### 6. Register IPN URL

```python
from pesapal import IPNRegistration

ipn = await client.register_ipn(
    ipn_url="https://your-domain.com/webhooks/pesapal",
    ipn_notification_type="POST"
)

print(f"IPN Notification ID: {ipn.notification_id}")
```

### 7. List Registered IPNs

```python
ipn_list = await client.get_registered_ipns()
for ipn in ipn_list:
    print(f"ID: {ipn.notification_id}, URL: {ipn.ipn_url}")
```

## Error Handling

The SDK provides specific exception types for different error scenarios:

```python
from pesapal import (
    PesapalError,
    PesapalAPIError,
    PesapalAuthenticationError,
    PesapalValidationError
)

try:
    response = await client.submit_order(payment_request)
except PesapalAuthenticationError:
    print("Authentication failed - check your credentials")
except PesapalValidationError as e:
    print(f"Validation error: {e}")
except PesapalAPIError as e:
    print(f"API error: {e}")
except PesapalError as e:
    print(f"General error: {e}")
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

if is_valid:
    # Process webhook
    pass
```

## Supported Currencies

- KES (Kenyan Shilling)
- TZS (Tanzanian Shilling)
- UGX (Ugandan Shilling)
- RWF (Rwandan Franc)
- USD (US Dollar)

## API Reference

### PesapalClient

Main client class for interacting with Pesapal API.

#### Methods

- `submit_order(payment_request: PaymentRequest) -> PaymentResponse`
- `get_payment_status(order_tracking_id: str, order_id: str) -> PaymentStatus`
- `refund_order(confirmation_code: str, amount: Decimal, username: str, remarks: str, order_tracking_id: Optional[str] = None) -> dict`
- `cancel_order(order_tracking_id: str) -> dict`
- `register_ipn(ipn_url: str, ipn_notification_type: str = "GET") -> IPNRegistration`
- `get_registered_ipns() -> List[IPNRegistration]`

### Models

- `PaymentRequest` - Payment order request model
- `PaymentResponse` - Payment submission response
- `PaymentStatus` - Payment status information
- `IPNRegistration` - IPN registration information

### Exceptions

- `PesapalError` - Base exception class
- `PesapalAPIError` - API-related errors
- `PesapalAuthenticationError` - Authentication failures
- `PesapalValidationError` - Validation errors

## Requirements

- Python 3.8+
- httpx >= 0.24.0
- pydantic >= 2.0.0

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions:
- GitHub Issues: [https://github.com/yourusername/pesapal-python-sdk/issues](https://github.com/yourusername/pesapal-python-sdk/issues)
- Pesapal Documentation: [https://developer.pesapal.com](https://developer.pesapal.com)

## Changelog

### 1.0.0 (2025-01-XX)
- Initial release
- Payment submission and status checking
- Refund and cancellation support
- IPN management
- Webhook signature verification


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
    amount=Decimal("1000.00"),
    currency="KES",
    description="Payment for order #123",
    callback_url="https://your-domain.com/callback",
    notification_id="your_ipn_notification_id"
)

response = await client.submit_order(payment)
print(f"Redirect URL: {response.redirect_url}")
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

### Check Payment Status

```python
status = await client.get_payment_status(
    order_tracking_id="tracking-id",
    order_id="ORDER-123"
)
print(f"Status: {status.payment_status_description}")
```

### Process Refund

```python
result = await client.refund_order(
    confirmation_code="confirmation-code",
    amount=Decimal("500.00"),
    username="admin",
    remarks="Customer requested refund"
)
```

### Cancel Order

```python
result = await client.cancel_order(
    order_tracking_id="tracking-id"
)
```

### Register IPN

```python
ipn = await client.register_ipn(
    ipn_url="https://your-domain.com/webhooks/pesapal",
    ipn_notification_type="POST"
)
print(f"IPN ID: {ipn.notification_id}")
```

### List Registered IPNs

```python
ipn_list = await client.get_registered_ipns()
for ipn in ipn_list:
    print(f"ID: {ipn.notification_id}, URL: {ipn.ipn_url}")
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

## Supported Currencies

- KES (Kenyan Shilling)
- TZS (Tanzanian Shilling)
- UGX (Ugandan Shilling)
- RWF (Rwandan Franc)
- USD (US Dollar)

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

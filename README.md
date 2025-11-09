# Pesapal Python SDK

[![PyPI version](https://badge.fury.io/py/pesapal-python-sdk.svg)](https://badge.fury.io/py/pesapal-python-sdk)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Python SDK for Pesapal Payment Gateway API 3.0 - Clean, async interface for payment processing.

## 🚀 Quick Start

```bash
pip install pesapal-python-sdk
```

```python
from pesapal import PesapalClient, PaymentRequest
from decimal import Decimal

# Initialize client
client = PesapalClient(
    consumer_key="your_key",
    consumer_secret="your_secret",
    sandbox=True
)

# Submit payment
payment = PaymentRequest(
    id="ORDER-123",
    amount=Decimal("50000.00"),
    currency="TZS",
    description="Payment for order #123",
    callback_url="https://your-domain.com/callback",
    notification_id="your_ipn_id"
)

response = await client.submit_order(payment)
print(f"Redirect: {response.redirect_url}")
```

## ✨ Features

- ✅ Async/await support
- ✅ Type-safe with Pydantic
- ✅ Payment processing & status checking
- ✅ Refunds & cancellations
- ✅ IPN management
- ✅ Webhook signature verification
- ✅ Sandbox & production modes

## 📚 Documentation

- **Full Documentation**: See [README_SDK.md](README_SDK.md)
- **API Reference**: [GitHub Repository](https://github.com/erickblema/pesapal-python-sdk)
- **Pesapal Docs**: [developer.pesapal.com](https://developer.pesapal.com)

## 🔧 Installation

```bash
pip install pesapal-python-sdk
```

## 💡 Usage Examples

### Complete Payment Flow

```python
import asyncio
from pesapal import PesapalClient, PaymentRequest
from decimal import Decimal

async def process_payment():
    client = PesapalClient(
        consumer_key="your_key",
        consumer_secret="your_secret",
        sandbox=True
    )
    
    # Create payment with customer details
    payment = PaymentRequest(
        id="ORDER-TZS-001",
        amount=Decimal("25000.00"),
        currency="TZS",
        description="Product purchase",
        callback_url="https://your-domain.com/callback",
        notification_id="your_ipn_id",
        customer={
            "email": "customer@example.com",
            "phone_number": "+255712345678",
            "first_name": "John",
            "last_name": "Doe"
        },
        billing_address={
      "email_address": "customer@example.com",
            "phone_number": "+255712345678",
      "country_code": "TZ",
      "first_name": "John",
      "last_name": "Doe",
            "line_1": "123 Main Street",
      "city": "Dar es Salaam",
            "postal_code": "11101"
    }
    )
    
    # Submit payment
    response = await client.submit_order(payment)
    print(f"Tracking ID: {response.order_tracking_id}")
    print(f"Redirect URL: {response.redirect_url}")
    
    return response

# Run
asyncio.run(process_payment())
```

### Check Payment Status

```python
status = await client.get_payment_status(
    order_tracking_id="tracking-id",
    order_id="ORDER-TZS-001"
)
print(f"Status: {status.payment_status_description}")
print(f"Payment Method: {status.payment_method}")
print(f"Confirmation Code: {status.confirmation_code}")
```

### Process Refund

```python
result = await client.refund_order(
    confirmation_code="confirmation-code",
    amount=Decimal("10000.00"),  # Partial refund in TZS
    username="admin",
    remarks="Customer requested partial refund"
)
print(f"Refund Status: {result.get('status')}")
```

### Cancel Pending Order

```python
result = await client.cancel_order(
    order_tracking_id="tracking-id"
)
print(f"Cancel Status: {result.get('status')}")
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

### List All IPNs

```python
ipn_list = await client.get_registered_ipns()
for ipn in ipn_list:
    print(f"{ipn.notification_id}: {ipn.ipn_url} ({ipn.ipn_notification_type})")
```

## 🔄 Payment Flow

```
1. Create Payment Request
   └─> PaymentRequest(id, amount, currency="TZS", ...)
   
2. Submit to Pesapal
   └─> client.submit_order(payment)
   └─> Returns: redirect_url & tracking_id
   
3. Customer Completes Payment
   └─> Redirect customer to redirect_url
   └─> Customer pays on Pesapal
   
4. Check Status
   └─> client.get_payment_status(tracking_id, order_id)
   └─> Returns: status, payment_method, confirmation_code
   
5. Process Refund (if needed)
   └─> client.refund_order(confirmation_code, amount, ...)
```

## 🏗️ Project Structure

```
pesapal-python-sdk/
├── pesapal/              # SDK package
│   ├── client.py        # Main client
│   ├── models.py        # Pydantic models
│   ├── exceptions.py    # Error handling
│   └── utils.py         # Utilities
├── app/                 # FastAPI example app (not published)
└── README_SDK.md        # Full SDK documentation
```

## 📦 Requirements

- Python 3.8+
- httpx >= 0.24.0
- pydantic >= 2.0.0

## 🔗 Links

- **PyPI**: [pypi.org/project/pesapal-python-sdk](https://pypi.org/project/pesapal-python-sdk)
- **GitHub**: [github.com/erickblema/pesapal-python-sdk](https://github.com/erickblema/pesapal-python-sdk)
- **Issues**: [GitHub Issues](https://github.com/erickblema/pesapal-python-sdk/issues)

## 📄 License

MIT License - See [LICENSE](LICENSE) file

## 👤 Author

**Erick Lema**  
Email: ericklema360@gmail.com

---

**Note**: The `app/` directory contains a FastAPI example application and is not part of the published SDK package.

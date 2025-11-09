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
    amount=Decimal("1000.00"),
    currency="KES",
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

### Register IPN

```python
ipn = await client.register_ipn(
    ipn_url="https://your-domain.com/webhooks/pesapal",
    ipn_notification_type="POST"
)
print(f"IPN ID: {ipn.notification_id}")
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

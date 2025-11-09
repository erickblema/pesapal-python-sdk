# Pesapal Python SDK

[![PyPI version](https://badge.fury.io/py/pesapal-python-sdk.svg)](https://badge.fury.io/py/pesapal-python-sdk)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Python SDK for Pesapal Payment Gateway API 3.0 - Clean, async interface for payment processing in Tanzania, Kenya, Uganda, Rwanda, and more.

## 📦 Installation

```bash
pip install pesapal-python-sdk
```

## 🚀 Quick Start

### Step 1: Get Your Credentials

1. Sign up at [Pesapal Developer Portal](https://developer.pesapal.com/)
2. Create an application
3. Get your `consumer_key` and `consumer_secret`
4. Note your callback URL (must be publicly accessible via HTTPS)

### Step 2: Basic Usage

```python
import asyncio
from pesapal import PesapalClient, PaymentRequest
from decimal import Decimal

async def main():
    # Initialize client
    client = PesapalClient(
        consumer_key="your_consumer_key",
        consumer_secret="your_consumer_secret",
        sandbox=True  # Use True for testing, False for production
    )
    
    # Step 1: Register IPN (do this once, save the IPN ID)
    ipn = await client.register_ipn(
        ipn_url="https://your-domain.com/callback",
        ipn_notification_type="GET"
    )
    print(f"IPN ID: {ipn.notification_id}")  # Save this for future use
    
    # Step 2: Create payment request
    payment = PaymentRequest(
        id="ORDER-123",  # Your unique order ID
        amount=Decimal("50000.00"),
        currency="TZS",
        description="Payment for order #123",
        callback_url="https://your-domain.com/callback",
        notification_id=ipn.notification_id,  # Use registered IPN ID
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
    print(f"Redirect customer to: {response.redirect_url}")
    print(f"Tracking ID: {response.order_tracking_id}")
    
    # Step 4: Check payment status
    status = await client.get_payment_status(response.order_tracking_id)
    print(f"Status: {status.payment_status_description}")

asyncio.run(main())
```

## ✨ Features

- ✅ **Async/await support** - Modern Python async patterns
- ✅ **Type-safe** - Built with Pydantic for validation
- ✅ **Payment processing** - Initiate and track payments
- ✅ **Status checking** - Real-time payment status updates
- ✅ **Refunds & cancellations** - Full payment lifecycle management
- ✅ **IPN management** - Register and manage Instant Payment Notifications
- ✅ **Webhook verification** - Secure webhook signature verification
- ✅ **Sandbox & production** - Easy environment switching

## 📖 Common Use Cases

### Use Case 1: E-commerce Payment

```python
async def process_ecommerce_payment(order_id: str, amount: Decimal, customer_email: str):
    client = PesapalClient(
        consumer_key="your_key",
        consumer_secret="your_secret",
        sandbox=False  # Production mode
    )
    
    # Use pre-registered IPN ID (register once, reuse)
    payment = PaymentRequest(
        id=order_id,
        amount=amount,
        currency="TZS",
        description=f"Order #{order_id}",
        callback_url="https://yourstore.com/payment/callback",
        notification_id="your-saved-ipn-id",
        billing_address={
            "email_address": customer_email,
            "phone_number": "+255123456789",
            "country_code": "TZ",
            "first_name": "Customer",
            "last_name": "Name",
            "line_1": "Address",
            "city": "City",
            "postal_code": "11101"
        }
    )
    
    response = await client.submit_order(payment)
    return response.redirect_url  # Redirect customer to this URL
```

### Use Case 2: Check Payment Status

```python
async def check_payment(tracking_id: str):
    client = PesapalClient(
        consumer_key="your_key",
        consumer_secret="your_secret",
        sandbox=False
    )
    
    status = await client.get_payment_status(tracking_id)
    
    if status.status_code == "1":  # Completed
        print(f"Payment completed: {status.confirmation_code}")
        print(f"Amount: {status.amount} {status.currency}")
        print(f"Method: {status.payment_method}")
    elif status.status_code == "0":  # Pending
        print("Payment is still pending")
    else:
        print(f"Payment status: {status.payment_status_description}")
    
    return status
```

### Use Case 3: Process Refund

```python
async def refund_payment(confirmation_code: str, refund_amount: Decimal):
    client = PesapalClient(
        consumer_key="your_key",
        consumer_secret="your_secret",
        sandbox=False
    )
    
    result = await client.refund_order(
        confirmation_code=confirmation_code,
        amount=refund_amount,
        username="admin",
        remarks="Customer requested refund"
    )
    
    return result
```

## 🔧 Configuration

### Environment Variables (Recommended)

```python
import os
from pesapal import PesapalClient

client = PesapalClient(
    consumer_key=os.getenv("PESAPAL_CONSUMER_KEY"),
    consumer_secret=os.getenv("PESAPAL_CONSUMER_SECRET"),
    sandbox=os.getenv("PESAPAL_SANDBOX", "True").lower() == "true"
)
```

### Settings File

```python
# config.py
PESAPAL_CONSUMER_KEY = "your_key"
PESAPAL_CONSUMER_SECRET = "your_secret"
PESAPAL_SANDBOX = True
PESAPAL_CALLBACK_URL = "https://your-domain.com/callback"
PESAPAL_IPN_ID = "your-ipn-id"  # Register once, save it
```

## 📚 Complete Examples

### Full Payment Flow with Error Handling

```python
import asyncio
from pesapal import PesapalClient, PaymentRequest, PesapalError
from decimal import Decimal

async def complete_payment_flow():
    try:
        client = PesapalClient(
            consumer_key="your_key",
            consumer_secret="your_secret",
            sandbox=True
        )
        
        # Register IPN (if not already registered)
        try:
            ipn = await client.register_ipn(
                ipn_url="https://your-domain.com/callback",
                ipn_notification_type="GET"
            )
            ipn_id = ipn.notification_id
        except PesapalError as e:
            print(f"IPN registration failed: {e}")
            # Use existing IPN ID if registration fails
            ipn_id = "your-existing-ipn-id"
        
        # Create payment
        payment = PaymentRequest(
            id="ORDER-001",
            amount=Decimal("100000.00"),
            currency="TZS",
            description="Product purchase",
            callback_url="https://your-domain.com/callback",
            notification_id=ipn_id,
            billing_address={
                "email_address": "customer@example.com",
                "phone_number": "+255712345678",
                "country_code": "TZ",
                "first_name": "John",
                "last_name": "Doe",
                "line_1": "123 Main St",
                "city": "Dar es Salaam",
                "postal_code": "11101"
            }
        )
        
        # Submit payment
        response = await client.submit_order(payment)
        print(f"✅ Payment created!")
        print(f"   Redirect URL: {response.redirect_url}")
        print(f"   Tracking ID: {response.order_tracking_id}")
        
        # Monitor payment status
        import time
        for _ in range(10):  # Check up to 10 times
            time.sleep(5)  # Wait 5 seconds between checks
            status = await client.get_payment_status(response.order_tracking_id)
            print(f"Status: {status.payment_status_description}")
            
            if status.status_code == "1":  # Completed
                print("✅ Payment completed!")
                break
        
        return response
        
    except PesapalError as e:
        print(f"❌ Error: {e}")
        return None

asyncio.run(complete_payment_flow())
```

## 🔄 Payment Flow Diagram

```
┌─────────────────┐
│  Initialize     │
│  Client         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Register IPN   │ ◄─── One-time setup
│  (Save IPN ID)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Create Payment │
│  Request        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Submit Order   │
│  Get redirect   │
│  URL            │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Redirect       │
│  Customer       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Customer Pays  │
│  on Pesapal     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Check Status   │ ◄─── Poll or use webhook
│  Process Result │
└─────────────────┘
```

## 💡 Best Practices

1. **Register IPN Once**: Register your IPN URL once and save the IPN ID. Reuse it for all payments.

2. **Use Environment Variables**: Never hardcode credentials. Use environment variables or secure config files.

3. **Handle Errors**: Always wrap API calls in try-except blocks to handle errors gracefully.

4. **Validate Amounts**: Use `Decimal` for currency amounts to avoid floating-point errors.

5. **Unique Order IDs**: Ensure each payment has a unique `id` (order ID).

6. **HTTPS Callbacks**: Your callback URL must be publicly accessible via HTTPS.

7. **Status Polling**: For real-time updates, implement webhook handlers instead of polling.

## 🐛 Troubleshooting

### Issue: "Invalid IPN ID"
**Solution**: Make sure you've registered the IPN first and are using the correct `notification_id`.

### Issue: "Authentication failed"
**Solution**: Verify your `consumer_key` and `consumer_secret` are correct and match your environment (sandbox/production).

### Issue: "Invalid amount"
**Solution**: Ensure amounts are formatted with exactly 2 decimal places (e.g., `Decimal("100.00")`).

### Issue: "Callback URL not accessible"
**Solution**: Your callback URL must be publicly accessible via HTTPS. Use tools like ngrok for local testing.

## 📋 API Reference

### PesapalClient Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `register_ipn(ipn_url, ipn_notification_type)` | Register IPN URL | `IPNRegistration` |
| `get_registered_ipns()` | List all registered IPNs | `List[IPNRegistration]` |
| `submit_order(payment_request)` | Submit payment order | `PaymentResponse` |
| `get_payment_status(order_tracking_id)` | Get payment status | `PaymentStatus` |
| `refund_order(confirmation_code, amount, username, remarks)` | Process refund | `dict` |
| `cancel_order(order_tracking_id)` | Cancel pending payment | `dict` |

### Payment Status Codes

- `"0"` - Pending
- `"1"` - Completed
- `"2"` - Failed
- `"3"` - Invalid

## 🌍 Supported Currencies

- **TZS** - Tanzanian Shilling (Example: 50000.00 TZS)
- **KES** - Kenyan Shilling (Example: 1000.00 KES)
- **UGX** - Ugandan Shilling (Example: 50000.00 UGX)
- **RWF** - Rwandan Franc (Example: 10000.00 RWF)
- **USD** - US Dollar (Example: 50.00 USD)

## 📦 Requirements

- Python 3.8+
- httpx >= 0.24.0
- pydantic >= 2.0.0

## 🔗 Links

- **PyPI**: [pypi.org/project/pesapal-python-sdk](https://pypi.org/project/pesapal-python-sdk)
- **GitHub**: [github.com/erickblema/pesapal-python-sdk](https://github.com/erickblema/pesapal-python-sdk)
- **Issues**: [GitHub Issues](https://github.com/erickblema/pesapal-python-sdk/issues)
- **Pesapal Docs**: [developer.pesapal.com](https://developer.pesapal.com)

## 📄 License

MIT License - See [LICENSE](LICENSE) file

## 👤 Author

**Erick Lema**  
Email: ericklema360@gmail.com

---

**Note**: The `app/` directory contains a FastAPI example application and is not part of the published SDK package.

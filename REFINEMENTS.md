# Pesapal SDK Refinements - Official Documentation Compliance

This document outlines the refinements made to align the codebase with the official Pesapal API 3.0 documentation.

## ✅ Completed Refinements

### 1. Token Expiration Handling (5 Minutes Lifetime)
**Location:** `pesapal/client.py`

- **Added:** Token expiration tracking with `_token_expires_at` field
- **Implementation:** 
  - Tokens are automatically refreshed when expired (with 30-second buffer)
  - Token expiration is set to 5 minutes from issuance (as per Pesapal docs)
  - Automatic retry on 401 errors with token refresh
- **Key Features:**
  - Prevents token expiration issues
  - Seamless automatic renewal
  - Logs token refresh events

### 2. Register IPN URL Endpoint
**Location:** `pesapal/client.py` → `register_ipn()` method

- **Endpoint:** `/api/URLSetup/RegisterIPN`
- **Purpose:** Register your IPN URL to receive payment notifications
- **Returns:** `notification_id` that you use when submitting orders
- **API Route:** `POST /ipn/register`
- **Usage:**
  ```python
  registration = await client.register_ipn(
      ipn_url="https://your-domain.com/webhooks/pesapal",
      ipn_notification_type="GET"  # or "POST"
  )
  # Save registration.notification_id for use in payment requests
  ```

### 3. Get List of Registered IPNs
**Location:** `pesapal/client.py` → `get_registered_ipns()` method

- **Endpoint:** `/api/URLSetup/GetRegisteredNotificationUrl`
- **Purpose:** Retrieve all registered IPN URLs for your merchant account
- **API Route:** `GET /ipn/list`
- **Usage:**
  ```python
  ipn_list = await client.get_registered_ipns()
  # Returns list of IPNRegistration objects
  ```

### 4. Refund Request Endpoint
**Location:** `pesapal/client.py` → `refund_order()` method

- **Endpoint:** `/api/Transactions/RefundOrder`
- **Purpose:** Request a refund for a completed payment
- **API Route:** `POST /payments/refund`
- **Features:**
  - Full refund (if amount not specified)
  - Partial refund (if amount specified)
  - Optional refund reason
- **Usage:**
  ```python
  # Full refund
  result = await client.refund_order(order_tracking_id="...")
  
  # Partial refund
  result = await client.refund_order(
      order_tracking_id="...",
      amount=Decimal("500.00"),
      currency="KES",
      reason="Customer request"
  )
  ```

### 5. Order Cancellation Endpoint
**Location:** `pesapal/client.py` → `cancel_order()` method

- **Endpoint:** `/api/Transactions/CancelOrder`
- **Purpose:** Cancel a pending payment order
- **API Route:** `POST /payments/cancel`
- **Usage:**
  ```python
  result = await client.cancel_order(order_tracking_id="...")
  ```

### 6. Updated Constants
**Location:** `pesapal/constants.py`

Added all required endpoint constants:
- `ENDPOINT_IPN_REGISTER`
- `ENDPOINT_IPN_LIST`
- `ENDPOINT_REFUND`
- `ENDPOINT_CANCEL_ORDER`

### 7. New API Routes
**Location:** `app/routers/`

- **IPN Management Router:** `app/routers/ipn.py`
  - `POST /ipn/register` - Register IPN URL
  - `GET /ipn/list` - List registered IPNs
  
- **Payment Operations Router:** `app/routers/payments.py` (updated)
  - `POST /payments/refund` - Request refund
  - `POST /payments/cancel` - Cancel order

## 🔄 Complete Payment Flow (As Per Official Docs)

### Step 1: Authenticate
```python
# Automatic - handled by PesapalClient
# Token obtained on first API call
# Token expires in 5 minutes, auto-refreshed
```

### Step 2: Register IPN URL (One-time setup)
```python
# Register your IPN URL
registration = await client.register_ipn(
    ipn_url="https://your-domain.com/webhooks/pesapal",
    ipn_notification_type="GET"
)
# Save registration.notification_id
```

### Step 3: Submit Order Request
```python
payment_request = PaymentRequest(
    id="ORDER-123",
    amount=Decimal("1000.00"),
    currency="KES",
    description="Payment description",
    callback_url="https://your-domain.com/payments/callback",
    notification_id=registration.notification_id  # From step 2
)
response = await client.submit_order(payment_request)
# Returns: order_tracking_id + redirect_url
```

### Step 4: Customer Completes Payment
- Customer is redirected to `redirect_url`
- Customer completes payment on Pesapal side

### Step 5: Receive Notifications
Pesapal does two things:
1. **Callback URL** - Redirects customer back with:
   - `OrderTrackingId`
   - `OrderMerchantReference`
   - `OrderNotificationType = "CALLBACKURL"`
   
2. **IPN** - Sends notification to your IPN URL with:
   - `OrderTrackingId`
   - `OrderMerchantReference`
   - `OrderNotificationType = "IPNCHANGE"`

### Step 6: Get Transaction Status
```python
# IMPORTANT: Callback/IPN do NOT include full status
# You MUST call GetTransactionStatus API
status = await client.get_payment_status(
    order_tracking_id="...",
    merchant_reference="ORDER-123"
)
# Update your database based on status
```

### Step 7: Additional Operations (Optional)
```python
# Refund
await client.refund_order(order_tracking_id="...")

# Cancel
await client.cancel_order(order_tracking_id="...")
```

## 🔑 Key Improvements

1. **Token Management:**
   - Automatic expiration handling (5 minutes)
   - Automatic refresh on 401 errors
   - Prevents authentication failures

2. **Complete API Coverage:**
   - All official endpoints implemented
   - Proper error handling
   - Comprehensive logging

3. **IPN Management:**
   - Programmatic IPN registration
   - List registered IPNs
   - Proper notification_id handling

4. **Payment Operations:**
   - Refund support (full & partial)
   - Order cancellation
   - Status checking

5. **Documentation:**
   - All methods documented
   - Flow sequence documented
   - Usage examples provided

## 📝 Important Notes

1. **Base URLs:**
   - Sandbox: `https://cybqa.pesapal.com/pesapalv3`
   - Production: `https://pay.pesapal.com/v3`

2. **Token Lifetime:**
   - 5 minutes (handled automatically)
   - Refreshed on expiration or 401 errors

3. **IPN URL Requirements:**
   - Must be publicly accessible (HTTPS)
   - Must be registered before submitting orders
   - Use `notification_id` from registration in payment requests

4. **Status Checking:**
   - Callback/IPN do NOT contain full payment status
   - Always call `GetTransactionStatus` API after receiving callback/IPN
   - Status codes: 0=INVALID, 1=COMPLETED, 2=FAILED, 3=REVERSED

## 🧪 Testing

All endpoints are available via Swagger UI:
- Start server: `uvicorn main:app --reload`
- Access: `http://localhost:8000/docs`

## 📚 References

- Official Pesapal API 3.0 Documentation
- Base URLs and endpoints documented in `PESAPAL_URLS.md`
- Payment flow documented in this file


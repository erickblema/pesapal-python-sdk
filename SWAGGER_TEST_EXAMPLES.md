# Swagger Test Examples - Pesapal Payment API

## 🚀 Quick Start

1. Start server: `uvicorn main:app --reload`
2. Open Swagger: `http://localhost:8000/docs`
3. Click **POST /payments/** → **Try it out**
4. Copy any JSON below and paste into request body
5. Click **Execute**

---

## 📋 Example 1: Basic Payment (KES)

```json
{
  "order_id": "ORDER-001",
  "amount": "100.00",
  "currency": "KES",
  "description": "Payment for KES 100"
}
```

---

## 📋 Example 2: Basic Payment (TZS - Tanzania)

```json
{
  "order_id": "ORDER-002",
  "amount": "50000.00",
  "currency": "TZS",
  "description": "Payment for TZS 50000"
}
```

---

## 📋 Example 3: Payment with Customer Info

```json
{
  "order_id": "ORDER-003",
  "amount": "250.00",
  "currency": "KES",
  "description": "Payment with customer information",
  "customer": {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone_number": "+255712345678"
  }
}
```

---

## 📋 Example 4: Full Payment (Kenya - Complete Details)

```json
{
  "order_id": "ORDER-004",
  "amount": "500.00",
  "currency": "KES",
  "description": "Payment with full customer and billing details",
  "customer": {
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane.smith@example.com",
    "phone_number": "+254712345678"
  },
  "billing_address": {
    "phone_number": "+254712345678",
    "email_address": "jane.smith@example.com",
    "country_code": "KE",
    "first_name": "Jane",
    "middle_name": "",
    "last_name": "Smith",
    "line_1": "123 Main Street",
    "line_2": "Apartment 4B",
    "city": "Nairobi",
    "state": "Nairobi",
    "postal_code": "00100",
    "zip_code": "00100"
  }
}
```

---

## 📋 Example 5: Tanzania Payment (Full Details)

```json
{
  "order_id": "ORDER-005",
  "amount": "75000.00",
  "currency": "TZS",
  "description": "Tanzania payment with full details",
  "customer": {
    "first_name": "Ahmed",
    "last_name": "Hassan",
    "email": "ahmed.hassan@example.com",
    "phone_number": "+255712345678"
  },
  "billing_address": {
    "phone_number": "+255712345678",
    "email_address": "ahmed.hassan@example.com",
    "country_code": "TZ",
    "first_name": "Ahmed",
    "middle_name": "",
    "last_name": "Hassan",
    "line_1": "456 Uhuru Street",
    "line_2": "",
    "city": "Dar es Salaam",
    "state": "",
    "postal_code": "11101",
    "zip_code": "11101"
  }
}
```

---

## 📋 Example 6: Uganda Payment (UGX)

```json
{
  "order_id": "ORDER-006",
  "amount": "100000.00",
  "currency": "UGX",
  "description": "Payment in Ugandan Shilling"
}
```

---

## 📋 Example 7: Rwanda Payment (RWF)

```json
{
  "order_id": "ORDER-007",
  "amount": "50000.00",
  "currency": "RWF",
  "description": "Payment in Rwandan Franc"
}
```

---

## 📋 Example 8: USD Payment

```json
{
  "order_id": "ORDER-008",
  "amount": "50.00",
  "currency": "USD",
  "description": "Payment in US Dollar"
}
```

---

## 📋 Example 9: Minimal Test Payment

```json
{
  "order_id": "ORDER-TEST-001",
  "amount": "1.00",
  "currency": "KES",
  "description": "Minimum test payment"
}
```

---

## ✅ Expected Response

When successful, you'll receive:

```json
{
  "id": "507f1f77bcf86cd799439011",
  "order_id": "ORDER-001",
  "amount": "100.00",
  "currency": "KES",
  "description": "Payment for KES 100",
  "status": "PENDING",
  "order_tracking_id": "abc123xyz",
  "redirect_url": "https://cybqa.pesapal.com/pesapalv3/redirect?orderTrackingId=abc123xyz",
  "payment_method": null,
  "confirmation_code": null,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

## 🔗 Other Endpoints

### GET Payment Details
```
GET /payments/ORDER-001
```

### Check Payment Status
```
GET /payments/ORDER-001/status
```

### List All Payments
```
GET /payments/?skip=0&limit=10
```

### List by Status
```
GET /payments/?status_filter=COMPLETED&skip=0&limit=10
```

---

## 📝 Notes

- **Order ID**: Must be unique for each payment
- **Amount**: Must be a string with 2 decimal places (e.g., "100.00")
- **Currency**: Must be uppercase (KES, TZS, UGX, RWF, USD)
- **Description**: Max 100 characters
- **Customer & Billing**: Optional but recommended

---

## 🧪 cURL Examples

### Create Payment
```bash
curl -X POST 'http://localhost:8000/payments/' \
  -H 'Content-Type: application/json' \
  -d '{
    "order_id": "ORDER-TEST-001",
    "amount": "100.00",
    "currency": "KES",
    "description": "Test payment"
  }'
```

### Get Payment
```bash
curl -X GET 'http://localhost:8000/payments/ORDER-TEST-001'
```

### Check Status
```bash
curl -X GET 'http://localhost:8000/payments/ORDER-TEST-001/status'
```


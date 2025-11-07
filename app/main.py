import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns welcome message"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Welcome to SDK Payments API"}


class TestHealthCheck:
    """Tests for the health check endpoint"""
    
    def test_health_check(self):
        """Test health check endpoint returns healthy status"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestGetPayments:
    """Tests for getting all payments"""
    
    def test_get_payments_empty(self):
        """Test getting payments when none exist"""
        response = client.get("/api/v1/payments")
        assert response.status_code == 200
        assert "payments" in response.json()
        assert response.json()["payments"] == []


class TestCreatePayment:
    """Tests for creating payments"""
    
    def test_create_payment_success(self):
        """Test creating a payment successfully"""
        payment_data = {
            "amount": 100.00,
            "currency": "USD",
            "description": "Test payment"
        }
        response = client.post("/api/v1/payments", json=payment_data)
        assert response.status_code == 200
        assert response.json()["message"] == "Payment created"
        assert "payment" in response.json()
        assert response.json()["payment"] == payment_data
    
    def test_create_payment_with_minimal_data(self):
        """Test creating a payment with minimal data"""
        payment_data = {"amount": 50.00}
        response = client.post("/api/v1/payments", json=payment_data)
        assert response.status_code == 200
        assert response.json()["message"] == "Payment created"


class TestGetPayment:
    """Tests for getting a specific payment"""
    
    def test_get_payment_by_id(self):
        """Test getting a payment by ID"""
        payment_id = 1
        response = client.get(f"/api/v1/payments/{payment_id}")
        assert response.status_code == 200
        assert response.json()["payment_id"] == payment_id
        assert "status" in response.json()
    
    def test_get_payment_different_ids(self):
        """Test getting payments with different IDs"""
        for payment_id in [1, 2, 100, 999]:
            response = client.get(f"/api/v1/payments/{payment_id}")
            assert response.status_code == 200
            assert response.json()["payment_id"] == payment_id


class TestUpdatePayment:
    """Tests for updating payments"""
    
    def test_update_payment_success(self):
        """Test updating a payment successfully"""
        payment_id = 1
        payment_data = {
            "amount": 200.00,
            "currency": "EUR",
            "status": "completed"
        }
        response = client.put(f"/api/v1/payments/{payment_id}", json=payment_data)
        assert response.status_code == 200
        assert response.json()["message"] == "Payment updated"
        assert response.json()["payment_id"] == payment_id
        assert response.json()["payment"] == payment_data
    
    def test_update_payment_partial_data(self):
        """Test updating a payment with partial data"""
        payment_id = 2
        payment_data = {"status": "cancelled"}
        response = client.put(f"/api/v1/payments/{payment_id}", json=payment_data)
        assert response.status_code == 200
        assert response.json()["payment_id"] == payment_id


class TestDeletePayment:
    """Tests for deleting payments"""
    
    def test_delete_payment_success(self):
        """Test deleting a payment successfully"""
        payment_id = 1
        response = client.delete(f"/api/v1/payments/{payment_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Payment deleted"
        assert response.json()["payment_id"] == payment_id
    
    def test_delete_payment_different_ids(self):
        """Test deleting payments with different IDs"""
        for payment_id in [1, 5, 10]:
            response = client.delete(f"/api/v1/payments/{payment_id}")
            assert response.status_code == 200
            assert response.json()["payment_id"] == payment_id


class TestAPIIntegration:
    """Integration tests for the API"""
    
    def test_full_payment_lifecycle(self):
        """Test complete payment lifecycle: create, get, update, delete"""
        # Create payment
        payment_data = {
            "amount": 150.00,
            "currency": "USD",
            "description": "Integration test payment"
        }
        create_response = client.post("/api/v1/payments", json=payment_data)
        assert create_response.status_code == 200
        
        # Get payment
        payment_id = 1
        get_response = client.get(f"/api/v1/payments/{payment_id}")
        assert get_response.status_code == 200
        
        # Update payment
        update_data = {"status": "completed"}
        update_response = client.put(f"/api/v1/payments/{payment_id}", json=update_data)
        assert update_response.status_code == 200
        
        # Delete payment
        delete_response = client.delete(f"/api/v1/payments/{payment_id}")
        assert delete_response.status_code == 200
    
    def test_api_endpoints_exist(self):
        """Test that all API endpoints are accessible"""
        endpoints = [
            ("/", "GET"),
            ("/health", "GET"),
            ("/api/v1/payments", "GET"),
            ("/api/v1/payments", "POST"),
            ("/api/v1/payments/1", "GET"),
            ("/api/v1/payments/1", "PUT"),
            ("/api/v1/payments/1", "DELETE"),
        ]
        
        for endpoint, method in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json={})
            elif method == "PUT":
                response = client.put(endpoint, json={})
            elif method == "DELETE":
                response = client.delete(endpoint)
            
            # All endpoints should return 200 (not 404)
            assert response.status_code != 404, f"Endpoint {method} {endpoint} not found"


class TestErrorHandling:
    """Tests for error handling"""
    
    def test_invalid_json_payload(self):
        """Test handling of invalid JSON payload"""
        response = client.post(
            "/api/v1/payments",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        # Should handle gracefully (either 400 or 422)
        assert response.status_code in [400, 422]
    
    def test_missing_content_type(self):
        """Test handling of missing content type"""
        response = client.post("/api/v1/payments", data="some data")
        # Should handle gracefully
        assert response.status_code in [200, 400, 422]


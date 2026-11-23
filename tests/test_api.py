import sys
from pathlib import Path

# Add root folder to python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app.main import app

def run_test():
    client = TestClient(app)
    
    print("Testing API Health endpoint...")
    response = client.get("/health")
    assert response.status_code == 200, "Health endpoint failed."
    assert response.json().get("status") == "ok", "Health status payload invalid."
    print("API Health passed.")
    
    print("\nTesting API Ready endpoint...")
    response = client.get("/ready")
    assert response.status_code == 200, "Ready endpoint failed."
    assert response.json().get("status") == "ready", "Ready status payload invalid."
    print("API Ready passed.")

    print("\nTesting Authentication endpoints...")
    # Register test user
    reg_payload = {"username": "testuser_docker", "password": "password123"}
    reg_resp = client.post("/auth/register", json=reg_payload)
    assert reg_resp.status_code in [201, 409], f"Register failed: {reg_resp.text}"

    # Login to obtain JWT
    login_resp = client.post(
        "/auth/login",
        data={"username": reg_payload["username"], "password": reg_payload["password"]},
    )
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token = login_resp.json().get("access_token")
    assert token, "No access token returned from login."
    auth_headers = {"Authorization": f"Bearer {token}"}
    print("Authentication passed (registered & obtained JWT).")

    print("\nTesting unauthenticated access rejection (401)...")
    unauth_resp = client.get("/trace/empty_session_123")
    assert unauth_resp.status_code == 401, "Expected 401 for unauthenticated request."
    print("Unauthenticated rejection passed.")
    
    print("\nTesting trace retrieval for non-existent session (authenticated)...")
    response = client.get("/trace/empty_session_123", headers=auth_headers)
    assert response.status_code == 200, f"Trace failed: {response.status_code}"
    assert response.json() == [], f"Unexpected trace payload: {response.json()}"
    print("Trace endpoint passed.")
    
    print("\nTesting download Markdown error handling for invalid ID (authenticated)...")
    response = client.get("/download/invalid_id_000", headers=auth_headers)
    assert response.status_code == 404, "Invalid ID did not throw 404."
    print("Markdown download error handling passed.")
    
    print("\nAll integration API tests passed successfully!")

if __name__ == "__main__":
    run_test()

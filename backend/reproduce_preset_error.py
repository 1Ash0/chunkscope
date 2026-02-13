import httpx
import asyncio
import sys

async def reproduce():
    preset_id = "31438150-1405-43dc-9f4c-dcd9db0f9ff1" # Chatbot with Memory
    url = f"http://localhost:8001/api/v1/presets/{preset_id}/apply"
    
    # We need to simulate being the user b478684d-6360-4d1b-881d-7b86c2c7da23
    # In presets.py:
    # current_user: CurrentUser = Depends(get_current_user)
    
    # Since I don't have a valid JWT easily without logging in, 
    # and I added a 403 error for missing user in presets.py,
    # I should probably just use the actual credentials or bypass it if I can.
    
    # Wait, I can just use the registration/login logic to get a token.
    auth_url = "http://localhost:8001/api/v1/auth/login"
    login_data = {
        "username": "uploadtest@test.com", # Email is used as username in many RAG systems if configured so
        "password": "password123" # I should check what the password is or just register a new one
    }
    
    print(f"Applying preset: {preset_id}")
    
    # But wait, if I use the user ID directly in a test script, I can just mock the dependency in a test.
    # For now, let's try to see if a simple POST (even if it fails with 401/403) at least reaches the server.
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Request Error: {e}")

if __name__ == "__main__":
    asyncio.run(reproduce())

#!/usr/bin/env python3
"""
Debug validation failure for single plate connection
"""

import requests
import json

BACKEND_URL = "https://dash-troubleshoot-1.preview.emergentagent.com/api"

def debug_validation():
    # First register and login
    user_data = {
        "email": "debug_test@example.com",
        "password": "DebugPass123!",
        "full_name": "Debug Test User",
        "company": "Debug Test Co."
    }
    
    # Register
    response = requests.post(f"{BACKEND_URL}/auth/register", json=user_data)
    if response.status_code != 200:
        print(f"Registration failed: {response.text}")
        return
    
    # Login
    login_data = {"email": user_data["email"], "password": user_data["password"]}
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create project
    project_data = {
        "name": "Debug Project",
        "description": "Debug validation test",
        "location": "Test Location"
    }
    response = requests.post(f"{BACKEND_URL}/projects/", json=project_data, headers=headers)
    if response.status_code != 200:
        print(f"Project creation failed: {response.text}")
        return
    
    project_id = response.json()["id"]
    
    # Create connection with proper parameters for single_plate
    connection_data = {
        "name": "Debug Single Plate Connection",
        "connection_type": "single_plate",
        "project_id": project_id,
        "description": "Debug single plate connection",
        "parameters": {
            "num_bolts": 4,
            "bolt_diameter": 0.75,
            "bolt_spacing": 3.0,
            "edge_distance": 1.5,
            "plate_thickness": 0.375,
            "plate_width": 6.0,
            "plate_grade": "A36",
            "bolt_grade": "A325",
            "beam_depth": 24,
            "connection_depth": 10.0,
            "plate_length": 12.0  # Add this parameter
        }
    }
    
    response = requests.post(f"{BACKEND_URL}/connections/", json=connection_data, headers=headers)
    if response.status_code != 200:
        print(f"Connection creation failed: {response.text}")
        return
    
    connection_id = response.json()["id"]
    print(f"Created connection: {connection_id}")
    
    # Validate connection
    response = requests.post(f"{BACKEND_URL}/connections/{connection_id}/validate", headers=headers)
    print(f"Validation response status: {response.status_code}")
    print(f"Validation response: {json.dumps(response.json(), indent=2)}")
    
    # Try to export
    response = requests.post(f"{BACKEND_URL}/connections/{connection_id}/export/tekla", headers=headers)
    print(f"Export response status: {response.status_code}")
    print(f"Export response: {response.text}")
    
    # Cleanup
    requests.delete(f"{BACKEND_URL}/connections/{connection_id}", headers=headers)
    requests.delete(f"{BACKEND_URL}/projects/{project_id}", headers=headers)

if __name__ == "__main__":
    debug_validation()
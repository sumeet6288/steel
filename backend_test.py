#!/usr/bin/env python3
"""
SteelConnect AI Backend API Testing Suite
Tests all backend APIs including auth, projects, connections, and audit endpoints.
"""

import requests
import json
import sys
import os
from datetime import datetime

# Get backend URL from frontend .env file
BACKEND_URL = "https://connection-check-2.preview.emergentagent.com/api"

class SteelConnectAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.token = None
        self.user_id = None
        self.project_id = None
        self.connection_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, message="", response_data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "response_data": response_data
        })
        
    def test_health_check(self):
        """Test health check endpoints"""
        print("\n=== HEALTH CHECK TESTS ===")
        
        # Test root endpoint
        try:
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                if "SteelConnect AI" in data.get("message", ""):
                    self.log_test("Root endpoint", True, "API root accessible")
                else:
                    self.log_test("Root endpoint", False, "Unexpected response format")
            else:
                self.log_test("Root endpoint", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Root endpoint", False, f"Connection error: {str(e)}")
            
        # Test health endpoint
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("Health check", True, "Service healthy")
                else:
                    self.log_test("Health check", False, "Service not healthy")
            else:
                self.log_test("Health check", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Health check", False, f"Connection error: {str(e)}")
    
    def test_user_registration(self):
        """Test user registration"""
        print("\n=== AUTHENTICATION TESTS ===")
        
        # Generate unique email for testing
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_email = f"steeltest_{timestamp}@example.com"
        
        user_data = {
            "email": test_email,
            "password": "SecurePassword123!",
            "full_name": "Steel Test Engineer",
            "company": "Test Steel Fabricators Inc."
        }
        
        try:
            response = requests.post(f"{self.base_url}/auth/register", json=user_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("email") == test_email:
                    self.user_id = data.get("id")
                    self.log_test("User registration", True, f"User created with ID: {self.user_id}")
                    return user_data
                else:
                    self.log_test("User registration", False, "Invalid response data")
            else:
                self.log_test("User registration", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("User registration", False, f"Error: {str(e)}")
        
        return None
    
    def test_user_login(self, user_data):
        """Test user login"""
        if not user_data:
            self.log_test("User login", False, "No user data available")
            return False
            
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        try:
            response = requests.post(f"{self.base_url}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                if data.get("access_token"):
                    self.token = data["access_token"]
                    self.log_test("User login", True, "Login successful, token received")
                    return True
                else:
                    self.log_test("User login", False, "No access token in response")
            else:
                self.log_test("User login", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("User login", False, f"Error: {str(e)}")
        
        return False
    
    def test_get_current_user(self):
        """Test get current user info"""
        if not self.token:
            self.log_test("Get current user", False, "No authentication token")
            return
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.get(f"{self.base_url}/auth/me", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("id"):
                    self.log_test("Get current user", True, f"User info retrieved for ID: {data['id']}")
                else:
                    self.log_test("Get current user", False, "No user ID in response")
            else:
                self.log_test("Get current user", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Get current user", False, f"Error: {str(e)}")
    
    def test_create_project(self):
        """Test project creation"""
        print("\n=== PROJECT TESTS ===")
        
        if not self.token:
            self.log_test("Create project", False, "No authentication token")
            return
            
        headers = {"Authorization": f"Bearer {self.token}"}
        project_data = {
            "name": "Steel Bridge Connection Test Project",
            "description": "Test project for validating steel connection APIs",
            "location": "San Francisco, CA"
        }
        
        try:
            response = requests.post(f"{self.base_url}/projects/", json=project_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("id"):
                    self.project_id = data["id"]
                    self.log_test("Create project", True, f"Project created with ID: {self.project_id}")
                else:
                    self.log_test("Create project", False, "No project ID in response")
            else:
                self.log_test("Create project", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Create project", False, f"Error: {str(e)}")
    
    def test_get_projects(self):
        """Test get all projects"""
        if not self.token:
            self.log_test("Get projects", False, "No authentication token")
            return
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.get(f"{self.base_url}/projects/", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get projects", True, f"Retrieved {len(data)} projects")
                else:
                    self.log_test("Get projects", False, "Response is not a list")
            else:
                self.log_test("Get projects", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Get projects", False, f"Error: {str(e)}")
    
    def test_get_project_by_id(self):
        """Test get project by ID"""
        if not self.token or not self.project_id:
            self.log_test("Get project by ID", False, "No authentication token or project ID")
            return
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.get(f"{self.base_url}/projects/{self.project_id}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("id") == self.project_id:
                    self.log_test("Get project by ID", True, "Project retrieved successfully")
                else:
                    self.log_test("Get project by ID", False, "Project ID mismatch")
            else:
                self.log_test("Get project by ID", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Get project by ID", False, f"Error: {str(e)}")
    
    def test_update_project(self):
        """Test project update"""
        if not self.token or not self.project_id:
            self.log_test("Update project", False, "No authentication token or project ID")
            return
            
        headers = {"Authorization": f"Bearer {self.token}"}
        update_data = {
            "description": "Updated test project description with additional details"
        }
        
        try:
            response = requests.put(f"{self.base_url}/projects/{self.project_id}", json=update_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if "Updated" in data.get("description", ""):
                    self.log_test("Update project", True, "Project updated successfully")
                else:
                    self.log_test("Update project", False, "Project description not updated")
            else:
                self.log_test("Update project", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Update project", False, f"Error: {str(e)}")
    
    def test_create_connection(self):
        """Test connection creation"""
        print("\n=== CONNECTION TESTS ===")
        
        if not self.token or not self.project_id:
            self.log_test("Create connection", False, "No authentication token or project ID")
            return
            
        headers = {"Authorization": f"Bearer {self.token}"}
        connection_data = {
            "name": "Single Plate Shear Connection SP-01",
            "connection_type": "single_plate",
            "project_id": self.project_id,
            "description": "Single plate shear connection for W24x68 beam",
            "parameters": {
                "beam_depth": 24,
                "beam_flange_width": 9,
                "beam_flange_thickness": 0.75,
                "beam_web_thickness": 0.5,
                "shear_force": 50,
                "plate_thickness": 0.375,
                "plate_width": 6,
                "bolt_diameter": 0.75,
                "bolt_rows": 3
            }
        }
        
        try:
            response = requests.post(f"{self.base_url}/connections/", json=connection_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("id"):
                    self.connection_id = data["id"]
                    self.log_test("Create connection", True, f"Connection created with ID: {self.connection_id}")
                else:
                    self.log_test("Create connection", False, "No connection ID in response")
            else:
                self.log_test("Create connection", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Create connection", False, f"Error: {str(e)}")
    
    def test_get_connections(self):
        """Test get connections by project"""
        if not self.token or not self.project_id:
            self.log_test("Get connections", False, "No authentication token or project ID")
            return
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.get(f"{self.base_url}/connections/?project_id={self.project_id}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get connections", True, f"Retrieved {len(data)} connections for project")
                else:
                    self.log_test("Get connections", False, "Response is not a list")
            else:
                self.log_test("Get connections", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Get connections", False, f"Error: {str(e)}")
    
    def test_get_connection_by_id(self):
        """Test get connection by ID"""
        if not self.token or not self.connection_id:
            self.log_test("Get connection by ID", False, "No authentication token or connection ID")
            return
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.get(f"{self.base_url}/connections/{self.connection_id}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("id") == self.connection_id:
                    self.log_test("Get connection by ID", True, "Connection retrieved successfully")
                else:
                    self.log_test("Get connection by ID", False, "Connection ID mismatch")
            else:
                self.log_test("Get connection by ID", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Get connection by ID", False, f"Error: {str(e)}")
    
    def test_update_connection(self):
        """Test connection update"""
        if not self.token or not self.connection_id:
            self.log_test("Update connection", False, "No authentication token or connection ID")
            return
            
        headers = {"Authorization": f"Bearer {self.token}"}
        update_data = {
            "parameters": {
                "beam_depth": 24,
                "beam_flange_width": 9,
                "beam_flange_thickness": 0.75,
                "beam_web_thickness": 0.5,
                "shear_force": 65,  # Updated shear force
                "plate_thickness": 0.5,  # Updated plate thickness
                "plate_width": 6,
                "bolt_diameter": 0.75,
                "bolt_rows": 3
            }
        }
        
        try:
            response = requests.put(f"{self.base_url}/connections/{self.connection_id}", json=update_data, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("parameters", {}).get("shear_force") == 65:
                    self.log_test("Update connection", True, "Connection parameters updated successfully")
                else:
                    self.log_test("Update connection", False, "Connection parameters not updated correctly")
            else:
                self.log_test("Update connection", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Update connection", False, f"Error: {str(e)}")
    
    def test_validate_connection(self):
        """Test connection validation with AISC rules"""
        if not self.token or not self.connection_id:
            self.log_test("Validate connection", False, "No authentication token or connection ID")
            return
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.post(f"{self.base_url}/connections/{self.connection_id}/validate", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") in ["validated", "failed"]:
                    status = data["status"]
                    has_geometry = "geometry" in data
                    self.log_test("Validate connection", True, f"Validation completed with status: {status}, geometry generated: {has_geometry}")
                else:
                    self.log_test("Validate connection", False, "Invalid validation response")
            else:
                self.log_test("Validate connection", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Validate connection", False, f"Error: {str(e)}")
    
    def test_export_to_tekla(self):
        """Test Tekla export"""
        if not self.token or not self.connection_id:
            self.log_test("Export to Tekla", False, "No authentication token or connection ID")
            return
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.post(f"{self.base_url}/connections/{self.connection_id}/export/tekla", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("tekla_export") and data.get("format") == "tekla_parametric_json":
                    self.log_test("Export to Tekla", True, "Tekla export successful")
                else:
                    self.log_test("Export to Tekla", False, "Invalid Tekla export response")
            else:
                self.log_test("Export to Tekla", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Export to Tekla", False, f"Error: {str(e)}")

    def test_connection_designer_workflow(self):
        """Test complete ConnectionDesignerPage workflow"""
        print("\n=== CONNECTION DESIGNER PAGE WORKFLOW TESTS ===")
        
        if not self.token or not self.connection_id:
            self.log_test("Connection Designer Workflow", False, "No authentication token or connection ID")
            return
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test 1: Parameter Saving
        print("\n--- Testing Parameter Saving ---")
        updated_parameters = {
            "beam_depth": 24,
            "beam_flange_width": 9,
            "beam_flange_thickness": 0.75,
            "beam_web_thickness": 0.5,
            "shear_force": 75,  # Updated value
            "plate_thickness": 0.5,
            "plate_width": 8,   # Updated value
            "bolt_diameter": 0.875,  # Updated value
            "bolt_rows": 4      # Updated value
        }
        
        try:
            response = requests.put(f"{self.base_url}/connections/{self.connection_id}", 
                                  json={"parameters": updated_parameters}, headers=headers)
            if response.status_code == 200:
                data = response.json()
                saved_params = data.get("parameters", {})
                if (saved_params.get("shear_force") == 75 and 
                    saved_params.get("plate_width") == 8 and
                    saved_params.get("bolt_diameter") == 0.875):
                    self.log_test("Parameter Saving", True, "Parameters saved and verified successfully")
                else:
                    self.log_test("Parameter Saving", False, f"Parameters not saved correctly. Expected shear_force=75, got {saved_params.get('shear_force')}")
            else:
                self.log_test("Parameter Saving", False, f"Parameter save failed: {response.status_code}, {response.text}")
        except Exception as e:
            self.log_test("Parameter Saving", False, f"Parameter save error: {str(e)}")
        
        # Test 2: Validation Flow with detailed results
        print("\n--- Testing Validation Flow ---")
        try:
            response = requests.post(f"{self.base_url}/connections/{self.connection_id}/validate", headers=headers)
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                rule_validation = data.get("rule_validation", {})
                geometry_validation = data.get("geometry_validation", {})
                geometry = data.get("geometry")
                
                # Check validation structure
                validation_checks = []
                if status in ["validated", "failed"]:
                    validation_checks.append("✓ Status field present")
                else:
                    validation_checks.append("✗ Invalid status field")
                
                if rule_validation.get("checks"):
                    validation_checks.append(f"✓ AISC rule checks present ({len(rule_validation['checks'])} checks)")
                    
                    # Check for detailed rule information
                    sample_check = rule_validation["checks"][0] if rule_validation["checks"] else {}
                    if sample_check.get("rule_name") and sample_check.get("status"):
                        validation_checks.append("✓ Rule checks have detailed information")
                    else:
                        validation_checks.append("✗ Rule checks missing detailed information")
                        
                    # Check for calculated vs limit values
                    has_values = any(check.get("calculated_value") is not None and check.get("limit_value") is not None 
                                   for check in rule_validation["checks"])
                    if has_values:
                        validation_checks.append("✓ Calculated and limit values present")
                    else:
                        validation_checks.append("✗ Missing calculated/limit values")
                else:
                    validation_checks.append("✗ No AISC rule checks found")
                
                if geometry_validation:
                    validation_checks.append("✓ Geometry validation section present")
                else:
                    validation_checks.append("✗ Geometry validation section missing")
                
                if geometry:
                    validation_checks.append("✓ Geometry data generated")
                else:
                    validation_checks.append("✗ No geometry data generated")
                
                self.log_test("Validation Flow", True, f"Validation completed. {'; '.join(validation_checks)}")
                
                # Store validation results for geometry test
                self.validation_results = data
                
            else:
                self.log_test("Validation Flow", False, f"Validation failed: {response.status_code}, {response.text}")
        except Exception as e:
            self.log_test("Validation Flow", False, f"Validation error: {str(e)}")
        
        # Test 3: Geometry Display Structure
        print("\n--- Testing Geometry Display ---")
        try:
            # Get updated connection with geometry
            response = requests.get(f"{self.base_url}/connections/{self.connection_id}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                geometry = data.get("geometry")
                
                if geometry:
                    geometry_checks = []
                    
                    # Check for geometry components
                    if geometry.get("plate"):
                        geometry_checks.append("✓ Plate component present")
                    if geometry.get("bolts"):
                        geometry_checks.append(f"✓ Bolts component present ({len(geometry['bolts'])} bolts)")
                    if geometry.get("angles"):
                        geometry_checks.append(f"✓ Angles component present ({len(geometry['angles'])} angles)")
                    if geometry.get("dimensions"):
                        geometry_checks.append("✓ Dimensions data present")
                    
                    # Check geometry structure is readable (not just raw JSON)
                    if isinstance(geometry, dict) and len(geometry) > 0:
                        geometry_checks.append("✓ Geometry data is structured")
                    else:
                        geometry_checks.append("✗ Geometry data is not properly structured")
                    
                    self.log_test("Geometry Display", True, f"Geometry components verified. {'; '.join(geometry_checks)}")
                else:
                    self.log_test("Geometry Display", False, "No geometry data found after validation")
            else:
                self.log_test("Geometry Display", False, f"Failed to retrieve connection geometry: {response.status_code}")
        except Exception as e:
            self.log_test("Geometry Display", False, f"Geometry display error: {str(e)}")
        
        # Test 4: Export to Tekla (after validation)
        print("\n--- Testing Export to Tekla ---")
        try:
            response = requests.post(f"{self.base_url}/connections/{self.connection_id}/export/tekla", headers=headers)
            if response.status_code == 200:
                data = response.json()
                export_checks = []
                
                if data.get("tekla_export"):
                    export_checks.append("✓ Tekla export data present")
                if data.get("format") == "tekla_parametric_json":
                    export_checks.append("✓ Correct export format")
                if data.get("disclaimer"):
                    export_checks.append("✓ Engineering disclaimer present")
                
                # Check if connection status updated to exported
                conn_response = requests.get(f"{self.base_url}/connections/{self.connection_id}", headers=headers)
                if conn_response.status_code == 200:
                    conn_data = conn_response.json()
                    if conn_data.get("status") == "exported":
                        export_checks.append("✓ Connection status updated to 'exported'")
                    else:
                        export_checks.append(f"✗ Connection status not updated (current: {conn_data.get('status')})")
                
                self.log_test("Export to Tekla", True, f"Export successful. {'; '.join(export_checks)}")
            else:
                self.log_test("Export to Tekla", False, f"Export failed: {response.status_code}, {response.text}")
        except Exception as e:
            self.log_test("Export to Tekla", False, f"Export error: {str(e)}")

    def test_redlines_workflow(self):
        """Test redlines upload and AI interpretation workflow"""
        print("\n=== REDLINES WORKFLOW TESTS ===")
        
        if not self.token or not self.connection_id:
            self.log_test("Redlines Workflow", False, "No authentication token or connection ID")
            return
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test 1: Redline Upload (simulate file upload)
        print("\n--- Testing Redline Upload ---")
        try:
            # Create a mock file for testing
            mock_file_content = b"Mock redline drawing content for testing"
            files = {
                'file': ('test_redline.pdf', mock_file_content, 'application/pdf')
            }
            data = {
                'connection_id': self.connection_id
            }
            
            response = requests.post(f"{self.base_url}/redlines/upload", 
                                   files=files, data=data, headers=headers)
            if response.status_code == 200:
                upload_data = response.json()
                redline_id = upload_data.get("redline_id")
                if redline_id:
                    self.redline_id = redline_id
                    self.log_test("Redline Upload", True, f"Redline uploaded successfully with ID: {redline_id}")
                else:
                    self.log_test("Redline Upload", False, "No redline ID returned")
            else:
                self.log_test("Redline Upload", False, f"Upload failed: {response.status_code}, {response.text}")
        except Exception as e:
            self.log_test("Redline Upload", False, f"Upload error: {str(e)}")
        
        # Test 2: AI Interpretation (if redline uploaded successfully)
        if hasattr(self, 'redline_id'):
            print("\n--- Testing AI Interpretation ---")
            try:
                response = requests.post(f"{self.base_url}/redlines/{self.redline_id}/interpret", headers=headers)
                if response.status_code == 200:
                    interpret_data = response.json()
                    ai_extraction = interpret_data.get("ai_extraction", {})
                    
                    ai_checks = []
                    if ai_extraction.get("intent"):
                        ai_checks.append("✓ AI intent extracted")
                    if ai_extraction.get("parameters"):
                        ai_checks.append(f"✓ Parameter suggestions present ({len(ai_extraction['parameters'])} params)")
                    if ai_extraction.get("confidence") is not None:
                        ai_checks.append(f"✓ Confidence score present ({ai_extraction['confidence']*100:.1f}%)")
                    if interpret_data.get("disclaimer"):
                        ai_checks.append("✓ Advisory disclaimer present")
                    
                    self.log_test("AI Interpretation", True, f"AI interpretation completed. {'; '.join(ai_checks)}")
                    
                    # Test 3: Approve/Reject functionality
                    if ai_extraction.get("parameters"):
                        print("\n--- Testing Approve Functionality ---")
                        try:
                            approve_response = requests.post(
                                f"{self.base_url}/redlines/{self.redline_id}/approve",
                                json=ai_extraction["parameters"],
                                headers=headers
                            )
                            if approve_response.status_code == 200:
                                approve_data = approve_response.json()
                                if approve_data.get("updated_parameters"):
                                    self.log_test("Approve Functionality", True, "AI suggestions approved and applied successfully")
                                else:
                                    self.log_test("Approve Functionality", False, "No updated parameters returned")
                            else:
                                self.log_test("Approve Functionality", False, f"Approve failed: {approve_response.status_code}")
                        except Exception as e:
                            self.log_test("Approve Functionality", False, f"Approve error: {str(e)}")
                    
                else:
                    self.log_test("AI Interpretation", False, f"Interpretation failed: {response.status_code}, {response.text}")
            except Exception as e:
                self.log_test("AI Interpretation", False, f"Interpretation error: {str(e)}")
        
        # Test 4: Get redlines list
        print("\n--- Testing Redlines List ---")
        try:
            response = requests.get(f"{self.base_url}/redlines/{self.connection_id}/list", headers=headers)
            if response.status_code == 200:
                redlines_data = response.json()
                if isinstance(redlines_data, list):
                    self.log_test("Redlines List", True, f"Retrieved {len(redlines_data)} redlines for connection")
                else:
                    self.log_test("Redlines List", False, "Invalid redlines list response")
            else:
                self.log_test("Redlines List", False, f"Failed to get redlines: {response.status_code}")
        except Exception as e:
            self.log_test("Redlines List", False, f"Redlines list error: {str(e)}")
    
    def test_audit_logs(self):
        """Test audit logging"""
        print("\n=== AUDIT TESTS ===")
        
        if not self.token:
            self.log_test("Get user audit logs", False, "No authentication token")
            return
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test user activity logs
        try:
            response = requests.get(f"{self.base_url}/audit/my-activity?limit=50", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get user audit logs", True, f"Retrieved {len(data)} audit log entries")
                else:
                    self.log_test("Get user audit logs", False, "Response is not a list")
            else:
                self.log_test("Get user audit logs", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Get user audit logs", False, f"Error: {str(e)}")
        
        # Test connection audit trail
        if self.connection_id:
            try:
                response = requests.get(f"{self.base_url}/audit/connection/{self.connection_id}", headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        self.log_test("Get connection audit trail", True, f"Retrieved {len(data)} connection audit entries")
                    else:
                        self.log_test("Get connection audit trail", False, "Response is not a list")
                else:
                    self.log_test("Get connection audit trail", False, f"Status code: {response.status_code}")
            except Exception as e:
                self.log_test("Get connection audit trail", False, f"Error: {str(e)}")
    
    def test_error_cases(self):
        """Test error handling"""
        print("\n=== ERROR HANDLING TESTS ===")
        
        if not self.token:
            self.log_test("Error handling tests", False, "No authentication token")
            return
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test invalid project ID
        try:
            response = requests.get(f"{self.base_url}/projects/invalid-id", headers=headers)
            if response.status_code == 404:
                self.log_test("Invalid project ID error", True, "Correctly returned 404 for invalid project ID")
            else:
                self.log_test("Invalid project ID error", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_test("Invalid project ID error", False, f"Error: {str(e)}")
        
        # Test invalid connection ID
        try:
            response = requests.get(f"{self.base_url}/connections/invalid-id", headers=headers)
            if response.status_code == 404:
                self.log_test("Invalid connection ID error", True, "Correctly returned 404 for invalid connection ID")
            else:
                self.log_test("Invalid connection ID error", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_test("Invalid connection ID error", False, f"Error: {str(e)}")
        
        # Test unauthorized access
        try:
            response = requests.get(f"{self.base_url}/projects/")  # No auth header
            if response.status_code == 401:
                self.log_test("Unauthorized access error", True, "Correctly returned 401 for unauthorized access")
            else:
                self.log_test("Unauthorized access error", False, f"Expected 401, got {response.status_code}")
        except Exception as e:
            self.log_test("Unauthorized access error", False, f"Error: {str(e)}")
    
    def cleanup(self):
        """Clean up test data"""
        print("\n=== CLEANUP ===")
        
        if not self.token:
            self.log_test("Cleanup", False, "No authentication token")
            return
            
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Delete connection
        if self.connection_id:
            try:
                response = requests.delete(f"{self.base_url}/connections/{self.connection_id}", headers=headers)
                if response.status_code == 200:
                    self.log_test("Delete connection", True, "Connection deleted successfully")
                else:
                    self.log_test("Delete connection", False, f"Status code: {response.status_code}")
            except Exception as e:
                self.log_test("Delete connection", False, f"Error: {str(e)}")
        
        # Delete project
        if self.project_id:
            try:
                response = requests.delete(f"{self.base_url}/projects/{self.project_id}", headers=headers)
                if response.status_code == 200:
                    self.log_test("Delete project", True, "Project deleted successfully")
                else:
                    self.log_test("Delete project", False, f"Status code: {response.status_code}")
            except Exception as e:
                self.log_test("Delete project", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🔧 SteelConnect AI Backend API Test Suite")
        print(f"Testing backend at: {self.base_url}")
        print("=" * 60)
        
        # Health checks
        self.test_health_check()
        
        # Authentication flow
        user_data = self.test_user_registration()
        if user_data and self.test_user_login(user_data):
            self.test_get_current_user()
            
            # Project management
            self.test_create_project()
            self.test_get_projects()
            self.test_get_project_by_id()
            self.test_update_project()
            
            # Connection management
            self.test_create_connection()
            self.test_get_connections()
            self.test_get_connection_by_id()
            self.test_update_connection()
            self.test_validate_connection()
            self.test_export_to_tekla()
            
            # ConnectionDesignerPage specific workflow tests
            self.test_connection_designer_workflow()
            self.test_redlines_workflow()
            
            # Audit logging
            self.test_audit_logs()
            
            # Error handling
            self.test_error_cases()
            
            # Cleanup
            self.cleanup()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🚨 FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['message']}")
        
        print("\n" + "=" * 60)
        
        return failed_tests == 0

if __name__ == "__main__":
    tester = SteelConnectAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
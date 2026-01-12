import requests
import json

class APIDiscoveryAgent:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        
    def discover_endpoints(self):
        # Get OpenAPI spec
        try:
            response = requests.get(f"{self.base_url}/openapi.json")
            return response.json()
        except:
            return None
    
    def validate_endpoint(self, endpoint, method, payload=None):
        """Test if endpoint actually works as expected"""
        try:
            if payload is None:
                payload = {"name": "Test", "age": 25}  # Valid payload for /users
            response = requests.request(method, f"{self.base_url}{endpoint}", json=payload)
            return {
                "status": response.status_code,
                "response": response.json() if response.content else None,
                "working": response.status_code < 400
            }
        except Exception as e:
            return {"error": str(e), "working": False}
    
    def auto_discover_schema_issues(self):
        """Compare OpenAPI spec with actual API behavior"""
        spec = self.discover_endpoints()
        issues = []
        
        for path, methods in spec.get("paths", {}).items():
            for method, details in methods.items():
                # Test with empty payload
                result = self.validate_endpoint(path, method.upper(), {})
                
                if not result["working"]:
                    issues.append({
                        "endpoint": f"{method.upper()} {path}",
                        "issue": "Endpoint not working",
                        "details": result
                    })
        
        return issues
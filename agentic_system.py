from test_agent_new import TestAgent
from api_discovery import APIDiscoveryAgent
import json
import requests

class AgenticTestSystem:
    def __init__(self):
        self.test_agent = TestAgent()
        self.discovery_agent = APIDiscoveryAgent()
        self.knowledge_base = []
        
    def run_full_cycle(self):
        print("🔍 Discovering API...")
        issues = self.discovery_agent.auto_discover_schema_issues()
        
        if issues:
            print(f"⚠️  Found {len(issues)} API issues")
            self.fix_api_issues(issues)
        
        print("🧪 Generating and running tests...")
        self.test_agent.run_cycle()
        
        print("📊 Updating knowledge base...")
        self.update_knowledge()
    
    def fix_api_issues(self, issues):
        """Generate fixes for API issues"""
        for issue in issues:
            fix_prompt = f"Fix this API issue: {json.dumps(issue)}"

            
            response = requests.post("http://localhost:11434/api/generate",
                                   json={"model": "llama3", "prompt": fix_prompt, "stream": False})
            
            fix_suggestion = response.json()["response"]
            print(f"Issue: {issue['endpoint']} - {issue['issue']}")
            print(f"Suggested fix: {fix_suggestion[:200]}...")
    
    def update_knowledge(self):
        """Store learnings for future use"""
        self.knowledge_base.append({
            "timestamp": "now",
            "failed_tests": self.test_agent.failed_tests,
            "lessons": "API expects flat dict structure, not nested objects"
        })

if __name__ == "__main__":
    system = AgenticTestSystem()
    system.run_full_cycle()
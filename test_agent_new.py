import subprocess
import json
import requests
from parse_openapi import parse_openapi

class TestAgent:
    def __init__(self, api_url="http://localhost:8000", llm_url="http://localhost:11434"):
        self.api_url = api_url
        self.llm_url = llm_url
        self.failed_tests = []
        self.test_cases = []
        
    def generate_test_cases(self, schema):
        """Step 1: Generate test cases from schema"""
        prompt = f"""You are a senior QA automation engineer.

Given this API schema:
{json.dumps(schema, indent=2)}

Generate API test cases in STRICT JSON format.

Each test case must include:
- test_name
- payload
- expected_status

Rules:
- Output ONLY valid JSON
- Do NOT include explanations
- Do NOT include markdown
- Do NOT include comments"""
        
        response = requests.post(f"{self.llm_url}/api/generate",
                               json={"model": "llama3", "prompt": prompt, "stream": False})
        
        try:
            response_text = response.json()["response"]
            print(f"LLM response: {response_text[:200]}...")
            
            # Clean up markdown and explanations
            lines = response_text.split('\n')
            json_lines = []
            in_json = False
            
            for line in lines:
                if line.strip().startswith('[') or in_json:
                    in_json = True
                    json_lines.append(line)
                    if line.strip().endswith(']'):
                        break
            
            clean_json = '\n'.join(json_lines)
            test_cases = json.loads(clean_json)
            self.test_cases = test_cases
            return test_cases
        except Exception as e:
            print(f"❌ Failed to parse test cases: {e}")
            # Fallback test cases
      
    
    def generate_pytest_code(self, test_cases):
        """Step 2: Convert test cases to pytest code"""
        prompt = f"""Convert these test cases to pytest code:
{json.dumps(test_cases, indent=2)}

Rules:
- Import requests
- Use BASE_URL = "http://localhost:8000"
- Create complete pytest functions
- 
- Use the exact payload and expected_status from test cases
- Output ONLY Python code
- NO explanations or markdown"""
        
        response = requests.post(f"{self.llm_url}/api/generate",
                               json={"model": "llama3", "prompt": prompt, "stream": False})
        
        code = response.json()["response"]
        
        # Clean up markdown
        lines = code.split('\n')
        python_lines = []
        in_code = False
        
        for line in lines:
            if line.strip() == '```python' or line.strip() == '```':
                in_code = not in_code
                continue
            if in_code or (line.strip().startswith('import') or line.strip().startswith('def ') or line.strip().startswith('    ') or line.strip().startswith('BASE_URL')):
                python_lines.append(line)
        
        return '\n'.join(python_lines)
    
    def execute_tests(self, test_file="test_api.py"):
        """Step 3: Execute pytest and capture results"""
        result = subprocess.run(["python", "-m", "pytest", test_file, "-v"], 
                              capture_output=True, text=True)
        print(f"Test output: {result.stdout}")
        if result.stderr:
            print(f"Test errors: {result.stderr}")
        return result.returncode == 0, result.stdout, result.stderr
    
    def analyze_failures(self, stderr):
        self.failed_tests.append(stderr)
        
    def run_cycle(self):
        schema = parse_openapi()
        
        for attempt in range(3):
            print(f"\n🔄 Attempt {attempt + 1}")
            
            # Step 1: Generate test cases
            print("📝 Generating test cases...")
            test_cases = self.generate_test_cases(schema)
            print(f"Generated {len(test_cases) if test_cases else 0} test cases")
            
            # Step 2: Generate pytest code
            print("🐍 Generating pytest code...")
            pytest_code = self.generate_pytest_code(test_cases)
            
            with open("test_api.py", "w") as f:
                f.write(pytest_code)
            
            # Step 3: Execute tests
            print("🧪 Executing tests...")
            success, stdout, stderr = self.execute_tests()
            
            if success:
                print("✅ All tests passed!")
                break
            else:
                print(f"❌ Tests failed (attempt {attempt + 1})")
                self.analyze_failures(stderr)

if __name__ == "__main__":
    agent = TestAgent()
    agent.run_cycle()
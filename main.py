import requests

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llama3",
        "prompt": "Generate API test cases in JSON"
    }
)

print(response.json())
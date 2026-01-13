# AI-Generated API Tests

Automated API test generation using LLM and OpenAPI schemas.

## Overview

This project automatically generates pytest test cases from OpenAPI specifications using a local LLM. It creates comprehensive API tests by analyzing schema definitions and generating realistic test data.

## Features

- Parses OpenAPI JSON schemas
- Generates test cases with realistic payloads
- Creates pytest code automatically
- Validates API responses against expected status codes
- Iterative test improvement cycle

## Setup

1. Start your FastAPI server:
```bash
cd MyApi
uvicorn main:app --reload
```

2. Start local LLM (Ollama):
```bash
ollama serve
ollama pull llama3
```

3. Run test generation:
```bash
python test_agent_new.py
```

## Files

- `test_agent_new.py` - Main test generation agent
- `parse_openapi.py` - OpenAPI schema parser with reference resolution
- `openapi.json` - API specification
- `MyApi/main.py` - Sample FastAPI application
- `test_api.py` - Generated test file (auto-created)

## Requirements

- Python 3.8+
- FastAPI
- Ollama with llama3 model
- requests
- pytest
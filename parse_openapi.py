import json

def parse_openapi(file_path="openapi.json"):
    """
    Parse OpenAPI JSON and return a structured schema suitable for AI test generation.
    """
    with open(file_path) as f:
        spec = json.load(f)

    api_schema = []

    paths = spec.get("paths", {})

    for path, methods in paths.items():
        for method, details in methods.items():
            entry = {
                "path": path,
                "method": method.upper(),
                "request_schema": None,
                "responses": list(details.get("responses", {}).keys())
            }

            request_body = details.get("requestBody")
            if request_body:
                content = request_body.get("content", {})
                if "application/json" in content:
                    entry["request_schema"] = content["application/json"].get("schema")

            api_schema.append(entry)

    return api_schema

# # For testing
# if __name__ == "__main__":
#     schema = parse_openapi()
#     print(json.dumps(schema, indent=2))


import json

def analyze_data(data):
    try:
        json.loads(data)
        return "JSON"
    except json.JSONDecodeError:
        pass

    if "password" in data.lower() or "login" in data.lower():
        return "Credentials"
    elif "GET" in data or "POST" in data:
        return "HTTP Request"
    elif any(c.isdigit() for c in data) and ":" in data:
        return "Possible IP Address"
    else:
        return "Unknown"
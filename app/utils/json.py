import re
from fastapi import HTTPException
from pydantic import json


def sanitize_json(raw_str: str) -> dict:
    """
    Sanitize a JSON string by fixing common issues:
    - Remove trailing commas
    - Quote unquoted keys
    - Handle nested objects and special cases
    - Remove function definitions and other non-JSON compliant elements
    """
    # Remove any descriptive text before the JSON object
    raw_str = re.sub(r'^.*?(\{)', r'\1', raw_str, flags=re.DOTALL)

    # Remove function definitions and related properties
    raw_str = re.sub(r':\s*\[Function:[^\]]*\]', ': null', raw_str)
    raw_str = re.sub(r':\s*\[Function[^\]]*\]', ': null', raw_str)
    raw_str = re.sub(r':\s*\[Object \.\.\.\]', ': {}', raw_str)

    # Replace <Buffer > with empty array
    raw_str = re.sub(r'<Buffer\s*>', '[]', raw_str)

    # Handle Uint8Array by converting to a simple array representation
    raw_str = re.sub(r'Uint8Array\(\d+\)\s*\[(.*?)\]', r'[\1]', raw_str)

    # Remove trailing commas in objects and arrays
    raw_str = re.sub(r',\s*}', '}', raw_str)
    raw_str = re.sub(r',\s*\]', ']', raw_str)

    # Quote unquoted keys
    raw_str = re.sub(r'([\{\s,])([a-zA-Z0-9_]+)\s*:', r'\1"\2":', raw_str)

    # Handle special word cases like null, true, false
    raw_str = re.sub(r':\s*null\s*([,}])', r': null\1', raw_str)
    raw_str = re.sub(r':\s*true\s*([,}])', r': true\1', raw_str)
    raw_str = re.sub(r':\s*false\s*([,}])', r': false\1', raw_str)

    # Handle object references like toJSON: [Function: toJSON]
    raw_str = re.sub(r':\s*\[Function: [^\]]*\]', ': null', raw_str)

    try:
        return json.loads(raw_str)
    except json.JSONDecodeError as e:
        # If still failing, try to extract just the first valid JSON object
        try:
            match = re.search(r'\{.*?\}', raw_str, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise HTTPException(status_code=500, detail=f"Error processing JSON: {e}")
        except json.JSONDecodeError as e2:
            raise HTTPException(status_code=500, detail=f"Error processing JSON: {e2}")


def sanitize_json_array(raw_str: str) -> list:
    """
    Extract individual JSON objects from a string and sanitize them.
    Handle complex nested objects with potential "Content" descriptors.
    """
    # First split by obvious object boundaries to handle Content { cases
    segments = re.split(r'(Content \{|\}\n\{)', raw_str)

    # Process each potential JSON object
    result = []
    current_obj = ""

    for segment in segments:
        if segment.strip() == "Content {":
            # Start of a content object description, save previous if any
            if current_obj and "{" in current_obj:
                try:
                    sanitized = sanitize_json(current_obj)
                    result.append(sanitized)
                except:
                    pass  # Skip invalid objects
                current_obj = "{"  # Start new object
        elif segment.strip() == "}\n{" or segment.strip() == "}":
            # End of object, process current and start new
            current_obj += "}"
            try:
                sanitized = sanitize_json(current_obj)
                result.append(sanitized)
            except:
                pass  # Skip invalid objects
            current_obj = "{" if segment.strip() == "}\n{" else ""
        else:
            # Part of current object
            current_obj += segment

    # Process any remaining object
    if current_obj and "{" in current_obj:
        try:
            sanitized = sanitize_json(current_obj)
            result.append(sanitized)
        except:
            pass  # Skip invalid objects

    # If the above approach fails, fall back to basic pattern matching
    if not result:
        objects = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', raw_str, flags=re.DOTALL)
        for obj in objects:
            try:
                sanitized = sanitize_json(obj)
                result.append(sanitized)
            except:
                pass  # Skip invalid objects

    return result

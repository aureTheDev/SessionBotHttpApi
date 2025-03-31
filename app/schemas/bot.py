import os
import json
import re
import subprocess
from typing import Any
from fastapi import HTTPException
from pydantic import field_validator, BaseModel, constr

from schemas.message import Message, SentMessage, PolledMessage


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


current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
session_messenger_utils = os.path.join(project_root, "session-messenger-utils")


class BotBasic(BaseModel):
    name: str
    id: constr(min_length=66, max_length=66)

    @field_validator('id', mode='before')
    def id_must_be_exactly_66_chars(cls, v):
        """
        Validate that the bot ID is exactly 66 characters long.
        """
        if len(v) != 66:
            raise HTTPException(status_code=422, detail="ID must contain exactly 66 characters.")
        return v


class Bot(BotBasic):
    mnemonic: str

    @field_validator('mnemonic', mode='before', check_fields=False)
    def mnemonic_must_be_13_words(cls, v):
        """
        Validate that the mnemonic contains exactly 13 words.
        """
        if len(v.split()) != 13:
            raise HTTPException(status_code=400, detail="Invalid mnemonic length. Must be 13 words.")
        return v

    def send_message(self, message: Message) -> Any:

        ts_file = os.path.join(session_messenger_utils, "send_message.ts")
        cmd = [
            "bun", "run", ts_file,
            self.mnemonic, self.name, message.recipient_id, message.text
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            sanitize_result = sanitize_json(result.stdout)
            return SentMessage(message_hash=sanitize_result["messageHash"], sync_message_hash=sanitize_result["syncMessageHash"], timestamp=sanitize_result["timestamp"])
        except subprocess.CalledProcessError as err:
            return err.stderr

    def poll_messages(self):

        ts_file = os.path.join(session_messenger_utils, "poll_message.ts")
        cmd = ["bun", "run", ts_file, self.mnemonic, self.name]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return sanitize_json_array(result.stdout)
        except subprocess.CalledProcessError as err:
            return err.stderr




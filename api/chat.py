import os
from typing import Any

from flask import Flask, jsonify, request
from openai import AuthenticationError, OpenAI, RateLimitError

app = Flask(__name__)

SYSTEM_PROMPT = """You are a helpful, friendly chatbot. Give clear, accurate answers.
When web search is enabled, use it for current or factual claims that could have changed.
If sources are available, cite them naturally in the response and avoid inventing links.
Never claim to have searched the web when web search was not enabled."""


def extract_sources(response: Any) -> list[dict[str, str]]:
    """Collect unique URL citations from a Responses API result."""
    sources: list[dict[str, str]] = []
    seen: set[str] = set()

    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            for annotation in getattr(content, "annotations", []) or []:
                annotation_type = getattr(annotation, "type", "")
                if annotation_type not in {"url_citation", "url"}:
                    continue
                url = getattr(annotation, "url", "") or ""
                title = getattr(annotation, "title", "") or url
                if url and url not in seen:
                    seen.add(url)
                    sources.append({"title": title, "url": url})
    return sources


@app.post("/api/chat")
def chat():
    if not os.environ.get("OPENAI_API_KEY"):
        return jsonify({"error": "OPENAI_API_KEY is not configured on the server."}), 500

    data = request.get_json(silent=True) or {}
    messages = data.get("messages", [])
    use_web_search = bool(data.get("web_search", False))

    if not isinstance(messages, list) or not messages:
        return jsonify({"error": "Please send at least one message."}), 400

    # Keep only a small, predictable chat history. The browser sends this data.
    clean_messages = []
    for message in messages[-12:]:
        role = message.get("role") if isinstance(message, dict) else None
        content = message.get("content") if isinstance(message, dict) else None
        if role in {"user", "assistant"} and isinstance(content, str) and content.strip():
            clean_messages.append({"role": role, "content": content[:4000]})

    if not clean_messages:
        return jsonify({"error": "No valid messages were provided."}), 400

    tools = [{"type": "web_search"}] if use_web_search else []

    try:
        client = OpenAI()
        response = client.responses.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-5-mini"),
            instructions=SYSTEM_PROMPT,
            input=clean_messages,
            tools=tools,
        )
        return jsonify({
            "reply": response.output_text,
            "sources": extract_sources(response),
        })
    except RateLimitError:
        return jsonify({"error": "OpenAI API credits are unavailable. Add billing credits to this API project, then try again."}), 429
    except AuthenticationError:
        return jsonify({"error": "The server's OpenAI API key was not accepted. Check the key in .env and restart the app."}), 401
    except Exception:
        # Detailed provider errors stay in server logs; users get a safe message.
        app.logger.exception("OpenAI request failed")
        return jsonify({"error": "The chatbot could not answer right now. Check your API key, billing, and model name."}), 502

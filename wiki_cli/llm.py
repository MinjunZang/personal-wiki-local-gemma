"""The only module that talks to the local model runtime (Ollama's HTTP API on localhost).

Gemma never reads files by itself: every call below receives exactly the text
the harness chose to send.
"""
import json
import time
import urllib.error
import urllib.request

from . import config


class LocalModelError(RuntimeError):
    """Raised with a message the CLI can show to the user as-is."""


def _post(path: str, payload: dict, timeout: float = 600) -> dict:
    url = config.OLLAMA_URL + path
    request = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.load(response)
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8", "replace")
        if err.code == 404 and "not found" in body:
            model = payload.get("model", "?")
            raise LocalModelError(
                f"Model '{model}' is not downloaded. While online, run: ollama pull {model}"
            ) from None
        raise LocalModelError(f"Ollama returned HTTP {err.code}: {body[:300]}") from None
    except (urllib.error.URLError, ConnectionError, TimeoutError) as err:
        raise LocalModelError(
            f"Cannot reach the local model server at {config.OLLAMA_URL} ({err}).\n"
            "Start it with:  brew services start ollama   (or run: ollama serve)"
        ) from None


def list_local_models() -> list[str]:
    url = config.OLLAMA_URL + "/api/tags"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return [m["name"] for m in json.load(response)["models"]]
    except (urllib.error.URLError, ConnectionError, TimeoutError) as err:
        raise LocalModelError(
            f"Cannot reach the local model server at {config.OLLAMA_URL} ({err}).\n"
            "Start it with:  brew services start ollama   (or run: ollama serve)"
        ) from None


def ensure_model(model: str) -> None:
    names = list_local_models()
    if model not in names and f"{model}:latest" not in names:
        raise LocalModelError(
            f"Model '{model}' is not downloaded. While online, run: ollama pull {model}"
        )


def chat(messages: list[dict], *, schema: dict | None = None,
         temperature: float = 0.3, model: str | None = None) -> tuple[str, dict]:
    """Send a message list to local Gemma. Returns (reply_text, stats).

    `schema` (a JSON schema) makes Ollama constrain the output to valid JSON.
    Thinking mode is turned off: it made replies ~8x slower in setup tests.
    """
    payload = {
        "model": model or config.CHAT_MODEL,
        "messages": messages,
        "stream": False,
        "think": False,
        "options": {"temperature": temperature, "num_ctx": config.NUM_CTX},
    }
    if schema is not None:
        payload["format"] = schema
    started = time.perf_counter()
    try:
        data = _post("/api/chat", payload)
    except LocalModelError as err:
        # Seen once on this Mac: the runtime timed out while loading the model, and the
        # next attempt loaded in ~7 s. Retry that specific failure one time.
        if "llama-server to start" not in str(err):
            raise
        data = _post("/api/chat", payload)
    stats = {
        "model": payload["model"],
        "seconds": round(time.perf_counter() - started, 2),
        "prompt_tokens": data.get("prompt_eval_count"),
        "output_tokens": data.get("eval_count"),
    }
    return data["message"]["content"], stats


def chat_json(messages: list[dict], schema: dict, **kwargs) -> tuple[dict, dict]:
    text, stats = chat(messages, schema=schema, **kwargs)
    try:
        return json.loads(text), stats
    except json.JSONDecodeError:
        raise LocalModelError(f"Model returned invalid JSON: {text[:300]}") from None


def embed(texts: list[str], batch_size: int = 16) -> list[list[float]]:
    """Embed texts with the local embedding model (no text leaves the machine)."""
    vectors: list[list[float]] = []
    for i in range(0, len(texts), batch_size):
        data = _post("/api/embed", {"model": config.EMBED_MODEL, "input": texts[i:i + batch_size]})
        vectors.extend(data["embeddings"])
    return vectors

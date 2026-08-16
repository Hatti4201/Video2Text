import json
import os
import re

MAX_TRANSCRIPT_CHARS = 60000
HEURISTIC_ID = "heuristic"
HEURISTIC_LABEL = "规则匹配（无需 API Key）"

CODE_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE | re.IGNORECASE)

# Most vendors speak the OpenAI chat-completions protocol, so one client
# (kind="openai" + base_url) covers them instead of a bespoke SDK each.
PROVIDERS = {
    "claude": {
        "label": "Claude (Anthropic)",
        "env": "ANTHROPIC_API_KEY",
        "model": "claude-opus-4-8",
        "kind": "anthropic",
    },
    "gpt": {
        "label": "GPT (OpenAI)",
        "env": "OPENAI_API_KEY",
        "model": "gpt-4o",
        "kind": "openai",
        "base_url": None,
    },
    "gemini": {
        "label": "Gemini (Google)",
        "env": "GOOGLE_API_KEY",
        "model": "gemini-2.0-flash",
        "kind": "openai",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
    },
    "qwen": {
        "label": "通义千问 (Alibaba)",
        "env": "DASHSCOPE_API_KEY",
        "model": "qwen-plus",
        "kind": "openai",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    },
    "deepseek": {
        "label": "DeepSeek",
        "env": "DEEPSEEK_API_KEY",
        "model": "deepseek-chat",
        "kind": "openai",
        "base_url": "https://api.deepseek.com",
    },
    "doubao": {
        "label": "豆包 (ByteDance)",
        "env": "ARK_API_KEY",
        "model": "doubao-seed-1-6",
        "kind": "openai",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
    },
    "moonshot": {
        "label": "Kimi (Moonshot)",
        "env": "MOONSHOT_API_KEY",
        "model": "kimi-k2-0711-preview",
        "kind": "openai",
        "base_url": "https://api.moonshot.cn/v1",
    },
    "zhipu": {
        "label": "智谱 GLM (Zhipu)",
        "env": "ZHIPU_API_KEY",
        "model": "glm-4.6",
        "kind": "openai",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
    },
    "ernie": {
        "label": "文心一言 (Baidu)",
        "env": "BAIDU_API_KEY",
        "model": "ernie-4.5-turbo",
        "kind": "openai",
        "base_url": "https://qianfan.baidubce.com/v2",
    },
    "mistral": {
        "label": "Mistral",
        "env": "MISTRAL_API_KEY",
        "model": "mistral-large-latest",
        "kind": "openai",
        "base_url": "https://api.mistral.ai/v1",
    },
}


def is_configured(provider_id: str) -> bool:
    info = PROVIDERS.get(provider_id)
    return bool(info and os.environ.get(info["env"]))


def list_providers() -> list[dict]:
    providers = [
        {"id": pid, "label": info["label"], "available": is_configured(pid)}
        for pid, info in PROVIDERS.items()
    ]
    providers.append({"id": HEURISTIC_ID, "label": HEURISTIC_LABEL, "available": True})
    return providers


def default_provider() -> str:
    return next((pid for pid in PROVIDERS if is_configured(pid)), HEURISTIC_ID)


def _prompt(title: str, transcript: str) -> str:
    return (
        f'Here is the transcript of a video titled "{title}".\n\n'
        f"Transcript:\n{transcript}\n\n"
        "Write study notes for someone who has not watched the video. "
        "Respond with ONLY a JSON object (no markdown, no code fences) with these keys:\n"
        '- "summary": a clear, well-organized paragraph (3-5 sentences) covering '
        "the main topic and conclusions.\n"
        '- "key_points": 4-6 concise bullet points (array of strings) covering '
        "the most important ideas, facts, or arguments.\n"
        '- "action_items": concrete, actionable steps a viewer could take '
        "(array of strings). Empty array if none."
    )


def _parse_json_notes(text: str) -> dict | None:
    cleaned = CODE_FENCE_RE.sub("", text.strip())
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict) or not data.get("summary"):
        return None
    return {
        "summary": data["summary"],
        "key_points": data.get("key_points") or ["No key points were generated."],
        "action_items": data.get("action_items") or ["No explicit action items found."],
    }


def _call_anthropic(info: dict, title: str, transcript: str) -> dict | None:
    try:
        import anthropic
        from pydantic import BaseModel
    except ImportError:
        return None

    class VideoNotes(BaseModel):
        summary: str
        key_points: list[str]
        action_items: list[str]

    try:
        client = anthropic.Anthropic()
        response = client.messages.parse(
            model=info["model"],
            max_tokens=2000,
            messages=[{"role": "user", "content": _prompt(title, transcript)}],
            output_format=VideoNotes,
        )
        notes = response.parsed_output
        return {
            "summary": notes.summary,
            "key_points": notes.key_points or ["No key points were generated."],
            "action_items": notes.action_items or ["No explicit action items found."],
        }
    except Exception:
        return None


def _call_openai_compatible(info: dict, title: str, transcript: str) -> dict | None:
    try:
        from openai import OpenAI
    except ImportError:
        return None

    try:
        client = OpenAI(api_key=os.environ[info["env"]], base_url=info.get("base_url"))
        response = client.chat.completions.create(
            model=info["model"],
            messages=[{"role": "user", "content": _prompt(title, transcript)}],
            temperature=0.3,
        )
        return _parse_json_notes(response.choices[0].message.content or "")
    except Exception:
        return None


def generate(provider_id: str, title: str, transcript: str) -> dict | None:
    """Ask the given provider for notes. Returns None on any failure so the
    caller can fall back to the heuristic generator."""
    info = PROVIDERS.get(provider_id)
    if not info or not is_configured(provider_id):
        return None

    body = transcript.strip()
    if len(body) > MAX_TRANSCRIPT_CHARS:
        body = body[:MAX_TRANSCRIPT_CHARS] + "\n\n[transcript truncated]"

    if info["kind"] == "anthropic":
        return _call_anthropic(info, title, body)
    return _call_openai_compatible(info, title, body)

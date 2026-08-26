"""One model call, shared by all three agents.

Each agent is really just "a system prompt + a model call". This module is the call.
It has the same two-mode shape as every project in this track:

  REAL mode     `completion()` through LiteLLM -- one function, many providers. Swap
                Gemini for Groq or Claude by changing the model string. Needs a key.

  OFFLINE mode  There's no generic fake here, because a fake *agent* has to behave
                like its role (a Researcher makes bullets, an Editor gives a verdict).
                So the deterministic offline behaviour lives in agents.py, one fake
                per role. This module only handles the REAL path.

Keeping the real call in one place means the three agents differ only in their PROMPT,
not in their plumbing -- which is exactly the point of role-based agents.
"""

from __future__ import annotations

import os

DEFAULT_MODEL = os.environ.get("CONTENT_TEAM_MODEL", "gemini/gemini-1.5-flash")


def call_model(
    system: str, user: str, *, model: str | None = None, temperature: float = 0.7
) -> str:
    """Send a system + user message to a real model via LiteLLM and return the text.

    Imported lazily so offline mode (the default) never needs litellm installed.
    """
    from litellm import completion  # noqa: PLC0415  (lazy on purpose)

    response = completion(
        model=model or DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
    )
    return response.choices[0].message.content or ""

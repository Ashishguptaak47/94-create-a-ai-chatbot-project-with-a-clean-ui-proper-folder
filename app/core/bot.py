import os
import re
import math
from typing import AsyncGenerator, Dict, List
from app.core.memory import ConversationMemory

PERSONAS: Dict[str, Dict[str, str]] = {
    "assistant": {
        "name": "Nova",
        "tagline": "General Intelligence Assistant",
        "system": "I am Nova, a balanced, concise, and helpful AI assistant."
    },
    "coder": {
        "name": "Nexus Code",
        "tagline": "Senior Software Architect",
        "system": "I am Nexus Code. I deliver robust, clean, and production-ready code with explanations."
    },
    "creative": {
        "name": "Aura",
        "tagline": "Creative & Brainstorming Partner",
        "system": "I am Aura, an imaginative writer and divergent thinking collaborator."
    },
    "strategist": {
        "name": "Vanguard",
        "tagline": "Technology & Product Strategist",
        "system": "I am Vanguard. I analyze problems structurally, focusing on trade-offs and scaling."
    }
}

class ChatbotEngine:
    def __init__(self):
        self.memory = ConversationMemory(max_history=10)

    def _evaluate_expression(self, expr: str) -> str | None:
        clean = re.sub(r"[^0-9+\-*/().%^\s]", "", expr)
        if not clean.strip() or not any(char.isdigit() for char in clean):
            return None
        try:
            sanitized = clean.replace("^", "**")
            # Restrict eval context to basic math
            safe_dict = {"__builtins__": None, "math": math, "abs": abs, "round": round}
            result = eval(sanitized, safe_dict, {})
            return f"Result: `{clean.strip()} = {result}`"
        except Exception:
            return None

    def generate_response(self, prompt: str, persona_key: str = "assistant") -> str:
        persona = PERSONAS.get(persona_key, PERSONAS["assistant"])
        prompt_lower = prompt.lower().strip()

        # 1. Direct arithmetic detection
        if any(keyword in prompt_lower for keyword in ["calculate", "compute", "what is"]) or re.match(r"^[0-9+\-*/().\s^]+$", prompt.strip()):
            calc_target = re.sub(r"(?i)(calculate|compute|what is)\s*", "", prompt).rstrip("? ")
            calc_res = self._evaluate_expression(calc_target)
            if calc_res:
                return f"{calc_res}"

        # 2. Persona-specific logic
        if persona_key == "coder":
            if "python" in prompt_lower or "code" in prompt_lower or "function" in prompt_lower:
                return (
                    "Here is an idiomatic solution:\n\n"
                    "```python\n"
                    "from typing import Any, Iterable\n\n"
                    "def process_data(items: Iterable[Any]) -> list[Any]:\n"
                    "    \"\"\"Filters and transforms input stream safely.\"\"\"\n"
                    "    return [item for item in items if item is not None]\n"
                    "```\n\n"
                    "**Key considerations:**\n"
                    "- Type safety using modern Python `3.10+` annotations\n"
                    "- Time complexity: O(N) linear iteration\n"
                    "- Space complexity: O(N) allocation"
                )
            return f"[Nexus Code]: Analyzing '{prompt}'. Provide constraints, stack requirements, or a code snippet to refactor."

        if persona_key == "creative":
            return (
                f"[Aura]: Picture this scenario regarding \"{prompt}\":\n\n"
                "The boundaries blur between conception and reality. Ideas collide like constellations in an indigo sky, "
                "offering an unexpected angle: what if the constraint itself is the centerpiece of the narrative?"
            )

        if persona_key == "strategist":
            return (
                f"### Strategic Assessment: {prompt.title()}\n\n"
                "1. **Core Problem Statement**: Identifying bottlenecks and primary leverage points.\n"
                "2. **Trade-off Matrix**:\n"
                "   - *Velocity vs. Tech Debt*: Ship early or engineer resilience?\n"
                "   - *Cost of Complexity*: Minimize surface area while maintaining agility.\n"
                "3. **Recommendation**: Implement in phases with measurable milestones and automated feedback loops."
            )

        # 3. Conversational greetings and facts
        if prompt_lower in ["hi", "hello", "hey", "greetings"]:
            return f"Hello! I am {persona['name']}, your {persona['tagline']}. How can I assist you today?"
        elif "who are you" in prompt_lower or "your name" in prompt_lower:
            return f"I am {persona['name']}, operating as your {persona['tagline']}. {persona['system']}"
        elif "help" in prompt_lower:
            return (
                "I can help you with:\n"
                "- Writing & debugging code in various languages\n"
                "- Mathematical calculations and problem-solving\n"
                "- Brainstorming, drafting content, and strategic planning\n"
                "- Conversational inquiry across diverse domains"
            )

        return (
            f"Regarding **{prompt}**:\n\n"
            f"{persona['name']} has analyzed your request. Depending on your objective, "
            "we can break this into sequential steps, explore edge cases, or dive deeper into practical implementations. "
            "Let me know which dimension you'd like to explore!"
        )

    async def stream_response(self, session_id: str, prompt: str, persona_key: str = "assistant") -> AsyncGenerator[str, None]:
        self.memory.add_message(session_id, "user", prompt)
        response_text = self.generate_response(prompt, persona_key)
        self.memory.add_message(session_id, "assistant", response_text)

        # Split by words to emulate progressive streaming tokens
        words = response_text.split(" ")
        for i, word in enumerate(words):
            chunk = word if i == len(words) - 1 else word + " "
            yield chunk

import json
from skill_loader import SkillPackage
from llm_client import get_llm_client


class BaseSkillAgent:
    def __init__(self, agent_name: str, skill_dir: str):
        self.agent_name = agent_name
        self.skill = SkillPackage(skill_dir)
        self.llm = get_llm_client()

    def build_prompt(self, model_output: dict, extra_context: dict | None = None) -> str:
        skill_context = self.skill.build_context()
        evidence = json.dumps(model_output, indent=2)

        prompt = f"""
You are an agent in a skill-guided interview coaching system.

{skill_context}

# Candidate Evidence
{evidence}
"""

        if extra_context:
            prompt += f"""

# Other Agent Outputs
{json.dumps(extra_context, indent=2)}
"""

        prompt += """

# Response Style Rules
- Keep the response short and straightforward.
- Use bullet points where possible.
- Avoid long paragraphs.
- Do not repeat the same point.
- Give only the most important feedback.
- Maximum length: around 150–200 words.

# Final Grounding Rules
- Use only the provided evidence.
- Mention specific acoustic points when giving acoustic feedback.
- Do not pretend you listened to the audio.
- Do not make hiring or rejection decisions.
- Keep the feedback focused on interview practice.
- Do not override interpreted acoustic evidence. Use the interpreted evidence as the main acoustic explanation.
"""

        return prompt.strip()

    def run(self, model_output: dict, extra_context: dict | None = None) -> str:
        prompt = self.build_prompt(model_output, extra_context)
        return self.llm.generate(prompt)
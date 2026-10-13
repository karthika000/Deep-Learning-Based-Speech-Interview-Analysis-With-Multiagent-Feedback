from base_agent import BaseSkillAgent

class SupporterAgent(BaseSkillAgent):
    def __init__(self):
        super().__init__(
            agent_name="Supporter Agent",
            skill_dir="skills/supporter_interview_skill"
        )
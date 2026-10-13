from base_agent import BaseSkillAgent

class CriticAgent(BaseSkillAgent):
    def __init__(self):
        super().__init__(
            agent_name="Critic Agent",
            skill_dir="skills/critic_interview_skill"
        )
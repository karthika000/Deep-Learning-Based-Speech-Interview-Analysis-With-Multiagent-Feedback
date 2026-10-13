from base_agent import BaseSkillAgent

class CoachAgent(BaseSkillAgent):
    def __init__(self):
        super().__init__(
            agent_name="Coach Agent",
            skill_dir="skills/coach_interview_skill"
        )
from base_agent import BaseSkillAgent

class JudgeAgent(BaseSkillAgent):
    def __init__(self):
        super().__init__(
            agent_name="Judge Agent",
            skill_dir="skills/judge_interview_skill")
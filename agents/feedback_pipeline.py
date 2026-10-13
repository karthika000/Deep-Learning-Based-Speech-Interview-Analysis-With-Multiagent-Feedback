import json
from pathlib import Path

from schemas import ModelOutput
from acoustic_interpreter import build_interpreted_evidence
from judge_agent import JudgeAgent
from critic_agent import CriticAgent
from supporter_agent import SupporterAgent
from coach_agent import CoachAgent


class FeedbackPipeline:
    def __init__(self):
        self.judge_agent = JudgeAgent()
        self.critic_agent = CriticAgent()
        self.supporter_agent = SupporterAgent()
        self.coach_agent = CoachAgent()

    @staticmethod
    def load_model_output(path):
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Model output file not found: {path}")

        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Validate structure
        ModelOutput(**data)

        return data

    @staticmethod
    def save_result(result, output_path):
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(result, file, indent=2, ensure_ascii=False)

        print(f"Feedback saved to: {output_path}")

    def prepare_agent_input(self, model_output):
        interpreted_evidence = build_interpreted_evidence(model_output)

        enriched_output = {
            **model_output,
            "interpreted_evidence": interpreted_evidence,
            "grounding_note": (
                "Agents did not listen to the audio directly. "
                "All voice-related feedback must be based only on model predictions, "
                "raw acoustic features, and interpreted acoustic evidence."
            )
        }

        return enriched_output

    def run(self, model_output):
        agent_input = self.prepare_agent_input(model_output)

        print("Running Judge Agent...")
        judge_output = self.judge_agent.run(agent_input)

        print("Running Critic Agent...")
        critic_output = self.critic_agent.run(agent_input)

        print("Running Supporter Agent...")
        supporter_output = self.supporter_agent.run(agent_input)

        coach_context = {
            "judge_agent_output": judge_output,
            "critic_agent_output": critic_output,
            "supporter_agent_output": supporter_output
        }

        print("Running Coach Agent...")
        coach_output = self.coach_agent.run(
            model_output=agent_input,
            extra_context=coach_context
        )

        result = {
            "sample_id": model_output.get("sample_id"),
            "question": model_output.get("question"),
            "transcript": model_output.get("transcript"),
            "predictions": model_output.get("predictions"),
            "acoustic_features": model_output.get("acoustic_features"),
            "interpreted_evidence": agent_input.get("interpreted_evidence"),
            "agent_outputs": {
                "judge": judge_output,
                "critic": critic_output,
                "supporter": supporter_output,
                "coach": coach_output
            },
            "final_feedback": coach_output,
            "safety_note": (
                "This feedback is for interview practice only and must not be used "
                "for real hiring decisions or automated candidate selection."
            )
        }

        return result
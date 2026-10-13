from pathlib import Path

from feedback_pipeline import FeedbackPipeline


def main():
    input_path = Path("outputs/agent_inputs/demo_agent_input.json")
    output_path = Path("outputs/feedback_demo_result.json")

    pipeline = FeedbackPipeline()

    model_output = pipeline.load_model_output(input_path)
    result = pipeline.run(model_output)
    pipeline.save_result(result, output_path)

    print("\nFinal Feedback:\n")
    print(result["final_feedback"])


if __name__ == "__main__":
    main()
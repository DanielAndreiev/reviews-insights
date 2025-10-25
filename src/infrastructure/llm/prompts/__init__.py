from pathlib import Path


def load_prompt(prompt_name: str) -> str:
    """Load prompt template from file."""
    prompts_dir = Path(__file__).parent
    prompt_file = prompts_dir / f"{prompt_name}.txt"
    return prompt_file.read_text(encoding="utf-8")
